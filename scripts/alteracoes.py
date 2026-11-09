"""Faz alterações REAIS pelo admin (requests logados) para gerar histórico nos dois pacotes.

regis e bruno acessam por 127.0.0.1; ana acessa pelo IP da rede local (192.168.18.172),
então o REMOTE_ADDR gravado pelo auditlog é diferente de verdade.
"""
import re
import sys
import time
from html.parser import HTMLParser

import requests

LOCAL = "http://127.0.0.1:8020"
REDE = "http://192.168.18.172:8020"
USUARIOS = {
    "regis": ("regis123", LOCAL),
    "ana": ("senha123", REDE),
    "bruno": ("senha123", LOCAL),
}


class Formulario(HTMLParser):
    """Lê os valores atuais de input/select/textarea do change form do admin."""

    def __init__(self):
        super().__init__()
        self.dados, self._textarea, self._select = {}, None, None

    def handle_starttag(self, tag, attrs):
        a = dict(attrs)
        if tag == "input" and a.get("name") and a.get("type") not in ("submit", "checkbox"):
            self.dados[a["name"]] = a.get("value", "")
        elif tag == "textarea":
            self._textarea = a["name"]
            self.dados[a["name"]] = ""
        elif tag == "select":
            self._select = a["name"]
        elif tag == "option" and self._select and "selected" in a:
            self.dados[self._select] = a.get("value", "")

    def handle_endtag(self, tag):
        if tag == "textarea":
            self._textarea = None
        elif tag == "select":
            self._select = None

    def handle_data(self, data):
        if self._textarea:
            self.dados[self._textarea] += data


def sessao(usuario):
    senha, base = USUARIOS[usuario]
    s = requests.Session()
    s.base = base
    r = s.get(f"{base}/admin/login/")
    token = re.search(r'name="csrfmiddlewaretoken" value="([^"]+)"', r.text).group(1)
    r = s.post(f"{base}/admin/login/?next=/admin/", data={
        "csrfmiddlewaretoken": token, "username": usuario, "password": senha, "next": "/admin/",
    }, headers={"Referer": f"{base}/admin/login/"})
    assert "logout" in r.text.lower(), f"login falhou para {usuario}"
    return s


def alterar(usuario, modelo, pk, **mudancas):
    s = sessao(usuario)
    url = f"{s.base}/admin/loja/{modelo}/{pk}/change/"
    f = Formulario()
    f.feed(s.get(url).text)
    dados = {k: v for k, v in f.dados.items() if not k.startswith("_")}
    dados.update({k: str(v) for k, v in mudancas.items()})
    dados["_save"] = "Salvar"
    r = s.post(url, data=dados, headers={"Referer": url})
    ok = r.status_code == 200 and "errornote" not in r.text
    print(f"{usuario:6} ({s.base}) {modelo} #{pk}: {mudancas} -> {'OK' if ok else 'ERRO'}")
    if not ok:
        sys.exit(r.text[:3000])


def visualizar(usuario, pk):
    s = sessao(usuario)
    r = s.get(f"{s.base}/clientes/{pk}/")
    print(f"{usuario:6} ({s.base}) visualizou /clientes/{pk}/ -> HTTP {r.status_code}")


if __name__ == "__main__":
    PAUSA = 3  # segundos entre as versões, para os horários ficarem distintos
    alterar("regis", "livro", 1, preco="44.90")
    time.sleep(PAUSA)
    alterar("ana", "livro", 1, estoque=8)
    time.sleep(PAUSA)
    alterar("bruno", "livro", 1, preco="42.00", estoque=15)
    time.sleep(PAUSA)
    alterar("ana", "livro", 1, descricao="Bentinho narra a vida e o ciúme de Capitu.")
    time.sleep(PAUSA)
    alterar("regis", "livro", 1, preco="49.90", estoque=10)
    time.sleep(PAUSA)
    alterar("ana", "cliente", 1, email="maria.oliveira@exemplo.com", cpf="529.982.247-25")
    time.sleep(PAUSA)
    visualizar("bruno", 1)
    visualizar("ana", 1)
