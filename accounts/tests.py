from django.test import TestCase
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