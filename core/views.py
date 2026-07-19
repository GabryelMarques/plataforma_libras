# ==========================================
# 1. IMPORTS PADRONIZADOS E ORGANIZADOS
# ==========================================
import random
import csv
from datetime import timedelta
from functools import wraps

from django.db.models import Q
from django.http import HttpResponse, JsonResponse
from django.shortcuts import render, get_object_or_404, redirect
from django.contrib.auth.decorators import login_required
from django.contrib.admin.views.decorators import staff_member_required
from django.contrib import messages
from django.utils import timezone
from django.urls import reverse

# Imports dos seus Apps
from modulos.models import (
    Modulo, Videoaula, ProgressoAula, Atividade, 
    Pergunta, Alternativa, RespostaAluno, 
    RespostaAssociacaoAluno, ItemAssociacao
)
from accounts.models import Escola, Usuario, TCLEAceite
from .models import ConfiguracaoSite

# ==========================================
# 2. DECORADORES E FUNÇÕES GERAIS
# ==========================================

def get_client_ip(request):
    x_forwarded_for = request.META.get('HTTP_X_FORWARDED_FOR')
    if x_forwarded_for:
        return x_forwarded_for.split(',')[0]
    return request.META.get('REMOTE_ADDR')

def tcle_required(view_func):
    """Guardião Ético: Impede acesso sem aceite do TCLE"""
    @wraps(view_func)
    def _wrapped_view(request, *args, **kwargs):
        if request.user.is_authenticated and not request.user.is_staff:
            if not TCLEAceite.objects.filter(usuario=request.user, aceito=True).exists():
                return redirect('tcle_aceite')
        return view_func(request, *args, **kwargs)
    return _wrapped_view

# ==========================================
# 3. VIEWS PÚBLICAS E ÁREA DO ALUNO
# ==========================================

def home(request):
    config_site = ConfiguracaoSite.objects.first()
    # prefetch_related otimiza a contagem no HTML
    modulos = Modulo.objects.prefetch_related('videoaulas', 'atividades').order_by('ordem')
    
    context = {
        'modulos': modulos,
        'config_site': config_site,
    }
    return render(request, 'home.html', context)

@login_required
def tcle_aceite(request):
    if request.method == 'POST':
        TCLEAceite.objects.create(
            usuario=request.user,
            aceito=True,
            ip_aceite=get_client_ip(request)
        )
        return redirect('dashboard')
    return render(request, 'tcle.html')

@login_required(login_url='/login/')
@tcle_required
def dashboard(request):
    aluno = request.user
    
    total_aulas = Videoaula.objects.count()
    aulas_concluidas = ProgressoAula.objects.filter(aluno=aluno, concluida=True).count()
    
    progresso_geral = 0
    if total_aulas > 0:
        progresso_geral = int((aulas_concluidas / total_aulas) * 100)
        
    ultimo_acesso = ProgressoAula.objects.filter(aluno=aluno).order_by('-ultimo_acesso').first()
    modulos = Modulo.objects.prefetch_related('videoaulas', 'atividades').order_by('ordem')
    
    context = {
        'progresso_geral': progresso_geral,
        'aulas_concluidas': aulas_concluidas,
        'total_aulas': total_aulas,
        'ultimo_acesso': ultimo_acesso,
        'modulos': modulos,
    }
    return render(request, 'dashboard.html', context)

