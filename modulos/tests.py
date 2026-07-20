from django.test import TestCase
from django.db.models import ProtectedError
from accounts.models import Usuario
from modulos.models import (
    Modulo, Videoaula, ProgressoAula, 
    Atividade, Pergunta, Alternativa, RespostaAluno
)

class PesquisaDataIntegrityTest(TestCase):
    def setUp(self):
        self.aluno = Usuario.objects.create_user(
            email='aluno@teste.com', username='aluno_teste', password='senha123', nome='Aluno Teste'
        )
        self.modulo = Modulo.objects.create(titulo="Módulo 1", descricao="Módulo de Introdução")
        self.aula = Videoaula.objects.create(modulo=self.modulo, titulo="Aula 1: Alfabeto")
        
        # Estrutura de Prova
        self.atividade = Atividade.objects.create(modulo=self.modulo, titulo="Pré-teste", tipo="PRE")
        self.pergunta = Pergunta.objects.create(atividade=self.atividade, enunciado="Qual o sinal?", tipo_pergunta="MULTIPLA")
        self.alternativa = Alternativa.objects.create(pergunta=self.pergunta, texto="Opção A", is_correta=True)

    def test_soft_delete_default(self):
        """Garante que as novas aulas nascem ativas por padrão"""
        self.assertTrue(self.aula.is_active)
        self.assertTrue(self.pergunta.is_active)

    def test_protecao_dados_progresso_aula(self):
        """Garante que uma aula NÃO pode ser apagada se houver progresso salvo (PROTECT)"""
        ProgressoAula.objects.create(aluno=self.aluno, aula=self.aula, concluida=True)
        with self.assertRaises(ProtectedError):
            self.aula.delete()

    def test_protecao_dados_respostas_provas(self):
        """Garante que Perguntas e Alternativas NÃO podem ser apagadas se o aluno já respondeu (PROTECT)"""
        RespostaAluno.objects.create(aluno=self.aluno, pergunta=self.pergunta, alternativa=self.alternativa)
        
        # Tenta deletar a pergunta
        with self.assertRaises(ProtectedError):
            self.pergunta.delete()
            
        # Tenta deletar a alternativa
        with self.assertRaises(ProtectedError):
            self.alternativa.delete()