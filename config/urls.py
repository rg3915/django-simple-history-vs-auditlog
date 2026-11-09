from django.contrib import admin
from django.urls import path
from django.views.generic import RedirectView

from loja.views import ClienteDetailView

urlpatterns = [
    path("", RedirectView.as_view(url="/admin/")),
    path("admin/", admin.site.urls),
    path("clientes/<int:pk>/", ClienteDetailView.as_view(), name="cliente_detalhe"),
]
