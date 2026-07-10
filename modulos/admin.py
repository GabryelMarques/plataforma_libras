from django.contrib import admin
from .models import Modulo, Videoaula, Atividade

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
    list_display = ('titulo', 'modulo')
    list_filter = ('modulo',)