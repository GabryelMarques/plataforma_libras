from django.test import TestCase
from django.urls import reverse

from accounts.models import Usuario


class PainelPesquisadorTests(TestCase):
    def test_painel_pesquisador_renders_student_link(self):
        staff_user = Usuario.objects.create_user(
            username='staff',
            email='staff@example.com',
            password='secret123',
            nome='Equipe',
            is_staff=True,
        )
        Usuario.objects.create_user(
            username='aluno',
            email='aluno@example.com',
            password='secret123',
            nome='Aluno Teste',
        )

        self.client.force_login(staff_user)
        response = self.client.get(reverse('painel_pesquisador'))

        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'Aluno Teste')
