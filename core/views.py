import random 
from django.db.models import Q
import csv
from datetime import timedelta
from django.http import HttpResponse
from modulos.models import Modulo
from django.shortcuts import render
from django.contrib.auth.decorators import login_required
from modulos.models import Modulo, Videoaula, ProgressoAula
from django.shortcuts import render, get_object_or_404, redirect
from modulos.models import Modulo, Videoaula, ProgressoAula , Atividade, Pergunta, Alternativa, RespostaAluno, RespostaAssociacaoAluno, Videoaula
from django.contrib import messages
from django.contrib.admin.views.decorators import staff_member_required
from accounts.models import Usuario
from django.utils import timezone 
from django.http import JsonResponse
from django.urls import reverse

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
    modulo = get_object_or_404(Modulo, id=modulo_id)
    aulas = modulo.videoaulas.all().order_by('ordem')
    atividades = modulo.atividades.all()
    
    # 1. Progresso das aulas
    progressos = ProgressoAula.objects.filter(aluno=request.user, aula__modulo=modulo)
    aulas_concluidas_ids = progressos.filter(concluida=True).values_list('aula_id', flat=True)
    
    # 2. TRAVA DO PRÉ-TESTE: Verifica se existe e se foi respondido
    pre_teste = atividades.filter(tipo='PRE').first()
    fez_pre_teste = True # Se não tiver pré-teste no módulo, libera direto
    if pre_teste and pre_teste.perguntas.exists():
        fez_pre_teste = RespostaAluno.objects.filter(aluno=request.user, pergunta__atividade=pre_teste).exists()
        
    # 3. TRAVA DO PÓS-TESTE: Verifica se 100% das aulas foram assistidas
    total_aulas = aulas.count()
    assistiu_todas_aulas = False
    if total_aulas > 0 and len(aulas_concluidas_ids) == total_aulas:
        assistiu_todas_aulas = True

    # 4. QUAIS ATIVIDADES JÁ FORAM FEITAS? (Para mudar o botão para "Concluída")
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
def assistir_aula(request, aula_id):
    aula = get_object_or_404(Videoaula, id=aula_id)
    
    # PROTEÇÃO DE URL: Impede o aluno de digitar o link do vídeo se não fez o pré-teste
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
def responder_atividade(request, atividade_id):
    atividade = get_object_or_404(Atividade, id=atividade_id)
    
    # PROTEÇÃO DE URL DO PÓS-TESTE
    if atividade.tipo == 'POS':
        aulas = atividade.modulo.videoaulas.all()
        # Aqui pode precisar importar o ProgressoAula se não estiver no topo
        from modulos.models import ProgressoAula 
        aulas_concluidas = ProgressoAula.objects.filter(aluno=request.user, aula__modulo=atividade.modulo, concluida=True).count()
        if aulas.count() > 0 and aulas_concluidas < aulas.count():
            return redirect('detalhe_modulo', modulo_id=atividade.modulo.id)

    # Busca as perguntas trazendo as alternativas e os itens de associação
    perguntas = atividade.perguntas.all().prefetch_related('alternativas', 'itens_associacao')
    
    ja_respondeu = False
    if perguntas.exists():
        # Verifica se ele já respondeu uma múltipla escolha ou uma associação desta prova
        ja_respondeu_multipla = RespostaAluno.objects.filter(aluno=request.user, pergunta=perguntas.first()).exists()
        ja_respondeu_assoc = RespostaAssociacaoAluno.objects.filter(aluno=request.user, pergunta=perguntas.first()).exists()
        ja_respondeu = ja_respondeu_multipla or ja_respondeu_assoc

    # LÓGICA DO METÓDO POST (Quando o aluno clica em Enviar)
    if request.method == 'POST' and not ja_respondeu:
        for pergunta in perguntas:
            
            # Se for MÚLTIPLA ESCOLHA
            if pergunta.tipo_pergunta == 'MULTIPLA':
                alternativa_id = request.POST.get(f'pergunta_{pergunta.id}')
                if alternativa_id:
                    alternativa = get_object_or_404(Alternativa, id=alternativa_id)
                    RespostaAluno.objects.create(aluno=request.user, pergunta=pergunta, alternativa=alternativa)
            
            # Se for ASSOCIAÇÃO
            elif pergunta.tipo_pergunta == 'ASSOC':
                for item in pergunta.itens_associacao.all():
                    # O HTML vai mandar o ID do item A para a gente saber o que ele respondeu no B
                    resposta_b = request.POST.get(f'assoc_{pergunta.id}_{item.id}')
                    if resposta_b:
                        RespostaAssociacaoAluno.objects.create(
                            aluno=request.user,
                            pergunta=pergunta,
                            item_a=item,
                            resposta_aluno_coluna_b=resposta_b
                        )
        
        return redirect('detalhe_modulo', modulo_id=atividade.modulo.id)

    # LÓGICA DO MÉTODO GET (Embaralhar as opções antes de mostrar a prova)
    for pergunta in perguntas:
        if pergunta.tipo_pergunta == 'ASSOC':
            # Pega todos os textos da coluna B, transforma numa lista e embaralha
            opcoes_b = list(pergunta.itens_associacao.values_list('coluna_b', flat=True))
            random.shuffle(opcoes_b)
            # Guarda as opções embaralhadas temporariamente na pergunta para o HTML ler
            pergunta.opcoes_embaralhadas = opcoes_b

    context = {'atividade': atividade, 'perguntas': perguntas, 'ja_respondeu': ja_respondeu}
    return render(request, 'responder_atividade.html', context)





