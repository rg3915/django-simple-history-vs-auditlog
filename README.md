# django-simple-history × django-auditlog

Projeto Django **real** usado no vídeo "Simple History × Auditlog: qual usar?" do canal
[Regis do Python](https://www.youtube.com/@RegisdoPython). Os dois pacotes rodam no mesmo modelo
(`Livro`) para comparar o que cada um guarda, e um script mede o espaço que cada um ocupa no banco.
As capturas usam o **admin padrão do Django em modo escuro**.

Versões: Django 6.1.1 · django-simple-history 3.13.0 · django-auditlog 3.4.1 · Python 3.14.

## O que cada pacote rastreia

| Modelo | simple-history | auditlog |
|---|---|---|
| `Livro` | `history = HistoricalRecords()` → tabela `loja_historicallivro` (linha inteira por versão) | `auditlog.register(Livro)` → `auditlog_logentry` (só o diff) |
| `Cliente` | — | `auditlog.register(Cliente, mask_fields=["cpf"])` (CPF mascarado no log) |

- `ClienteDetailView` (`/clientes/<pk>/`) usa `LogAccessMixin`: cada visualização vira um
  `LogEntry` com `action=3` (access).
- Middlewares: `HistoryRequestMiddleware` (preenche `history_user`) e `AuditlogMiddleware`
  (preenche `actor`, `remote_addr`, `cid`).
- No admin, `LivroAdmin` herda de `SimpleHistoryAdmin` (botão Histórico/Reverter) **e** de
  `AuditlogHistoryAdminMixin` (página `/admin/loja/livro/<pk>/auditlog/`). O admin do
  `LogEntry` foi estendido para mostrar o `remote_addr` na lista e o JSON cru de `changes`.

## Como rodar

```bash
cp .env.example .env            # ajuste a SECRET_KEY
uv sync
uv run python manage.py migrate
uv run python manage.py popular_loja      # 30 livros, 3 clientes, usuários regis/ana/bruno
uv run python manage.py runserver 0.0.0.0:8000
```

Usuários: `regis / regis123`, `ana / senha123`, `bruno / senha123` (todos superusuários).

## Scripts das capturas (`scripts/`)

| Script | O que faz |
|---|---|
| `alteracoes.py` | Faz login no admin com `requests` e altera o Dom Casmurro e a cliente Maria (regis e bruno por `127.0.0.1`, ana pelo IP da rede `192.168.18.172`, então o `remote_addr` muda de verdade). Também visita `/clientes/1/` (registro de acesso). |
| `capturas.py` | Playwright/Chromium, 1600×1000, DPR 2, tema escuro. Gera os PNGs em `../captura/`. |
| `sessao_shell.py` | Roda linhas Python num console interativo do Django e imprime como sessão `>>>` (usado no `sh_asof.txt`). |
| `experimento_tamanho.py` | 1 livro com descrição de ~2 KB + 1000 updates mudando só o preço (rodar com `DATABASE_URL=sqlite:///experimento.sqlite3`). |

Os scripts gravam os resultados na pasta `../captura/` (fora deste repositório).

## Como repetir o experimento de espaço

O experimento usa um banco separado, para não misturar com os dados do admin:

```bash
export DATABASE_URL=sqlite:///experimento.sqlite3
uv run python manage.py migrate
uv run python manage.py popular_loja
uv run python scripts/experimento_tamanho.py
unset DATABASE_URL
```

## Resultado do experimento de espaço (SQLite, dbstat)

| | linhas | tabela | tabela + índices |
|---|---|---|---|
| `loja_historicallivro` (simple-history) | 1001 | 4.112.384 B | 4.190.208 B |
| `auditlog_logentry` (auditlog) | 1001 | 159.744 B | 282.624 B |

## Observações reais encontradas

- `AUDITLOG_MASK_TRACKING_FIELDS` (máscara global) só funciona com
  `AUDITLOG_INCLUDE_ALL_MODELS=True`; aqui foi usado `mask_fields` no `register`.
- No `create`, o auditlog 3.4.1 grava o valor antigo `None` como a string `"None"`, e a máscara
  transforma isso em `"**ne"`.
- O admin padrão do `LogEntry` não mostra o IP; foi preciso estender o admin (`loja/admin.py`).
- O simple-history não grava IP; só o usuário (`history_user`).
