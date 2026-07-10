from django.db import models

# Create your models here.
from django.db import models
from django.conf import settings
from modulos.models import Atividade

class Teste(models.Model):
    TIPO_CHOICES = (
        ('PRE', 'Pré-teste'),
        ('POS', 'Pós-teste'),
    )
    titulo = models.CharField(max_length=255, verbose_name="Título")
    tipo = models.CharField(max_length=3, choices=TIPO_CHOICES, verbose_name="Tipo (Pré ou Pós)")
    descricao = models.TextField(blank=True, null=True, verbose_name="Descrição")
    ativo = models.BooleanField(default=True, verbose_name="Ativo")

    def __str__(self):
        return f"{self.get_tipo_display()} - {self.titulo}"

class Questao(models.Model):
    enunciado = models.TextField(verbose_name="Enunciado")
    ordem = models.IntegerField(default=1, verbose_name="Ordem")
    
    # Uma questão pode pertencer a um Teste ou a uma Atividade (opcionais)
    teste = models.ForeignKey(Teste, on_delete=models.CASCADE, related_name='questoes', blank=True, null=True)
    atividade = models.ForeignKey(Atividade, on_delete=models.CASCADE, related_name='questoes', blank=True, null=True)

    def __str__(self):
        return f"Questão {self.ordem}: {self.enunciado[:50]}..."

class Alternativa(models.Model):
    questao = models.ForeignKey(Questao, on_delete=models.CASCADE, related_name='alternativas')
    descricao = models.TextField(verbose_name="Descrição da Alternativa")
    correta = models.BooleanField(default=False, verbose_name="É a resposta correta?")

    def __str__(self):
        return f"{'[Correta]' if self.correta else '[Errada]'} {self.descricao[:50]}"

class Tentativa(models.Model):
    usuario = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='tentativas')
    
    # Pode ser a tentativa de um teste formal ou de uma atividade de fixação
    teste = models.ForeignKey(Teste, on_delete=models.CASCADE, blank=True, null=True)
    atividade = models.ForeignKey(Atividade, on_delete=models.CASCADE, blank=True, null=True)
    
    data_inicio = models.DateTimeField(auto_now_add=True, verbose_name="Data de Início")
    data_fim = models.DateTimeField(blank=True, null=True, verbose_name="Data de Fim")
    nota = models.FloatField(blank=True, null=True, verbose_name="Nota Final")

    def __str__(self):
        alvo = self.teste.titulo if self.teste else self.atividade.titulo
        return f"Tentativa de {self.usuario.nome} em {alvo}"

class Resposta(models.Model):
    tentativa = models.ForeignKey(Tentativa, on_delete=models.CASCADE, related_name='respostas')
    questao = models.ForeignKey(Questao, on_delete=models.CASCADE)
    alternativa = models.ForeignKey(Alternativa, on_delete=models.CASCADE)

    def __str__(self):
        return f"Resposta de {self.tentativa.usuario.nome} - Questão {self.questao.id}"