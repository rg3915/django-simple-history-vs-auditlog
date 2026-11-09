"""Roda linhas Python num console interativo real do Django e imprime como uma sessão (>>> / saída).

Uso: uv run python scripts/sessao_shell.py arquivo_com_linhas.py
"""
import code
import os
import sys

import django

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
os.environ.setdefault("DJANGO_SETTINGS_MODULE", "config.settings")
django.setup()

console = code.InteractiveConsole()
mais = False
for linha in open(sys.argv[1], encoding="utf-8").read().splitlines():
    print(("... " if mais else ">>> ") + linha, flush=True)
    mais = console.push(linha)
if mais:
    console.push("")
