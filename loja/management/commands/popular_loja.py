"""Popula a loja: categorias, 30 livros brasileiros, 3 usuários e 3 clientes."""
from datetime import date
from decimal import Decimal

from auditlog.context import set_actor
from django.contrib.auth import get_user_model
from django.core.management.base import BaseCommand
from django.db import transaction

from loja.models import Categoria, Cliente, Livro

# (título, autor, ano da 1ª edição, categoria, preço, estoque)
# Obs.: só o ano é real; a data fica em 1º de janeiro do ano.
LIVROS = [
    ("Dom Casmurro", "Machado de Assis", 1899, "Romance", "39.90", 12),
    ("Memórias Póstumas de Brás Cubas", "Machado de Assis", 1881, "Romance", "42.50", 9),
    ("Quincas Borba", "Machado de Assis", 1891, "Romance", "37.00", 5),
    ("A Hora da Estrela", "Clarice Lispector", 1977, "Romance", "54.90", 14),
    ("Perto do Coração Selvagem", "Clarice Lispector", 1943, "Romance", "59.90", 6),
    ("A Paixão Segundo G.H.", "Clarice Lispector", 1964, "Romance", "62.00", 4),
    ("Laços de Família", "Clarice Lispector", 1960, "Contos", "49.90", 8),
    ("Vidas Secas", "Graciliano Ramos", 1938, "Romance", "44.90", 20),
    ("São Bernardo", "Graciliano Ramos", 1934, "Romance", "46.00", 7),
    ("Angústia", "Graciliano Ramos", 1936, "Romance", "51.90", 3),
    ("Capitães da Areia", "Jorge Amado", 1937, "Romance", "57.90", 18),
    ("Gabriela, Cravo e Canela", "Jorge Amado", 1958, "Romance", "74.90", 10),
    ("Dona Flor e Seus Dois Maridos", "Jorge Amado", 1966, "Romance", "79.90", 6),
    ("O Cortiço", "Aluísio Azevedo", 1890, "Romance", "29.90", 25),
    ("Iracema", "José de Alencar", 1865, "Romance", "27.90", 15),
    ("O Guarani", "José de Alencar", 1857, "Romance", "34.90", 9),
    ("Grande Sertão: Veredas", "João Guimarães Rosa", 1956, "Romance", "89.90", 5),
    ("Sagarana", "João Guimarães Rosa", 1946, "Contos", "64.90", 7),
    ("Macunaíma", "Mário de Andrade", 1928, "Romance", "39.00", 11),
    ("Triste Fim de Policarpo Quaresma", "Lima Barreto", 1915, "Romance", "32.90", 13),
    ("O Quinze", "Rachel de Queiroz", 1930, "Romance", "41.90", 8),
    ("Menino de Engenho", "José Lins do Rego", 1932, "Romance", "45.90", 4),
    ("Incidente em Antares", "Erico Verissimo", 1971, "Romance", "69.90", 6),
    ("Lavoura Arcaica", "Raduan Nassar", 1975, "Romance", "58.90", 9),
    ("Alguma Poesia", "Carlos Drummond de Andrade", 1930, "Poesia", "48.90", 10),
    ("A Rosa do Povo", "Carlos Drummond de Andrade", 1945, "Poesia", "55.90", 7),
    ("Morte e Vida Severina", "João Cabral de Melo Neto", 1955, "Poesia", "36.90", 16),
    ("Libertinagem", "Manuel Bandeira", 1930, "Poesia", "43.90", 5),
    ("Os Sertões", "Euclides da Cunha", 1902, "Ensaio", "84.90", 4),
    ("Casa-Grande & Senzala", "Gilberto Freyre", 1933, "Ensaio", "99.90", 3),
]

SLUGS = {"Romance": "romance", "Contos": "contos", "Poesia": "poesia", "Ensaio": "ensaio"}

# Dados fictícios (CPFs gerados só para a demonstração)
CLIENTES = [
    ("Maria Oliveira", "maria@exemplo.com", "123.456.789-09"),
    ("João Pereira", "joao@exemplo.com", "987.654.321-00"),
    ("Carla Souza", "carla@exemplo.com", "111.444.777-35"),
]


class Command(BaseCommand):
    help = "Popula a loja com dados de exemplo"

    @transaction.atomic
    def handle(self, *args, **opts):
        User = get_user_model()
        senhas = {"regis": "regis123", "ana": "senha123", "bruno": "senha123"}
        usuarios = {}
        for nome, senha in senhas.items():
            u, _ = User.objects.get_or_create(
                username=nome,
                defaults={"email": f"{nome}@livraria.dev", "is_staff": True, "is_superuser": True},
            )
            u.set_password(senha)
            u.save()
            usuarios[nome] = u
        regis = usuarios["regis"]

        cats = {}
        for nome, slug in SLUGS.items():
            cats[nome], _ = Categoria.objects.get_or_create(nome=nome, slug=slug)

        with set_actor(regis):  # auditlog: actor fora de um request
            if not Livro.objects.exists():
                for titulo, autor, ano, cat, preco, estoque in LIVROS:
                    livro = Livro(
                        titulo=titulo, autor=autor, publicado_em=date(ano, 1, 1),
                        categoria=cats[cat], preco=Decimal(preco), estoque=estoque,
                    )
                    livro._history_user = regis  # simple-history: usuário fora de um request
                    livro._change_reason = "Cadastro inicial"
                    livro.save()
            if not Cliente.objects.exists():
                for nome, email, cpf in CLIENTES:
                    Cliente.objects.create(nome=nome, email=email, cpf=cpf)

        self.stdout.write(self.style.SUCCESS(
            f"{Livro.objects.count()} livros, {Cliente.objects.count()} clientes, "
            f"{User.objects.count()} usuários"
        ))
