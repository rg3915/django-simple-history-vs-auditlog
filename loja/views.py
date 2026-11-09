from auditlog.mixins import LogAccessMixin
from django.contrib.auth.mixins import LoginRequiredMixin
from django.views.generic import DetailView

from .models import Cliente


class ClienteDetailView(LoginRequiredMixin, LogAccessMixin, DetailView):
    """Cada visualização vira um LogEntry com action=ACCESS."""

    model = Cliente
