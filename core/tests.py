from django.test import TestCase
from django.urls import reverse
from accounts.models import Usuario, TCLEAceite
from modulos.models import Modulo

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