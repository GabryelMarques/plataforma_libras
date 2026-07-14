import random 
import csv
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



# O decorador @staff_member_required barra qualquer aluno comum de acessar essa URL
@staff_member_required(login_url='/login/')
def painel_pesquisador(request):
    # Pega apenas os alunos comuns (ignora contas de administradores/professores)
    alunos = Usuario.objects.filter(is_staff=False)
    total_alunos = alunos.count()
    
    # Métricas Gerais
    aulas_assistidas_total = ProgressoAula.objects.filter(concluida=True).count()
    total_videoaulas = Videoaula.objects.count()
    
    # Monta a tabela de alunos com o progresso de cada um
    alunos_data = []
    for aluno in alunos:
        # Quantas aulas esse aluno concluiu?
        aulas_aluno = ProgressoAula.objects.filter(aluno=aluno, concluida=True).count()
        
        # Calcula a % de progresso do aluno (evita erro de divisão por zero)
        progresso_percentual = int((aulas_aluno / total_videoaulas) * 100) if total_videoaulas > 0 else 0
        
        # Checa se o aluno já enviou algum pré-teste ou pós-teste
        fez_pre = RespostaAluno.objects.filter(aluno=aluno, pergunta__atividade__tipo='PRE').exists() or \
                  RespostaAssociacaoAluno.objects.filter(aluno=aluno, pergunta__atividade__tipo='PRE').exists()
                  
        fez_pos = RespostaAluno.objects.filter(aluno=aluno, pergunta__atividade__tipo='POS').exists() or \
                  RespostaAssociacaoAluno.objects.filter(aluno=aluno, pergunta__atividade__tipo='POS').exists()
        
        alunos_data.append({
            'nome': aluno.nome,
            'email': aluno.email,
            'data_cadastro': aluno.date_joined,
            'progresso': progresso_percentual,
            'fez_pre': fez_pre,
            'fez_pos': fez_pos,
        })
        
    context = {
        'total_alunos': total_alunos,
        'aulas_assistidas_total': aulas_assistidas_total,
        'alunos_data': alunos_data,
    }
    return render(request, 'painel_pesquisador.html', context)

@staff_member_required(login_url='/login/')
def exportar_dados_csv(request):
    # Configura a resposta do navegador para entender que é um download de arquivo CSV
    response = HttpResponse(content_type='text/csv')
    response['Content-Disposition'] = 'attachment; filename="dados_pesquisa_libras.csv"'

    # Usamos ponto e vírgula ';' como separador, pois o Excel em português do Brasil entende isso nativamente
    writer = csv.writer(response, delimiter=';')
    
    # Escreve o cabeçalho da planilha (A primeira linha em negrito no Excel)
    writer.writerow(['Aluno', 'Email', 'Módulo', 'Atividade', 'Tipo de Atividade', 'Enunciado / Coluna A', 'Resposta do Aluno', 'Gabarito Correto', 'Acertou?', 'Data/Hora da Resposta'])

    # 1. Busca e escreve as respostas de Múltipla Escolha
    respostas_multipla = RespostaAluno.objects.all().select_related('aluno', 'pergunta__atividade__modulo', 'alternativa')
    
    for r in respostas_multipla:
        pergunta = r.pergunta
        atividade = pergunta.atividade
        
        # Encontra qual era a alternativa correta no banco para comparar
        alternativa_correta = pergunta.alternativas.filter(is_correta=True).first()
        gabarito = alternativa_correta.texto if alternativa_correta else 'N/A'
        acertou = 'Sim' if r.alternativa.is_correta else 'Não'
        
        writer.writerow([
            r.aluno.nome,
            r.aluno.email,
            atividade.modulo.titulo,
            atividade.titulo,
            atividade.get_tipo_display(),
            pergunta.enunciado,
            r.alternativa.texto,
            gabarito,
            acertou,
            r.data_resposta.strftime('%d/%m/%Y %H:%M')
        ])

    # 2. Busca e escreve as respostas de Associação (Ligar Colunas)
    respostas_assoc = RespostaAssociacaoAluno.objects.all().select_related('aluno', 'pergunta__atividade__modulo', 'item_a')
    
    for r in respostas_assoc:
        pergunta = r.pergunta
        atividade = pergunta.atividade
        item = r.item_a
        
        acertou = 'Sim' if r.resposta_aluno_coluna_b == item.coluna_b else 'Não'
        
        writer.writerow([
            r.aluno.nome,
            r.aluno.email,
            atividade.modulo.titulo,
            atividade.titulo,
            atividade.get_tipo_display(),
            f"{pergunta.enunciado} (Item: {item.coluna_a})",
            r.resposta_aluno_coluna_b,
            item.coluna_b,
            acertou,
            r.data_resposta.strftime('%d/%m/%Y %H:%M')
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