@login_required(login_url='/login/')
@tcle_required
def detalhe_modulo(request, modulo_id):
    modulo = get_object_or_404(Modulo, id=modulo_id)
    aulas = modulo.videoaulas.all().order_by('ordem')
    atividades = modulo.atividades.all()
    
    progressos = ProgressoAula.objects.filter(aluno=request.user, aula__modulo=modulo)
    aulas_concluidas_ids = progressos.filter(concluida=True).values_list('aula_id', flat=True)
    
    pre_teste = atividades.filter(tipo='PRE').first()
    fez_pre_teste = True 
    if pre_teste and pre_teste.perguntas.exists():
        fez_pre_teste = RespostaAluno.objects.filter(aluno=request.user, pergunta__atividade=pre_teste).exists()
        
    total_aulas = aulas.count()
    assistiu_todas_aulas = False
    if total_aulas > 0 and len(aulas_concluidas_ids) == total_aulas:
        assistiu_todas_aulas = True

    atividades_concluidas_ids = RespostaAluno.objects.filter(
        aluno=request.user, 
        pergunta__atividade__modulo=modulo
    ).values_list('pergunta__atividade_id', flat=True).distinct()
    
    context = {
        'modulo': modulo,
        'aulas': aulas,
        'atividades': atividades,
        'aulas_concluidas_ids': aulas_concluidas_ids,
        'fez_pre_teste': fez_pre_teste,
        'assistiu_todas_aulas': assistiu_todas_aulas,
        'atividades_concluidas_ids': atividades_concluidas_ids,
    }
    return render(request, 'detalhe_modulo.html', context)

@login_required(login_url='/login/')
@tcle_required
def assistir_aula(request, aula_id):
    aula = get_object_or_404(Videoaula, id=aula_id)
    
    pre_teste = aula.modulo.atividades.filter(tipo='PRE').first()
    if pre_teste and pre_teste.perguntas.exists():
        fez_pre_teste = RespostaAluno.objects.filter(aluno=request.user, pergunta__atividade=pre_teste).exists()
        if not fez_pre_teste:
            return redirect('detalhe_modulo', modulo_id=aula.modulo.id)

    progresso, created = ProgressoAula.objects.get_or_create(aluno=request.user, aula=aula)
    progresso.save() 
    
    if request.method == 'POST':
        progresso.concluida = True
        progresso.save()
        return redirect('detalhe_modulo', modulo_id=aula.modulo.id)
        
    context = {'aula': aula, 'progresso': progresso}
    return render(request, 'assistir_aula.html', context)

@login_required(login_url='/login/')
@tcle_required
def responder_atividade(request, atividade_id):
    atividade = get_object_or_404(Atividade, id=atividade_id)
    
    if atividade.tipo == 'POS':
        aulas = atividade.modulo.videoaulas.all()
        aulas_concluidas = ProgressoAula.objects.filter(aluno=request.user, aula__modulo=atividade.modulo, concluida=True).count()
        if aulas.count() > 0 and aulas_concluidas < aulas.count():
            return redirect('detalhe_modulo', modulo_id=atividade.modulo.id)

    perguntas = atividade.perguntas.all().prefetch_related('alternativas', 'itens_associacao')
    
    ja_respondeu = False
    if perguntas.exists():
        ja_respondeu_multipla = RespostaAluno.objects.filter(aluno=request.user, pergunta=perguntas.first()).exists()
        ja_respondeu_assoc = RespostaAssociacaoAluno.objects.filter(aluno=request.user, pergunta=perguntas.first()).exists()
        ja_respondeu = ja_respondeu_multipla or ja_respondeu_assoc

    if request.method == 'POST' and not ja_respondeu:
        for pergunta in perguntas:
            if pergunta.tipo_pergunta == 'MULTIPLA':
                alternativa_id = request.POST.get(f'pergunta_{pergunta.id}')
                if alternativa_id:
                    alternativa = get_object_or_404(Alternativa, id=alternativa_id)
                    RespostaAluno.objects.create(aluno=request.user, pergunta=pergunta, alternativa=alternativa)
            
            elif pergunta.tipo_pergunta == 'ASSOC':
                for item in pergunta.itens_associacao.all():
                    resposta_b = request.POST.get(f'assoc_{pergunta.id}_{item.id}')
                    if resposta_b:
                        RespostaAssociacaoAluno.objects.create(
                            aluno=request.user,
                            pergunta=pergunta,
                            item_a=item,
                            resposta_aluno_coluna_b=resposta_b
                        )
        return redirect('detalhe_modulo', modulo_id=atividade.modulo.id)

    for pergunta in perguntas:
        if pergunta.tipo_pergunta == 'ASSOC':
            opcoes_b = list(pergunta.itens_associacao.values_list('coluna_b', flat=True))
            random.shuffle(opcoes_b)
            pergunta.opcoes_embaralhadas = opcoes_b

    context = {'atividade': atividade, 'perguntas': perguntas, 'ja_respondeu': ja_respondeu}
    return render(request, 'responder_atividade.html', context)

