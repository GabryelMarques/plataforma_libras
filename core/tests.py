from django.test import TestCase
from django.urls import reverse
from accounts.models import Usuario, TCLEAceite
from modulos.models import Modulo, Videoaula, ProgressoAula, Atividade, Pergunta, Alternativa, RespostaAluno

class SegurancaTCLETest(TestCase):
    def setUp(self):
        # Cria um aluno novato que acabou de se cadastrar (ainda não assinou o TCLE)
        self.aluno = Usuario.objects.create_user(
            email='tcle@teste.com',
            username='aluno_tcle',
            password='senha123',
            nome='Aluno Sem TCLE'
        )

    def test_redirecionamento_sem_tcle(self):
        """Garante que um aluno logado, mas sem TCLE, seja barrado do dashboard"""
        self.client.login(email='tcle@teste.com', password='senha123')
        response = self.client.get(reverse('dashboard'))
        # O sistema deve interceptar e redirecionar para a tela do TCLE (Código 302)
        self.assertRedirects(response, reverse('tcle_aceite'))

    def test_acesso_liberado_com_tcle(self):
        """Garante que o aluno acessa as aulas normalmente após assinar o TCLE"""
        TCLEAceite.objects.create(usuario=self.aluno, aceito=True)
        self.client.login(email='tcle@teste.com', password='senha123')
        response = self.client.get(reverse('dashboard'))
        # O sistema permite o acesso e carrega a tela com sucesso (Código 200 OK)
        self.assertEqual(response.status_code, 200)

    def test_tcle_aceite_nao_cria_duplicidade_e_redireciona(self):
        """Garante que o aceite do TCLE seja salvo uma única vez e não duplicate registros."""
        self.client.login(email='tcle@teste.com', password='senha123')

        response = self.client.post(reverse('tcle_aceite'))
        self.assertRedirects(response, reverse('dashboard'))
        self.assertEqual(TCLEAceite.objects.filter(usuario=self.aluno).count(), 1)

        response = self.client.post(reverse('tcle_aceite'))
        self.assertRedirects(response, reverse('dashboard'))
        self.assertEqual(TCLEAceite.objects.filter(usuario=self.aluno).count(), 1)

class PainelPesquisadorTests(TestCase):
    def test_painel_pesquisador_renders_student_link(self):
        """Garante que o painel do pesquisador carrega os dados dos alunos"""
        staff_user = Usuario.objects.create_user(
            username='staff', email='staff@example.com', password='secret123',
            nome='Equipe', is_staff=True,
        )
        Usuario.objects.create_user(
            username='aluno', email='aluno@example.com', password='secret123',
            nome='Aluno Teste',
        )
        self.client.force_login(staff_user)
        response = self.client.get(reverse('painel_pesquisador'))
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'Aluno Teste')

class HomeViewTests(TestCase):
    def test_home_shows_placeholder_when_cover_file_is_missing(self):
        """Garante que a Home não quebra se faltar a imagem de capa de um módulo"""
        Modulo.objects.create(
            titulo="Módulo teste", descricao="Descrição de teste", ordem=1,
            imagem_capa="capas/arquivo-nao-existe.jpg",
        )
        response = self.client.get(reverse("home"))
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "bi-image")
        self.assertNotContains(response, "/media/capas/arquivo-nao-existe.jpg")


class DashboardAndActivityLogicTests(TestCase):
    def setUp(self):
        self.aluno = Usuario.objects.create_user(
            email='dashboard@teste.com', username='dashboard_teste', password='senha123', nome='Aluno Dashboard'
        )
        TCLEAceite.objects.create(usuario=self.aluno, aceito=True)

    def test_dashboard_progress_counts_only_active_aulas(self):
        """Garante que o progresso do dashboard ignore aulas desativadas no cálculo."""
        self.client.force_login(self.aluno)

        modulo = Modulo.objects.create(titulo='Módulo teste', descricao='Descrição teste')
        aula_ativa = Videoaula.objects.create(modulo=modulo, titulo='Aula ativa')
        aula_inativa = Videoaula.objects.create(modulo=modulo, titulo='Aula antiga')
        aula_inativa.soft_delete()

        ProgressoAula.objects.create(aluno=self.aluno, aula=aula_ativa, concluida=True)
        ProgressoAula.objects.create(aluno=self.aluno, aula=aula_inativa, concluida=True)

        response = self.client.get(reverse('dashboard'))

        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.context['progresso_geral'], 100)

    def test_responder_atividade_bloqueia_acesso_apos_qualquer_resposta(self):
        """Garante que a atividade não fique disponível novamente após qualquer resposta registrada."""
        self.client.force_login(self.aluno)

        modulo = Modulo.objects.create(titulo='Módulo teste', descricao='Descrição teste')
        atividade = Atividade.objects.create(modulo=modulo, titulo='Atividade teste', tipo='EXERCICIO')
        pergunta_1 = Pergunta.objects.create(atividade=atividade, enunciado='Pergunta 1', tipo_pergunta='MULTIPLA')
        pergunta_2 = Pergunta.objects.create(atividade=atividade, enunciado='Pergunta 2', tipo_pergunta='MULTIPLA')

        alternativa = Alternativa.objects.create(pergunta=pergunta_2, texto='Opção', is_correta=True)
        RespostaAluno.objects.create(aluno=self.aluno, pergunta=pergunta_2, alternativa=alternativa)

        response = self.client.get(reverse('responder_atividade', args=[atividade.id]))

        self.assertRedirects(response, reverse('dashboard'))