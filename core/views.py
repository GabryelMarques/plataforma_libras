from django.shortcuts import render
from modulos.models import Modulo

def home(request):
    # Busca todos os módulos no banco, ordenados pelo campo 'ordem'
    modulos = Modulo.objects.all().order_by('ordem')
    
    # Cria um "pacote" (contexto) para enviar ao HTML
    context = {
        'modulos': modulos
    }
    
    return render(request, 'home.html', context)