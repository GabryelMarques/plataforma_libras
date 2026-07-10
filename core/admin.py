from django.contrib import admin
from .models import TCLE

@admin.register(TCLE)
class TCLEAdmin(admin.ModelAdmin):
    list_display = ('usuario', 'aceitou', 'data_aceite')
    list_filter = ('aceitou', 'data_aceite')
    search_fields = ('usuario__nome', 'usuario__email')