@staff_member_required(login_url='/login/')
def painel_pesquisador(request):
    # 1. SISTEMA DE BUSCA GLOBAL
    query = request.GET.get('q', '')
    alunos = Usuario.objects.filter(is_staff=False)
    
    if query:
        alunos = alunos.filter(Q(nome__icontains=query) | Q(email__icontains=query))
        
    total_alunos = alunos.count()
    
    # 2. VARIÁVEIS PARA OS CÁLCULOS GERAIS
    total_aulas_sistema = Videoaula.objects.count()
    perguntas_pre = Pergunta.objects.filter(atividade__tipo='PRE')
    perguntas_pos = Pergunta.objects.filter(atividade__tipo='POS')
    
    total_q_pre = perguntas_pre.count()
    total_q_pos = perguntas_pos.count()
    
    alunos_concluidos = 0
    soma_notas_pre = 0
    soma_notas_pos = 0
    alunos_fizeram_pre = 0
    alunos_fizeram_pos = 0
    
    alunos_data = []

    # 3. MOTOR DE PROCESSAMENTO INDIVIDUAL
    for aluno in alunos:
        # A. Calcula Progresso das Aulas
        aulas_assistidas = ProgressoAula.objects.filter(aluno=aluno, concluida=True).count()
        progresso = int((aulas_assistidas / total_aulas_sistema) * 100) if total_aulas_sistema > 0 else 0
        
        if progresso == 100:
            alunos_concluidos += 1
            
        # B. Checa se fez os testes
        fez_pre = RespostaAluno.objects.filter(aluno=aluno, pergunta__in=perguntas_pre).exists()
        fez_pos = RespostaAluno.objects.filter(aluno=aluno, pergunta__in=perguntas_pos).exists()
        
        # C. Calcula a Nota do Pré-teste (0 a 10)
        if fez_pre and total_q_pre > 0:
            acertos_pre = RespostaAluno.objects.filter(aluno=aluno, pergunta__in=perguntas_pre, alternativa__is_correta=True).count()
            nota_pre = (acertos_pre / total_q_pre) * 10
            soma_notas_pre += nota_pre
            alunos_fizeram_pre += 1
            
        # D. Calcula a Nota do Pós-teste (0 a 10)
        if fez_pos and total_q_pos > 0:
            acertos_pos = RespostaAluno.objects.filter(aluno=aluno, pergunta__in=perguntas_pos, alternativa__is_correta=True).count()
            nota_pos = (acertos_pos / total_q_pos) * 10
            soma_notas_pos += nota_pos
            alunos_fizeram_pos += 1

        # E. Salva os dados para a Tabela HTML
        alunos_data.append({
            'nome': aluno.nome,
            'email': aluno.email,
            'data_cadastro': aluno.date_joined, # Altere para o campo de data de criação correto do seu model Usuario
            'fez_pre': fez_pre,
            'fez_pos': fez_pos,
            'progresso': progresso,
        })
        
    # 4. CÁLCULO DAS MÉDIAS FINAIS DO PAINEL
    taxa_conclusao = f"{(alunos_concluidos / total_alunos * 100):.0f}%" if total_alunos > 0 else "0%"
    
    # Faz a média e converte para string com vírgula (ex: "8.5" vira "8,5")
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
    # 1. Configura a resposta HTTP para forçar o download do arquivo
    response = HttpResponse(content_type='text/csv; charset=utf-8-sig') # utf-8-sig aceita acentuação no Excel
    data_atual = timezone.now().strftime('%Y-%m-%d')
    response['Content-Disposition'] = f'attachment; filename="dataset_libras_{data_atual}.csv"'
    
    # 2. Cria o escritor do CSV (Usando ';' para compatibilidade com o Excel BR)
    writer = csv.writer(response, delimiter=';')
    
    # 3. Escreve o Cabeçalho (a primeira linha do arquivo)
    writer.writerow(['Nome do Sujeito', 'E-mail', 'Data de Ingresso', 'Progresso da Intervenção (%)', 'Fez Pré-teste', 'Nota Pré-teste', 'Fez Pós-teste', 'Nota Pós-teste'])
    
    # 4. Busca os dados reais
    alunos = Usuario.objects.filter(is_staff=False)
    total_aulas = Videoaula.objects.count()
    perguntas_pre = Pergunta.objects.filter(atividade__tipo='PRE')
    perguntas_pos = Pergunta.objects.filter(atividade__tipo='POS')
    total_q_pre = perguntas_pre.count()
    total_q_pos = perguntas_pos.count()
    
    for aluno in alunos:
        # Progresso
        aulas_assistidas = ProgressoAula.objects.filter(aluno=aluno, concluida=True).count()
        progresso = int((aulas_assistidas / total_aulas) * 100) if total_aulas > 0 else 0
        
        # Pré-teste
        fez_pre = RespostaAluno.objects.filter(aluno=aluno, pergunta__in=perguntas_pre).exists()
        nota_pre = 0
        if fez_pre and total_q_pre > 0:
            acertos_pre = RespostaAluno.objects.filter(aluno=aluno, pergunta__in=perguntas_pre, alternativa__is_correta=True).count()
            nota_pre = round((acertos_pre / total_q_pre) * 10, 1)
            
        # Pós-teste
        fez_pos = RespostaAluno.objects.filter(aluno=aluno, pergunta__in=perguntas_pos).exists()
        nota_pos = 0
        if fez_pos and total_q_pos > 0:
            acertos_pos = RespostaAluno.objects.filter(aluno=aluno, pergunta__in=perguntas_pos, alternativa__is_correta=True).count()
            nota_pos = round((acertos_pos / total_q_pos) * 10, 1)
        
        # Formatação de texto para o Excel
        # Confirme se seu model de usuário usa 'date_joined' ou outro nome
        data_cadastro = aluno.date_joined.strftime('%d/%m/%Y') if aluno.date_joined else 'N/A' 
        fez_pre_str = 'Sim' if fez_pre else 'Não'
        fez_pos_str = 'Sim' if fez_pos else 'Não'
        
        # 5. Escreve a linha do aluno no arquivo
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

