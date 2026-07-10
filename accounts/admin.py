from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from .models import Usuario, Escola  # <-- Adicione a Escola aqui no import

@admin.register(Usuario)
class UsuarioAdmin(UserAdmin):
    model = Usuario
    list_display = ['username', 'email', 'nome', 'tipo', 'escola', 'is_staff']
    list_filter = ['tipo', 'is_staff', 'is_active']
    
    # Adiciona os campos na tela de edição
    fieldsets = UserAdmin.fieldsets + (
        ('Informações da Pesquisa', {'fields': ('tipo', 'escola')}),
    )
    # Adiciona os campos na tela de criação
    add_fieldsets = UserAdmin.add_fieldsets + (
        ('Informações da Pesquisa', {'fields': ('nome', 'email', 'tipo', 'escola')}),
    )

# <-- Adicione este bloco no final do arquivo
@admin.register(Escola)
class EscolaAdmin(admin.ModelAdmin):
    list_display = ('nome', 'cidade')
    search_fields = ('nome',)