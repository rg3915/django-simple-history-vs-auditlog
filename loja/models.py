from auditlog.registry import auditlog
from django.db import models
from simple_history.models import HistoricalRecords


class Categoria(models.Model):
    nome = models.CharField(max_length=60, unique=True)
    slug = models.SlugField(unique=True)

    class Meta:
        ordering = ["nome"]
        verbose_name_plural = "categorias"

    def __str__(self):
        return self.nome


class Livro(models.Model):
    titulo = models.CharField("título", max_length=200)
    autor = models.CharField(max_length=120)
    preco = models.DecimalField("preço", max_digits=8, decimal_places=2)
    categoria = models.ForeignKey(Categoria, on_delete=models.PROTECT, related_name="livros")
    publicado_em = models.DateField("publicado em")
    estoque = models.PositiveIntegerField(default=0)
    descricao = models.TextField("descrição", blank=True)

    history = HistoricalRecords()  # simple-history: cópia da linha inteira

    class Meta:
        ordering = ["titulo"]

    def __str__(self):
        return f"{self.titulo} ({self.autor})"


class Cliente(models.Model):
    nome = models.CharField(max_length=120)
    email = models.EmailField()
    cpf = models.CharField("CPF", max_length=14)

    class Meta:
        ordering = ["nome"]

    def __str__(self):
        return self.nome


# auditlog: só o diff (campo: [antigo, novo]) numa tabela única
auditlog.register(Livro)
auditlog.register(Cliente, mask_fields=["cpf"])
