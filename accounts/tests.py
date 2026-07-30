from django.test import TestCase
from django.urls import reverse
from accounts.models import Usuario, Escola

class UsuarioModelTest(TestCase):
    def setUp(self):
        # Prepara o cenário criando uma escola e um aluno
        self.escola = Escola.objects.create(nome="Escola Estadual Padrão", cidade="Palmas")
        self.aluno = Usuario.objects.create_user(
            email="aluno@teste.com",
            username="aluno_teste",
            password="senha123",
            nome="Aluno da Silva",
            escola=self.escola
        )

    def test_criacao_usuario_estudante(self):
        """Garante que o aluno é criado corretamente e vinculado à escola"""
        self.assertEqual(self.aluno.email, "aluno@teste.com")
        self.assertEqual(self.aluno.escola.nome, "Escola Estadual Padrão")
        self.assertEqual(self.aluno.tipo, "ESTUDANTE")
        self.assertFalse(self.aluno.is_staff)

    def test_cadastro_salva_is_surdo_no_usuario(self):
        """Garante que o valor do campo is_surdo do formulário é salvo no usuário."""
        escola = Escola.objects.create(nome="Escola Teste", cidade="Palmas")
        response = self.client.post(reverse('cadastro'), {
            'nome': 'Maria Silva',
            'email': 'maria@teste.com',
            'is_surdo': 'True',
            'escola': escola.id,
            'senha': 'senha1234',
            'confirmar_senha': 'senha1234',
        })

        self.assertEqual(response.status_code, 302)
        usuario = Usuario.objects.get(email='maria@teste.com')
        self.assertTrue(usuario.is_surdo)