# ==========================================
# 4. ÁREA DO PESQUISADOR (PAINEL E DASHBOARDS)
# ==========================================

@staff_member_required(login_url='/login/')
def painel_pesquisador(request):
    query = request.GET.get('q', '')
    
    # 🚀 OTIMIZAÇÃO (N+1 Resolvido com os related_names exatos do seu model!)
    alunos = Usuario.objects.filter(is_staff=False).prefetch_related(
        'progressos_aulas', 
        'respostas_atividades__alternativa'
    )
    
    if query:
        alunos = alunos.filter(Q(nome__icontains=query) | Q(email__icontains=query))
        
    total_alunos = alunos.count()
    total_aulas_sistema = Videoaula.objects.count()
    
    # Busca apenas os IDs das perguntas em uma única consulta rápida
    perguntas_pre_ids = set(Pergunta.objects.filter(atividade__tipo='PRE').values_list('id', flat=True))
    perguntas_pos_ids = set(Pergunta.objects.filter(atividade__tipo='POS').values_list('id', flat=True))
    
    total_q_pre = len(perguntas_pre_ids)
    total_q_pos = len(perguntas_pos_ids)
    
    alunos_concluidos = soma_notas_pre = soma_notas_pos = 0
    alunos_fizeram_pre = alunos_fizeram_pos = 0
    alunos_data = []

    for aluno in alunos:
        # A. Calcula Progresso: Lendo direto da memória RAM (muito rápido)
        aulas_assistidas = sum(1 for p in aluno.progressos_aulas.all() if p.concluida)
        progresso = int((aulas_assistidas / total_aulas_sistema) * 100) if total_aulas_sistema > 0 else 0
        
        if progresso == 100:
            alunos_concluidos += 1
            
        # Puxa todas as respostas da memória RAM
        respostas = aluno.respostas_atividades.all()
        
        # B/C. Avaliação Pré-teste Rápida
        respostas_pre = [r for r in respostas if r.pergunta_id in perguntas_pre_ids]
        fez_pre = len(respostas_pre) > 0
        if fez_pre and total_q_pre > 0:
            acertos_pre = sum(1 for r in respostas_pre if r.alternativa and r.alternativa.is_correta)
            soma_notas_pre += (acertos_pre / total_q_pre) * 10
            alunos_fizeram_pre += 1
            
        # B/D. Avaliação Pós-teste Rápida
        respostas_pos = [r for r in respostas if r.pergunta_id in perguntas_pos_ids]
        fez_pos = len(respostas_pos) > 0
        if fez_pos and total_q_pos > 0:
            acertos_pos = sum(1 for r in respostas_pos if r.alternativa and r.alternativa.is_correta)
            soma_notas_pos += (acertos_pos / total_q_pos) * 10
            alunos_fizeram_pos += 1

        alunos_data.append({
            'nome': aluno.nome,
            'id': aluno.id,
            'aluno_id': aluno.id,
            'email': aluno.email,
            'data_cadastro': aluno.date_joined,
            'fez_pre': fez_pre,
            'fez_pos': fez_pos,
            'progresso': progresso,
        })
        
    taxa_conclusao = f"{(alunos_concluidos / total_alunos * 100):.0f}%" if total_alunos > 0 else "0%"
    media_pre = round(soma_notas_pre / alunos_fizeram_pre, 1) if alunos_fizeram_pre > 0 else 0.0
    media_pos = round(soma_notas_pos / alunos_fizeram_pos, 1) if alunos_fizeram_pos > 0 else 0.0

    context = {
        'total_alunos': total_alunos,
        'taxa_conclusao': taxa_conclusao,
        'alunos_concluidos': alunos_concluidos,
        'media_pre_teste': str(media_pre).replace('.', ','),
        'media_pos_teste': str(media_pos).replace('.', ','),
        'alunos_data': alunos_data,
        'query': query,
    }
    return render(request, 'painel_pesquisador.html', context)


