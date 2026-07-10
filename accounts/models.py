from django.contrib.auth.models import AbstractUser
from django.db import models

# 1. Criamos a tabela Escola
class Escola(models.Model):
    nome = models.CharField(max_length=255, verbose_name="Nome da Instituição")
    cidade = models.CharField(max_length=100, blank=True, null=True, verbose_name="Cidade")

    def __str__(self):
        return self.nome

# 2. Atualizamos o Usuário
class Usuario(AbstractUser):
    TIPO_CHOICES = (
        ('ESTUDANTE', 'Estudante'),
        ('ADMIN', 'Administrador'),
    )

    nome = models.CharField(max_length=255, verbose_name="Nome Completo")
    email = models.EmailField(unique=True, verbose_name="E-mail")
    
    # Mudamos de CharField para ForeignKey conectando com a Escola
    escola = models.ForeignKey(Escola, on_delete=models.SET_NULL, null=True, blank=True, verbose_name="Escola", related_name="alunos")
    
    tipo = models.CharField(max_length=15, choices=TIPO_CHOICES, default='ESTUDANTE', verbose_name="Tipo de Usuário")

    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS = ['username', 'nome']

    def __str__(self):
        return self.nome if self.nome else self.email