from modulos.models import Modulo # Certifique-se de que Modulo está importado
from django.contrib.admin.views.decorators import staff_member_required

@staff_member_required(login_url='/login/')
def gestao_modulos(request):
    # Puxa todos os módulos ordenados
    modulos = Modulo.objects.all().order_by('ordem')
    
    context = {
        'modulos': modulos,
    }
    return render(request, 'gestao_modulos.html', context)

@staff_member_required(login_url='/login/')
def criar_modulo(request):
    if request.method == 'POST':
        titulo = request.POST.get('titulo')
        descricao = request.POST.get('descricao')
        ordem = request.POST.get('ordem', 1)
        # request.FILES pega os arquivos enviados (como a imagem da capa)
        imagem_capa = request.FILES.get('imagem_capa')

        # Cria o módulo no banco de dados
        Modulo.objects.create(
            titulo=titulo,
            descricao=descricao,
            ordem=ordem,
            imagem_capa=imagem_capa
        )
        
        # Volta para a lista de módulos após salvar
        return redirect('gestao_modulos')
        
    return render(request, 'criar_modulo.html')

@staff_member_required(login_url='/login/')
def editar_modulo(request, modulo_id):
    modulo = get_object_or_404(Modulo, id=modulo_id)
    
    if request.method == 'POST':
        modulo.titulo = request.POST.get('titulo')
        modulo.descricao = request.POST.get('descricao')
        modulo.ordem = request.POST.get('ordem', 1)
        
        # Só atualiza a imagem se o usuário tiver enviado uma nova
        if 'imagem_capa' in request.FILES:
            modulo.imagem_capa = request.FILES.get('imagem_capa')
            
        modulo.save()
        return redirect('gestao_modulos')
        
    return render(request, 'editar_modulo.html', {'modulo': modulo})