@staff_member_required(login_url='/login/')
def exportar_dados_csv(request):
    response = HttpResponse(content_type='text/csv; charset=utf-8-sig')
    data_atual = timezone.now().strftime('%Y-%m-%d')
    response['Content-Disposition'] = f'attachment; filename="dataset_libras_{data_atual}.csv"'
    
    writer = csv.writer(response, delimiter=';')
    writer.writerow(['Nome do Sujeito', 'E-mail', 'Data de Ingresso', 'Progresso da Intervenção (%)', 'Fez Pré-teste', 'Nota Pré-teste', 'Fez Pós-teste', 'Nota Pós-teste'])
    
    # 🚀 Mesma OTIMIZAÇÃO aplicada na exportação do CSV
    alunos = Usuario.objects.filter(is_staff=False).prefetch_related(
        'progressos_aulas', 
        'respostas_atividades__alternativa'
    )
    total_aulas = Videoaula.objects.count()
    
    perguntas_pre_ids = set(Pergunta.objects.filter(atividade__tipo='PRE').values_list('id', flat=True))
    perguntas_pos_ids = set(Pergunta.objects.filter(atividade__tipo='POS').values_list('id', flat=True))
    total_q_pre = len(perguntas_pre_ids)
    total_q_pos = len(perguntas_pos_ids)
    
    for aluno in alunos:
        aulas_assistidas = sum(1 for p in aluno.progressos_aulas.all() if p.concluida)
        progresso = int((aulas_assistidas / total_aulas) * 100) if total_aulas > 0 else 0
        
        respostas = aluno.respostas_atividades.all()
        
        respostas_pre = [r for r in respostas if r.pergunta_id in perguntas_pre_ids]
        fez_pre = len(respostas_pre) > 0
        nota_pre = 0
        if fez_pre and total_q_pre > 0:
            acertos_pre = sum(1 for r in respostas_pre if r.alternativa and r.alternativa.is_correta)
            nota_pre = round((acertos_pre / total_q_pre) * 10, 1)
            
        respostas_pos = [r for r in respostas if r.pergunta_id in perguntas_pos_ids]
        fez_pos = len(respostas_pos) > 0
        nota_pos = 0
        if fez_pos and total_q_pos > 0:
            acertos_pos = sum(1 for r in respostas_pos if r.alternativa and r.alternativa.is_correta)
            nota_pos = round((acertos_pos / total_q_pos) * 10, 1)
        
        data_cadastro = aluno.date_joined.strftime('%d/%m/%Y') if getattr(aluno, 'date_joined', None) else 'N/A' 
        fez_pre_str = 'Sim' if fez_pre else 'Não'
        fez_pos_str = 'Sim' if fez_pos else 'Não'
        
        writer.writerow([
            aluno.nome, 
            aluno.email, 
            data_cadastro, 
            progresso, 
            fez_pre_str, 
            str(nota_pre).replace('.', ','), 
            fez_pos_str, 
            str(nota_pos).replace('.', ',')
        ])
        
    return response

@staff_member_required(login_url='/login/')
def busca_global_ajax(request):
    query = request.GET.get('q', '').strip()
    if len(query) < 2:
        return JsonResponse({'resultados': []})

    resultados = []

    alunos = Usuario.objects.filter(is_staff=False).filter(
        Q(nome__icontains=query) | Q(email__icontains=query)
    )[:3]
    for aluno in alunos:
        resultados.append({
            'tipo': 'Aluno (Amostra)',
            'icone': 'bi-person-fill text-primary',
            'texto': aluno.nome,
            'url': reverse('detalhe_participante', args=[aluno.id]) 
        })

    modulos = Modulo.objects.filter(titulo__icontains=query)[:3]
    for mod in modulos:
        resultados.append({
            'tipo': 'Módulo',
            'icone': 'bi-folder-fill text-success',
            'texto': mod.titulo,
            'url': reverse('editar_modulo', args=[mod.id])
        })

    aulas = Videoaula.objects.filter(titulo__icontains=query)[:3]
    for aula in aulas:
        resultados.append({
            'tipo': 'Videoaula',
            'icone': 'bi-play-btn-fill text-danger',
            'texto': aula.titulo,
            'url': reverse('editar_videoaula', args=[aula.id])
        })

    atividades = Atividade.objects.filter(titulo__icontains=query)[:3]
    for atv in atividades:
        resultados.append({
            'tipo': atv.get_tipo_display(),
            'icone': 'bi-file-earmark-text-fill text-warning',
            'texto': atv.titulo,
            'url': reverse('gerenciar_perguntas', args=[atv.id])
        })

    return JsonResponse({'resultados': resultados})

