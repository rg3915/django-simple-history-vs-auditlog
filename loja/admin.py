import json

from auditlog.admin import LogEntryAdmin
from auditlog.mixins import AuditlogHistoryAdminMixin
from auditlog.models import LogEntry
from django.contrib import admin
from django.utils.html import format_html
from simple_history.admin import SimpleHistoryAdmin

from .models import Categoria, Cliente, Livro


@admin.register(Categoria)
class CategoriaAdmin(admin.ModelAdmin):
    list_display = ["nome", "slug"]
    prepopulated_fields = {"slug": ["nome"]}


@admin.register(Livro)
class LivroAdmin(AuditlogHistoryAdminMixin, SimpleHistoryAdmin):
    list_display = ["titulo", "autor", "categoria", "preco", "estoque"]
    search_fields = ["titulo", "autor"]
    history_list_display = ["preco", "estoque"]  # colunas extras no histórico
    show_auditlog_history_link = True  # coluna "Audit log" na lista


@admin.register(Cliente)
class ClienteAdmin(admin.ModelAdmin):
    list_display = ["nome", "email", "cpf"]


# Admin do auditlog com o IP (remote_addr) na lista e o JSON cru no detalhe
admin.site.unregister(LogEntry)


@admin.register(LogEntry)
class LogEntryComIPAdmin(LogEntryAdmin):
    list_display = ["created", "resource_url", "action", "msg_short", "user_url", "remote_addr"]
    readonly_fields = [*LogEntryAdmin.readonly_fields, "remote_addr", "changes_json"]
    fieldsets = [
        (None, {"fields": ["created", "user_url", "remote_addr", "resource_url"]}),
        ("Mudanças", {"fields": ["action", "msg", "changes_json"]}),
    ]

    @admin.display(description="changes (JSON gravado)")
    def changes_json(self, obj):
        linhas = [
            f"  {json.dumps(campo)}: {json.dumps(valores, ensure_ascii=False)}"
            for campo, valores in (obj.changes or {}).items()
        ]
        texto = "{\n" + ",\n".join(linhas) + "\n}"
        return format_html('<pre style="margin:0">{}</pre>', texto)
