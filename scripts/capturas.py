"""Capturas do admin padrão do Django (tema escuro) com Playwright/Chromium, 1600x1000, DPR 2."""
import sys
from pathlib import Path

from playwright.sync_api import sync_playwright

BASE = "http://127.0.0.1:8000"
SAIDA = Path(__file__).resolve().parents[2] / "captura"

# (arquivo, url, seletor para esperar, captura de página inteira?)
PAGINAS = {
    "sh_lista.png": ("/admin/loja/livro/1/history/", "#change-history", False),
    "sh_reverter.png": ("/admin/loja/livro/1/history/32/", "input[name=_save]", False),
    "al_lista.png": ("/admin/auditlog/logentry/?q=Dom+Casmurro", "#result_list", False),
    "al_detalhe.png": ("/admin/auditlog/logentry/36/change/", "#content", False),
    "al_cpf.png": ("/admin/auditlog/logentry/39/change/", "#content", False),
    "al_acesso.png": ("/admin/auditlog/logentry/?action__exact=3", "#result_list", False),
    "al_historico_livro.png": ("/admin/loja/livro/1/auditlog/", "#content", False),
}


def main(nomes):
    with sync_playwright() as p:
        browser = p.chromium.launch()
        ctx = browser.new_context(
            viewport={"width": 1600, "height": 1000},
            device_scale_factor=2,
            color_scheme="dark",
            locale="pt-BR",
        )
        page = ctx.new_page()
        page.goto(f"{BASE}/admin/login/")
        page.fill("input[name=username]", "regis")
        page.fill("input[name=password]", "regis123")
        page.click("[type=submit]")
        page.wait_for_load_state("networkidle")
        for nome, (url, seletor, inteira) in PAGINAS.items():
            if nomes and nome not in nomes:
                continue
            page.goto(BASE + url)
            page.wait_for_selector(seletor)
            page.screenshot(path=str(SAIDA / nome), full_page=inteira)
            print("salvo", SAIDA / nome)
        browser.close()


if __name__ == "__main__":
    main(sys.argv[1:])
