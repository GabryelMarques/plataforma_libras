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
    list_display = ('ordem', 'titulo', 'is_active')
    list_filter = ('is_active',)
    ordering = ('ordem',)
    inlines = [VideoaulaInline, AtividadeInline]

    def get_queryset(self, request):
        return super().get_queryset(request).filter(is_active=True)

@admin.register(Videoaula)
class VideoaulaAdmin(admin.ModelAdmin):
    list_display = ('ordem', 'titulo', 'modulo', 'duracao', 'is_active')
    list_filter = ('modulo', 'is_active')
    search_fields = ('titulo',)
    ordering = ('modulo', 'ordem')

    def get_queryset(self, request):
        return super().get_queryset(request).filter(is_active=True)

@admin.register(Atividade)
class AtividadeAdmin(admin.ModelAdmin):
    list_display = ('titulo', 'tipo', 'modulo', 'is_active')
    list_filter = ('modulo', 'tipo', 'is_active')

    def get_queryset(self, request):
        return super().get_queryset(request).filter(is_active=True)


class AlternativaInline(admin.TabularInline):
    model = Alternativa
    extra = 4

class ItemAssociacaoInline(admin.TabularInline):
    model = ItemAssociacao
    extra = 4 # Deixa 4 linhas prontas pra ligar (A->B)

@admin.register(Pergunta)
class PerguntaAdmin(admin.ModelAdmin):
    list_display = ('enunciado', 'tipo_pergunta', 'atividade', 'ordem', 'is_active')
    list_filter = ('atividade', 'tipo_pergunta', 'is_active')
    def get_queryset(self, request):
        return super().get_queryset(request).filter(is_active=True)
    # O Django é inteligente: mostra as duas opções de cadastro na mesma tela
    inlines = [AlternativaInline, ItemAssociacaoInline] 

@admin.register(RespostaAssociacaoAluno)
class RespostaAssociacaoAlunoAdmin(admin.ModelAdmin):
    list_display = ('aluno', 'item_a', 'resposta_aluno_coluna_b', 'data_resposta')