@staff_member_required(login_url='/login/')
def detalhe_participante(request, aluno_id):
    aluno = get_object_or_404(Usuario, id=aluno_id)
    
    if request.method == 'POST':
        acao = request.POST.get('acao')
        if acao == 'salvar_dados':
            aluno.nome = request.POST.get('nome')
            aluno.email = request.POST.get('email')
            aluno.is_active = request.POST.get('is_active') == 'on'
            aluno.is_staff = request.POST.get('is_staff') == 'on'
            aluno.tipo = request.POST.get('tipo')
            
            escola_id = request.POST.get('escola')
            if escola_id:
                aluno.escola_id = escola_id
            else:
                aluno.escola = None
                
            aluno.save()
            messages.success(request, 'Dados do participante atualizados com sucesso!')
            return redirect('detalhe_participante', aluno_id=aluno.id)
            
        elif acao == 'excluir_aluno':
            aluno.delete()
            messages.success(request, 'Participante excluído permanentemente do sistema.')
            return redirect('painel_pesquisador')
            
    escolas = Escola.objects.all()
    tipos_perfil = Usuario.TIPO_CHOICES
            
    context = {
        'aluno': aluno,
        'escolas': escolas,
        'tipos_perfil': tipos_perfil,
    }
    return render(request, 'detalhe_participante.html', context)

# ==========================================
# 5. ÁREA DE GESTÃO (CRUDs ADMINISTRATIVOS)
# ==========================================

@staff_member_required(login_url='/login/')
def gestao_modulos(request):
    modulos = Modulo.objects.all().order_by('ordem')
    return render(request, 'gestao_modulos.html', {'modulos': modulos})

@staff_member_required(login_url='/login/')
def criar_modulo(request):
    if request.method == 'POST':
        Modulo.objects.create(
            titulo=request.POST.get('titulo'),
            descricao=request.POST.get('descricao'),
            ordem=request.POST.get('ordem', 1),
            imagem_capa=request.FILES.get('imagem_capa')
        )
        return redirect('gestao_modulos')
    return render(request, 'criar_modulo.html')

@staff_member_required(login_url='/login/')
def editar_modulo(request, modulo_id):
    modulo = get_object_or_404(Modulo, id=modulo_id)
    if request.method == 'POST':
        modulo.titulo = request.POST.get('titulo')
        modulo.descricao = request.POST.get('descricao')
        modulo.ordem = request.POST.get('ordem', 1)
        if 'imagem_capa' in request.FILES:
            modulo.imagem_capa = request.FILES.get('imagem_capa')
        modulo.save()
        return redirect('gestao_modulos')
    return render(request, 'editar_modulo.html', {'modulo': modulo})

@staff_member_required(login_url='/login/')
def excluir_modulo(request, modulo_id):
    modulo = get_object_or_404(Modulo, id=modulo_id)
    if request.method == 'POST':
        modulo.delete()
    return redirect('gestao_modulos')

@staff_member_required(login_url='/login/')
def gestao_videoaulas(request):
    videoaulas = Videoaula.objects.select_related('modulo').order_by('modulo__ordem', 'ordem')
    return render(request, 'gestao_videoaulas.html', {'videoaulas': videoaulas})

