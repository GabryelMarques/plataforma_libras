from django.contrib import admin
# Importa o TCLEAceite lá do app accounts
from accounts.models import TCLEAceite 
# Importa a Configuração Global do próprio app
from .models import ConfiguracaoSite

@admin.register(TCLEAceite)
class TCLEAceiteAdmin(admin.ModelAdmin):
    # Ajustado para 'aceito' e incluído o 'ip_aceite' para auditoria ética
    list_display = ('usuario', 'aceito', 'data_aceite', 'ip_aceite')
    list_filter = ('aceito', 'data_aceite')
    search_fields = ('usuario__nome', 'usuario__email')

@admin.register(ConfiguracaoSite)
class ConfiguracaoSiteAdmin(admin.ModelAdmin):
    # Remove o botão de "Adicionar" se já existir 1 configuração criada
    def has_add_permission(self, request):
        if ConfiguracaoSite.objects.exists():
            return False
        return super().has_add_permission(request)