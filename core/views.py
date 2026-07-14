from modulos.models import Modulo
from django.shortcuts import render
from django.contrib.auth.decorators import login_required
from modulos.models import Modulo, Videoaula, ProgressoAula
from django.shortcuts import render, get_object_or_404, redirect
from modulos.models import Videoaula, ProgressoAula



def home(request):
    # Busca todos os módulos no banco, ordenados pelo campo 'ordem'
    modulos = Modulo.objects.all().order_by('ordem')
    
    # Cria um "pacote" (contexto) para enviar ao HTML
    context = {
        'modulos': modulos
    }
    
    return render(request, 'home.html', context)


# O decorador garante que apenas alunos logados acessem esta view
@login_required(login_url='/login/')
def dashboard(request):
    aluno = request.user
    
    # 1. Cálculos de Progresso
    total_aulas = Videoaula.objects.count()
    aulas_concluidas = ProgressoAula.objects.filter(aluno=aluno, concluida=True).count()
    
    progresso_geral = 0
    if total_aulas > 0:
        progresso_geral = int((aulas_concluidas / total_aulas) * 100)
        
    # 2. Descobrir onde ele parou
    # Pega o último registro de acesso desse aluno específico
    ultimo_acesso = ProgressoAula.objects.filter(aluno=aluno).order_by('-ultimo_acesso').first()
    
    # 3. Carregar a Trilha de Aprendizagem
    modulos = Modulo.objects.all().order_by('ordem')
    
    # Empacota tudo para enviar para o HTML
    context = {
        'progresso_geral': progresso_geral,
        'aulas_concluidas': aulas_concluidas,
        'total_aulas': total_aulas,
        'ultimo_acesso': ultimo_acesso,
        'modulos': modulos,
    }
    
    return render(request, 'dashboard.html', context)

@login_required(login_url='/login/')
def detalhe_modulo(request, modulo_id):
    # Busca o módulo clicado ou retorna erro 404 se não existir
    modulo = get_object_or_404(Modulo, id=modulo_id)
    
    # Busca todas as aulas e atividades vinculadas a este módulo
    aulas = modulo.videoaulas.all().order_by('ordem')
    atividades = modulo.atividades.all()
    
    # Busca o progresso do aluno para sabermos quais aulas ele já concluiu
    progressos = ProgressoAula.objects.filter(aluno=request.user, aula__modulo=modulo)
    aulas_concluidas_ids = progressos.filter(concluida=True).values_list('aula_id', flat=True)
    
    context = {
        'modulo': modulo,
        'aulas': aulas,
        'atividades': atividades,
        'aulas_concluidas_ids': aulas_concluidas_ids,
    }
    
    return render(request, 'detalhe_modulo.html', context)


@login_required(login_url='/login/')
def assistir_aula(request, aula_id):
    # Busca a aula específica no banco de dados
    aula = get_object_or_404(Videoaula, id=aula_id)
    
    # Busca o registro de progresso do aluno para essa aula, ou cria um novo se for a primeira vez
    progresso, created = ProgressoAula.objects.get_or_create(
        aluno=request.user,
        aula=aula
    )
    
    # Isso garante que a data de "ultimo_acesso" seja atualizada só por ele abrir a aula
    progresso.save() 
    
    # Se a requisição for POST, significa que ele clicou no botão "Marcar como Concluída"
    if request.method == 'POST':
        progresso.concluida = True
        progresso.save()
        # Após concluir, manda ele de volta para a lista do módulo
        return redirect('detalhe_modulo', modulo_id=aula.modulo.id)
        
    context = {
        'aula': aula,
        'progresso': progresso,
    }
    return render(request, 'assistir_aula.html', context)