@staff_member_required(login_url='/login/')
def criar_videoaula(request):
    modulos = Modulo.objects.all().order_by('ordem')
    if request.method == 'POST':
        modulo = get_object_or_404(Modulo, id=request.POST.get('modulo'))
        
        duracao_str = request.POST.get('duracao')
        duracao_obj = None
        if duracao_str:
            partes = duracao_str.split(':')
            if len(partes) == 3:
                duracao_obj = timedelta(hours=int(partes[0]), minutes=int(partes[1]), seconds=int(partes[2]))
            elif len(partes) == 2:
                duracao_obj = timedelta(hours=int(partes[0]), minutes=int(partes[1]))
        
        Videoaula.objects.create(
            titulo=request.POST.get('titulo'),
            descricao=request.POST.get('descricao'),
            modulo=modulo,
            ordem=request.POST.get('ordem', 1),
            duracao=duracao_obj,
            thumbnail=request.FILES.get('miniatura'), 
            video=request.FILES.get('arquivo_video')  
        )
        return redirect('gestao_videoaulas')
    return render(request, 'criar_videoaula.html', {'modulos': modulos})

@staff_member_required(login_url='/login/')
def editar_videoaula(request, aula_id):
    aula = get_object_or_404(Videoaula, id=aula_id)
    modulos = Modulo.objects.all().order_by('ordem')
    
    if request.method == 'POST':
        aula.modulo = get_object_or_404(Modulo, id=request.POST.get('modulo'))
        aula.titulo = request.POST.get('titulo')
        aula.descricao = request.POST.get('descricao')
        aula.ordem = request.POST.get('ordem', 1)
        
        duracao_str = request.POST.get('duracao')
        if duracao_str:
            partes = duracao_str.split(':')
            if len(partes) == 3:
                aula.duracao = timedelta(hours=int(partes[0]), minutes=int(partes[1]), seconds=int(partes[2]))
            elif len(partes) == 2:
                aula.duracao = timedelta(hours=int(partes[0]), minutes=int(partes[1]))
        
        if 'miniatura' in request.FILES:
            aula.thumbnail = request.FILES.get('miniatura')
        if 'arquivo_video' in request.FILES:
            aula.video = request.FILES.get('arquivo_video')
            
        aula.save()
        return redirect('gestao_videoaulas')
    return render(request, 'editar_videoaula.html', {'aula': aula, 'modulos': modulos})

@staff_member_required(login_url='/login/')
def excluir_videoaula(request, aula_id):
    aula = get_object_or_404(Videoaula, id=aula_id)
    if request.method == 'POST':
        aula.delete()
    return redirect('gestao_videoaulas')

@staff_member_required(login_url='/login/')
def gestao_atividades(request):
    atividades = Atividade.objects.select_related('modulo').order_by('modulo__ordem', 'tipo')
    return render(request, 'gestao_atividades.html', {'atividades': atividades})

@staff_member_required(login_url='/login/')
def criar_atividade(request):
    modulos = Modulo.objects.all().order_by('ordem')
    tipos_atividade = Atividade.TIPO_CHOICES 
    
    if request.method == 'POST':
        modulo_id = request.POST.get('modulo')
        modulo = get_object_or_404(Modulo, id=modulo_id) if modulo_id else None
        
        Atividade.objects.create(
            titulo=request.POST.get('titulo'),
            descricao=request.POST.get('descricao'),
            modulo=modulo,
            tipo=request.POST.get('tipo')
        )
        return redirect('gestao_atividades')
    return render(request, 'criar_atividade.html', {'modulos': modulos, 'tipos_atividade': tipos_atividade})

@staff_member_required(login_url='/login/')
def editar_atividade(request, atividade_id):
    atividade = get_object_or_404(Atividade, id=atividade_id)
    modulos = Modulo.objects.all().order_by('ordem')
    tipos_atividade = Atividade.TIPO_CHOICES
    
    if request.method == 'POST':
        modulo_id = request.POST.get('modulo')
        atividade.modulo = get_object_or_404(Modulo, id=modulo_id) if modulo_id else None
        atividade.titulo = request.POST.get('titulo')
        atividade.descricao = request.POST.get('descricao')
        atividade.tipo = request.POST.get('tipo')
        atividade.save()
        return redirect('gestao_atividades')
    return render(request, 'editar_atividade.html', {'atividade': atividade, 'modulos': modulos, 'tipos_atividade': tipos_atividade})

@staff_member_required(login_url='/login/')
def excluir_atividade(request, atividade_id):
    atividade = get_object_or_404(Atividade, id=atividade_id)
    if request.method == 'POST':
        atividade.delete()
    return redirect('gestao_atividades')