@staff_member_required(login_url='/login/')
def excluir_modulo(request, modulo_id):
    modulo = get_object_or_404(Modulo, id=modulo_id)
    
    # Exige o método POST por segurança (evita que um link solto exclua dados)
    if request.method == 'POST':
        modulo.delete()
        
    return redirect('gestao_modulos')

from modulos.models import Modulo, Videoaula # Atualize seus imports no topo

# ==========================================
# GESTÃO DE VIDEOAULAS
# ==========================================

@staff_member_required(login_url='/login/')
def gestao_videoaulas(request):
    # Puxa todas as videoaulas, trazendo junto a informação do módulo para não pesar o banco
    videoaulas = Videoaula.objects.select_related('modulo').order_by('modulo__ordem', 'ordem')
    return render(request, 'gestao_videoaulas.html', {'videoaulas': videoaulas})

@staff_member_required(login_url='/login/')
def criar_videoaula(request):
    modulos = Modulo.objects.all().order_by('ordem')
    
    if request.method == 'POST':
        modulo_id = request.POST.get('modulo')
        modulo = get_object_or_404(Modulo, id=modulo_id)
        
        # Converte a string "HH:MM:SS" ou "HH:MM" para um objeto timedelta que o banco aceita
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
            duracao=duracao_obj, # Passamos o objeto convertido
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
        modulo_id = request.POST.get('modulo')
        aula.modulo = get_object_or_404(Modulo, id=modulo_id)
        aula.titulo = request.POST.get('titulo')
        aula.descricao = request.POST.get('descricao')
        aula.ordem = request.POST.get('ordem', 1)
        
        # Converte a string da edição para timedelta
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

from modulos.models import Modulo, Videoaula, Atividade # <-- Adicione Atividade aqui

# ==========================================
# GESTÃO DE ATIVIDADES (PRÉ E PÓS TESTES)
# ==========================================

@staff_member_required(login_url='/login/')
def gestao_atividades(request):
    # Puxa todas as atividades, ordenadas pela ordem do módulo e depois pelo tipo
    atividades = Atividade.objects.select_related('modulo').order_by('modulo__ordem', 'tipo')
    return render(request, 'gestao_atividades.html', {'atividades': atividades})

@staff_member_required(login_url='/login/')
def criar_atividade(request):
    modulos = Modulo.objects.all().order_by('ordem')
    tipos_atividade = Atividade.TIPO_CHOICES 
    
    if request.method == 'POST':
        modulo_id = request.POST.get('modulo')
        # A mágica acontece aqui: se não houver modulo_id, ele salva como None (vazio)
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
        # Atualiza para o módulo escolhido, ou None se for Avaliação Global
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

from modulos.models import Modulo, Videoaula, Atividade, Pergunta # <-- Adicione Pergunta

# ==========================================
# GESTÃO DE PERGUNTAS
# ==========================================

@staff_member_required(login_url='/login/')
def gerenciar_perguntas(request, atividade_id):
    atividade = get_object_or_404(Atividade, id=atividade_id)
    # Puxa as perguntas apenas desta atividade, ordenadas pela numeração
    perguntas = atividade.perguntas.all().order_by('ordem')
    
    context = {
        'atividade': atividade,
        'perguntas': perguntas
    }
    return render(request, 'gerenciar_perguntas.html', context)

