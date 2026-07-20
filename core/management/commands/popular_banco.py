import random
from django.core.management.base import BaseCommand
from accounts.models import Usuario, Escola, TCLEAceite
from modulos.models import (
    Modulo, Videoaula, Atividade, Pergunta, Alternativa, ItemAssociacao,
    ProgressoAula, RespostaAluno, RespostaAssociacaoAluno
)

class Command(BaseCommand):
    help = 'Popula o banco de dados com dados iniciais para teste da pesquisa'

    def handle(self, *args, **kwargs):
        self.stdout.write(self.style.WARNING('Iniciando a Parte 1: Criando Estrutura e Aulas...'))

        # ==========================================
        # 1. CRIAR ESCOLA E ADMIN
        # ==========================================
        escola, _ = Escola.objects.get_or_create(
            nome="Escola Modelo Estadual", defaults={'cidade': 'Palmas'}
        )
        self.stdout.write(self.style.SUCCESS(f'✅ Escola criada: {escola.nome}'))

        if not Usuario.objects.filter(email='admin@uft.edu.br').exists():
            Usuario.objects.create_superuser(
                username='pesquisador', email='admin@uft.edu.br', password='admin',
                nome='Pesquisador UFT', tipo='ADMIN'
            )
            self.stdout.write(self.style.SUCCESS('✅ Admin criado! (Email: admin@uft.edu.br | Senha: admin)'))

        # ==========================================
        # 2. CRIAR MÓDULOS E VIDEOAULAS
        # ==========================================
        modulo1, _ = Modulo.objects.get_or_create(ordem=1, defaults={'titulo': 'Módulo 1: Conceitos Básicos', 'descricao': 'Introdução à plataforma.'})
        modulo2, _ = Modulo.objects.get_or_create(ordem=2, defaults={'titulo': 'Módulo 2: Conteúdo Específico', 'descricao': 'Sinais avançados.'})

        Videoaula.objects.get_or_create(modulo=modulo1, titulo='Aula 1: Apresentação', defaults={'ordem': 1})
        Videoaula.objects.get_or_create(modulo=modulo1, titulo='Aula 2: O Alfabeto', defaults={'ordem': 2})
        Videoaula.objects.get_or_create(modulo=modulo2, titulo='Aula 3: Termos Técnicos A', defaults={'ordem': 1})
        self.stdout.write(self.style.SUCCESS('✅ Módulos e Videoaulas garantidos no banco.'))

        # ==========================================
        # PARTE 2: CRIAR ATIVIDADES (PROVAS)
        # ==========================================
        self.stdout.write(self.style.WARNING('\nIniciando a Parte 2: Motor de Provas...'))
        
        pre_teste, _ = Atividade.objects.get_or_create(modulo=modulo1, tipo='PRE', defaults={'titulo': 'Pré-teste Diagnóstico', 'descricao': 'Avaliação inicial.'})
        pos_teste, _ = Atividade.objects.get_or_create(modulo=modulo2, tipo='POS', defaults={'titulo': 'Pós-teste de Validação', 'descricao': 'Avaliação final.'})
        self.stdout.write(self.style.SUCCESS('✅ Provas (Pré-teste e Pós-teste) criadas.'))

        # Perguntas Múltipla Escolha
        p1_pre, created_p1_pre = Pergunta.objects.get_or_create(atividade=pre_teste, ordem=1, defaults={'tipo_pergunta': 'MULTIPLA', 'enunciado': 'O que significa a sigla LIBRAS?'})
        if created_p1_pre:
            Alternativa.objects.create(pergunta=p1_pre, texto='Língua Brasileira de Sinais', is_correta=True)
            Alternativa.objects.create(pergunta=p1_pre, texto='Linguagem Brasileira de Sinais', is_correta=False)

        p1_pos, created_p1_pos = Pergunta.objects.get_or_create(atividade=pos_teste, ordem=1, defaults={'tipo_pergunta': 'MULTIPLA', 'enunciado': 'Qual parâmetro define o local do corpo?'})
        if created_p1_pos:
            Alternativa.objects.create(pergunta=p1_pos, texto='Ponto de Articulação', is_correta=True)
            Alternativa.objects.create(pergunta=p1_pos, texto='Expressão Facial', is_correta=False)

        # Pergunta Associação (Ligar Colunas)
        p2_pre, created_p2_pre = Pergunta.objects.get_or_create(atividade=pre_teste, ordem=2, defaults={'tipo_pergunta': 'ASSOC', 'enunciado': 'Ligue o conceito à sua definição:'})
        if created_p2_pre:
            ItemAssociacao.objects.create(pergunta=p2_pre, coluna_a='Surdo', coluna_b='Usa a Libras como primeira língua')
            ItemAssociacao.objects.create(pergunta=p2_pre, coluna_a='Intérprete', coluna_b='Traduz entre Libras e Português')

        self.stdout.write(self.style.SUCCESS('✅ Perguntas e Alternativas garantidas.'))

        # ==========================================
        # PARTE 3: CRIAR ALUNOS E SIMULAR ACESSOS
        # ==========================================
        self.stdout.write(self.style.WARNING('\nIniciando a Parte 3: Gerando 10 Alunos, TCLE e Respostas...'))

        videoaulas = Videoaula.objects.all()
        perguntas_multipla = Pergunta.objects.filter(tipo_pergunta='MULTIPLA')
        perguntas_assoc = Pergunta.objects.filter(tipo_pergunta='ASSOC')

        for i in range(1, 11):
            email_aluno = f'aluno{i}@teste.com'
            
            # 1. Cria o Aluno
            aluno, created_aluno = Usuario.objects.get_or_create(
                email=email_aluno,
                defaults={'username': f'aluno_{i}', 'nome': f'Aluno Fictício {i}', 'escola': escola, 'tipo': 'ESTUDANTE'}
            )
            
            if created_aluno:
                aluno.set_password('senha123')
                aluno.save()

            # 2. Assina o TCLE (Todos assinam)
            TCLEAceite.objects.get_or_create(usuario=aluno, defaults={'aceito': True, 'ip_aceite': '192.168.0.1'})

            # 3. Simula visualização de videoaulas (Alguns assistem, outros não)
            for aula in videoaulas:
                ProgressoAula.objects.get_or_create(
                    aluno=aluno, aula=aula, defaults={'concluida': random.choice([True, True, False])} # 66% de chance de concluir
                )

            # 4. Simula as respostas de Múltipla Escolha
            for pergunta in perguntas_multipla:
                alternativas = list(pergunta.alternativas.all())
                if alternativas:
                    # O robô escolhe uma alternativa aleatoriamente
                    RespostaAluno.objects.get_or_create(
                        aluno=aluno, pergunta=pergunta, defaults={'alternativa': random.choice(alternativas)}
                    )

            # 5. Simula as respostas de Associação (Ligar colunas)
            for pergunta in perguntas_assoc:
                itens_a = list(pergunta.itens_associacao.all())
                opcoes_b = [item.coluna_b for item in itens_a]
                for item_a in itens_a:
                    RespostaAssociacaoAluno.objects.get_or_create(
                        aluno=aluno, pergunta=pergunta, item_a=item_a, defaults={'resposta_aluno_coluna_b': random.choice(opcoes_b)}
                    )

        self.stdout.write(self.style.SUCCESS(f'✅ 10 Alunos criados e simulados! (Senha padrão: senha123)'))
        
        self.stdout.write(self.style.SUCCESS('\n🎉 BANCO DE DADOS POPULADO COM SUCESSO!'))
        self.stdout.write(self.style.WARNING('👉 Teste como Pesquisador: admin@uft.edu.br | Senha: admin'))
        self.stdout.write(self.style.WARNING('👉 Teste como Aluno: aluno1@teste.com | Senha: senha123'))