@staff_member_required(login_url='/login/')
def gerenciar_perguntas(request, atividade_id):
    atividade = get_object_or_404(Atividade, id=atividade_id)
    perguntas = atividade.perguntas.all().order_by('ordem')
    return render(request, 'gerenciar_perguntas.html', {'atividade': atividade, 'perguntas': perguntas})

@staff_member_required(login_url='/login/')
def criar_pergunta(request, atividade_id, tipo):
    atividade = get_object_or_404(Atividade, id=atividade_id)
    if tipo not in ['MULTIPLA', 'ASSOC']:
        return redirect('gerenciar_perguntas', atividade_id=atividade.id)
        
    if request.method == 'POST':
        Pergunta.objects.create(
            atividade=atividade,
            tipo_pergunta=tipo,
            enunciado=request.POST.get('enunciado'),
            ordem=request.POST.get('ordem', 1),
            imagem_apoio=request.FILES.get('imagem_apoio')
        )
        return redirect('gerenciar_perguntas', atividade_id=atividade.id)
    return render(request, 'criar_pergunta.html', {'atividade': atividade, 'tipo': tipo})

@staff_member_required(login_url='/login/')
def editar_pergunta(request, pergunta_id):
    pergunta = get_object_or_404(Pergunta, id=pergunta_id)
    atividade = pergunta.atividade
    if request.method == 'POST':
        pergunta.enunciado = request.POST.get('enunciado')
        pergunta.ordem = request.POST.get('ordem', 1)
        if 'imagem_apoio' in request.FILES:
            pergunta.imagem_apoio = request.FILES.get('imagem_apoio')
        pergunta.save()
        return redirect('gerenciar_perguntas', atividade_id=atividade.id)
    return render(request, 'editar_pergunta.html', {'pergunta': pergunta, 'atividade': atividade})

@staff_member_required(login_url='/login/')
def excluir_pergunta(request, pergunta_id):
    pergunta = get_object_or_404(Pergunta, id=pergunta_id)
    atividade_id = pergunta.atividade.id 
    if request.method == 'POST':
        pergunta.delete()
    return redirect('gerenciar_perguntas', atividade_id=atividade_id)

@staff_member_required(login_url='/login/')
def configurar_pergunta(request, pergunta_id):
    pergunta = get_object_or_404(Pergunta, id=pergunta_id)
    atividade = pergunta.atividade
    
    if request.method == 'POST':
        if pergunta.tipo_pergunta == 'MULTIPLA':
            Alternativa.objects.create(
                pergunta=pergunta,
                texto=request.POST.get('texto'),
                is_correta=request.POST.get('is_correta') == 'on'
            )
        elif pergunta.tipo_pergunta == 'ASSOC':
            ItemAssociacao.objects.create(
                pergunta=pergunta,
                coluna_a=request.POST.get('coluna_a'),
                coluna_b=request.POST.get('coluna_b')
            )
        return redirect('configurar_pergunta', pergunta_id=pergunta.id)
        
    alternativas = pergunta.alternativas.all() if pergunta.tipo_pergunta == 'MULTIPLA' else None
    itens_associacao = pergunta.itens_associacao.all() if pergunta.tipo_pergunta == 'ASSOC' else None
    
    context = {
        'pergunta': pergunta,
        'atividade': atividade,
        'alternativas': alternativas,
        'itens_associacao': itens_associacao
    }
    return render(request, 'configurar_pergunta.html', context)

@staff_member_required(login_url='/login/')
def excluir_alternativa(request, alternativa_id):
    alternativa = get_object_or_404(Alternativa, id=alternativa_id)
    pergunta_id = alternativa.pergunta.id
    if request.method == 'POST':
        alternativa.delete()
    return redirect('configurar_pergunta', pergunta_id=pergunta_id)

@staff_member_required(login_url='/login/')
def excluir_item_associacao(request, item_id):
    item = get_object_or_404(ItemAssociacao, id=item_id)
    pergunta_id = item.pergunta.id
    if request.method == 'POST':
        item.delete()
    return redirect('configurar_pergunta', pergunta_id=pergunta_id)