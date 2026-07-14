from django.contrib import admin
from .models import Modulo, Videoaula, Atividade, Pergunta, Alternativa, RespostaAluno, ItemAssociacao, RespostaAssociacaoAluno


# Seus inlines originais (mantidos!)
class VideoaulaInline(admin.StackedInline):
    model = Videoaula
    extra = 1

class AtividadeInline(admin.StackedInline):
    model = Atividade
    extra = 1

@admin.register(Modulo)
class ModuloAdmin(admin.ModelAdmin):
    list_display = ('ordem', 'titulo')
    ordering = ('ordem',)
    inlines = [VideoaulaInline, AtividadeInline]

@admin.register(Videoaula)
class VideoaulaAdmin(admin.ModelAdmin):
    list_display = ('ordem', 'titulo', 'modulo', 'duracao')
    list_filter = ('modulo',)
    search_fields = ('titulo',)
    ordering = ('modulo', 'ordem')

@admin.register(Atividade)
class AtividadeAdmin(admin.ModelAdmin):
    list_display = ('titulo', 'tipo', 'modulo')
    list_filter = ('modulo', 'tipo')


class AlternativaInline(admin.TabularInline):
    model = Alternativa
    extra = 4

class ItemAssociacaoInline(admin.TabularInline):
    model = ItemAssociacao
    extra = 4 # Deixa 4 linhas prontas pra ligar (A->B)

@admin.register(Pergunta)
class PerguntaAdmin(admin.ModelAdmin):
    list_display = ('enunciado', 'tipo_pergunta', 'atividade', 'ordem')
    list_filter = ('atividade', 'tipo_pergunta')
    # O Django é inteligente: mostra as duas opções de cadastro na mesma tela
    inlines = [AlternativaInline, ItemAssociacaoInline] 

@admin.register(RespostaAssociacaoAluno)
class RespostaAssociacaoAlunoAdmin(admin.ModelAdmin):
    list_display = ('aluno', 'item_a', 'resposta_aluno_coluna_b', 'data_resposta')