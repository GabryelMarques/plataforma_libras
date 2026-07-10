from django.contrib import admin
from .models import Teste, Questao, Alternativa, Tentativa, Resposta

class AlternativaInline(admin.TabularInline):
    model = Alternativa
    extra = 4  # Já abre 4 campos em branco para as opções A, B, C e D

class QuestaoInline(admin.StackedInline):
    model = Questao
    extra = 1

@admin.register(Teste)
class TesteAdmin(admin.ModelAdmin):
    list_display = ('titulo', 'tipo', 'ativo')
    list_filter = ('tipo', 'ativo')
    search_fields = ('titulo',)

@admin.register(Questao)
class QuestaoAdmin(admin.ModelAdmin):
    list_display = ('enunciado', 'teste', 'atividade', 'ordem')
    list_filter = ('teste', 'atividade')
    inlines = [AlternativaInline]

class RespostaInline(admin.TabularInline):
    model = Resposta
    extra = 0
    readonly_fields = ('questao', 'alternativa')
    can_delete = False

@admin.register(Tentativa)
class TentativaAdmin(admin.ModelAdmin):
    list_display = ('usuario', 'teste', 'atividade', 'data_inicio', 'data_fim', 'nota')
    list_filter = ('teste', 'atividade', 'data_inicio')
    search_fields = ('usuario__nome', 'usuario__email')
    inlines = [RespostaInline]
    readonly_fields = ('data_inicio',)