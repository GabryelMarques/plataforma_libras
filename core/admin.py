from django.contrib import admin
from .models import TCLE

@admin.register(TCLE)
class TCLEAdmin(admin.ModelAdmin):
    list_display = ('usuario', 'aceitou', 'data_aceite')
    list_filter = ('aceitou', 'data_aceite')
    search_fields = ('usuario__nome', 'usuario__email')

from django.contrib import admin
from .models import ConfiguracaoSite

@admin.register(ConfiguracaoSite)
class ConfiguracaoSiteAdmin(admin.ModelAdmin):
    # Remove o botão de "Adicionar" se já existir 1 configuração criada
    def has_add_permission(self, request):
        if ConfiguracaoSite.objects.exists():
            return False
        return super().has_add_permission(request)