@staff_member_required(login_url='/login/')
def criar_pergunta(request, atividade_id, tipo):
    atividade = get_object_or_404(Atividade, id=atividade_id)
    
    # Validação de segurança para garantir que o tipo é válido
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
        # Após salvar o enunciado, volta para a lista de perguntas
        return redirect('gerenciar_perguntas', atividade_id=atividade.id)
        
    return render(request, 'criar_pergunta.html', {'atividade': atividade, 'tipo': tipo})

@staff_member_required(login_url='/login/')
def editar_pergunta(request, pergunta_id):
    pergunta = get_object_or_404(Pergunta, id=pergunta_id)
    atividade = pergunta.atividade
    
    if request.method == 'POST':
        pergunta.enunciado = request.POST.get('enunciado')
        pergunta.ordem = request.POST.get('ordem', 1)
        
        # Só atualiza a imagem se o usuário enviou uma nova
        if 'imagem_apoio' in request.FILES:
            pergunta.imagem_apoio = request.FILES.get('imagem_apoio')
            
        pergunta.save()
        return redirect('gerenciar_perguntas', atividade_id=atividade.id)
        
    return render(request, 'editar_pergunta.html', {'pergunta': pergunta, 'atividade': atividade})


@staff_member_required(login_url='/login/')
def excluir_pergunta(request, pergunta_id):
    pergunta = get_object_or_404(Pergunta, id=pergunta_id)
    atividade_id = pergunta.atividade.id # Guardamos o ID antes de apagar para poder voltar pra tela certa
    
    if request.method == 'POST':
        pergunta.delete()
        
    return redirect('gerenciar_perguntas', atividade_id=atividade_id)


from modulos.models import Modulo, Videoaula, Atividade, Pergunta, Alternativa, ItemAssociacao # Atualize os imports

# ==========================================
# CONFIGURAÇÃO DE ALTERNATIVAS E ASSOCIAÇÕES
# ==========================================

@staff_member_required(login_url='/login/')
def configurar_pergunta(request, pergunta_id):
    pergunta = get_object_or_404(Pergunta, id=pergunta_id)
    atividade = pergunta.atividade
    
    if request.method == 'POST':
        if pergunta.tipo_pergunta == 'MULTIPLA':
            Alternativa.objects.create(
                pergunta=pergunta,
                texto=request.POST.get('texto'),
                is_correta=request.POST.get('is_correta') == 'on' # Retorna True se o checkbox for marcado
            )
        elif pergunta.tipo_pergunta == 'ASSOC':
            ItemAssociacao.objects.create(
                pergunta=pergunta,
                coluna_a=request.POST.get('coluna_a'),
                coluna_b=request.POST.get('coluna_b')
            )
        # Recarrega a própria página para continuar adicionando itens
        return redirect('configurar_pergunta', pergunta_id=pergunta.id)
        
    # Puxa os dados existentes para listar na tela
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

@staff_member_required(login_url='/login/')
def busca_global_ajax(request):
    query = request.GET.get('q', '').strip()
    
    # Se digitar menos de 2 letras, não pesquisa nada para economizar banco de dados
    if len(query) < 2:
        return JsonResponse({'resultados': []})

    resultados = []

    # 1. Busca por Alunos
    alunos = Usuario.objects.filter(is_staff=False).filter(
        Q(nome__icontains=query) | Q(email__icontains=query)
    )[:3] # Limita a 3 resultados
    
    for aluno in alunos:
        resultados.append({
            'tipo': 'Aluno (Amostra)',
            'icone': 'bi-person-fill text-primary',
            'texto': aluno.nome,
            # Clicar no aluno redireciona para a própria tabela filtrada por ele
            'url': f"?q={aluno.nome}" 
        })

    # 2. Busca por Atividades / Testes
    atividades = Atividade.objects.filter(titulo__icontains=query)[:3]
    
    for atv in atividades:
        # Clicar no teste já joga o professor pra tela de gerenciar as perguntas dele!
        url = reverse('gerenciar_perguntas', args=[atv.id])
        tipo_nome = atv.get_tipo_display()
        
        resultados.append({
            'tipo': tipo_nome,
            'icone': 'bi-file-earmark-text-fill text-warning',
            'texto': atv.titulo,
            'url': url
        })

    return JsonResponse({'resultados': resultados})