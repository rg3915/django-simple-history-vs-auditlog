"""Experimento de espaço: 1 livro com descrição de ~2 KB, depois 1000 updates mudando SÓ o preço.

Roda num banco separado (experimento.sqlite3) para não sujar o banco das capturas:
    DATABASE_URL=sqlite:///experimento.sqlite3 uv run python scripts/experimento_tamanho.py
"""
import os
import sys
import time
from datetime import date
from decimal import Decimal

import django

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
os.environ.setdefault("DJANGO_SETTINGS_MODULE", "config.settings")
django.setup()

from auditlog.context import set_actor  # noqa: E402
from django.contrib.auth.models import User  # noqa: E402

from loja.models import Categoria, Livro  # noqa: E402

PARAGRAFO = (
    "Bento Santiago, o Bentinho, já velho e solitário, decide escrever suas memórias para "
    "atar as duas pontas da vida. Relembra a infância na Rua de Matacavalos, a promessa da "
    "mãe de fazê-lo padre, o seminário e o amor por Capitu, a menina de olhos de ressaca. "
)
DESCRICAO = (PARAGRAFO * 20)[:2048]
UPDATES = 1000

regis = User.objects.get(username="regis")
with set_actor(regis):
    livro = Livro(
        titulo="Dom Casmurro (edição de teste)", autor="Machado de Assis",
        categoria=Categoria.objects.get(slug="romance"), publicado_em=date(1899, 1, 1),
        preco=Decimal("10.00"), estoque=1, descricao=DESCRICAO,
    )
    livro._history_user = regis
    livro.save()
    print(f"livro #{livro.pk} criado; descrição com {len(DESCRICAO.encode())} bytes (UTF-8)")

    inicio = time.perf_counter()
    for i in range(1, UPDATES + 1):
        livro.preco = Decimal("10.00") + Decimal(i) / 100  # muda SÓ o preço
        livro._history_user = regis
        livro.save()
    print(f"{UPDATES} updates de preço em {time.perf_counter() - inicio:.1f} s")

print("linhas em loja_historicallivro deste livro:", livro.history.count())
from auditlog.models import LogEntry  # noqa: E402

print("linhas em auditlog_logentry deste livro:", LogEntry.objects.get_for_object(livro).count())
print("último LogEntry.changes:", LogEntry.objects.get_for_object(livro).first().changes)
