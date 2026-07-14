from django.db import models
from accounts.models import Usuario

class Modulo(models.Model):
    titulo = models.CharField(max_length=255, verbose_name="Título")
    descricao = models.TextField(verbose_name="Descrição")
    ordem = models.IntegerField(default=1, verbose_name="Ordem de Exibição")
    imagem_capa = models.ImageField(upload_to="capas/", blank=True, null=True, verbose_name="Imagem de Capa")

    @property
    def tem_imagem_capa(self):
        if not self.imagem_capa:
            return False
        return self.imagem_capa.storage.exists(self.imagem_capa.name)

    def __str__(self):
        return f"Módulo {self.ordem}: {self.titulo}"

class Videoaula(models.Model):
    modulo = models.ForeignKey(Modulo, on_delete=models.CASCADE, related_name='videoaulas')
    titulo = models.CharField(max_length=255, verbose_name="Título")
    
    video = models.FileField(upload_to="videos/", blank=True, null=True, verbose_name="Arquivo de Vídeo")
    thumbnail = models.ImageField(upload_to="thumbs/", blank=True, null=True, verbose_name="Miniatura (Thumbnail)")
    
    descricao = models.TextField(blank=True, null=True, verbose_name="Descrição")
    duracao = models.DurationField(blank=True, null=True, verbose_name="Duração (HH:MM:SS)")
    ordem = models.PositiveIntegerField(default=1, verbose_name="Ordem de Exibição")

    def __str__(self):
        return self.titulo

class Atividade(models.Model):
    modulo = models.ForeignKey(Modulo, on_delete=models.CASCADE, related_name='atividades')
    titulo = models.CharField(max_length=255, verbose_name="Título")
    descricao = models.TextField(verbose_name="Descrição")
    
    # --- NOVIDADE AQUI: O tipo da atividade ---
    TIPO_CHOICES = (
        ('PRE', 'Pré-teste'),
        ('POS', 'Pós-teste'),
        ('EXERCICIO', 'Exercício de Fixação'),
    )
    tipo = models.CharField(max_length=15, choices=TIPO_CHOICES, default='EXERCICIO')

    def __str__(self):
        return self.titulo

class ProgressoAula(models.Model):
    aluno = models.ForeignKey(Usuario, on_delete=models.CASCADE, related_name='progressos_aulas')
    aula = models.ForeignKey('Videoaula', on_delete=models.CASCADE)
    concluida = models.BooleanField(default=False)
    ultimo_acesso = models.DateTimeField(auto_now=True)

    class Meta:
        unique_together = ['aluno', 'aula']
        verbose_name = "Progresso de Aula"
        verbose_name_plural = "Progressos de Aulas"

    def __str__(self):
        status = "Concluída" if self.concluida else "Em andamento"
        return f"{self.aluno.nome} - {self.aula.titulo} ({status})"


# ==========================================
# NOVAS TABELAS: MOTOR DE TESTES/PROVAS
# ==========================================

class Pergunta(models.Model):
    atividade = models.ForeignKey(Atividade, on_delete=models.CASCADE, related_name='perguntas')
    
    # --- NOVIDADE AQUI: O cérebro da pergunta agora sabe de qual tipo ela é ---
    TIPO_PERGUNTA_CHOICES = (
        ('MULTIPLA', 'Múltipla Escolha'),
        ('ASSOC', 'Associação (Ligar Colunas)'),
    )
    tipo_pergunta = models.CharField(max_length=15, choices=TIPO_PERGUNTA_CHOICES, default='MULTIPLA', verbose_name="Tipo de Questão")
    
    enunciado = models.TextField(verbose_name="Enunciado da Questão")
    imagem_apoio = models.ImageField(upload_to="perguntas/", blank=True, null=True, verbose_name="Imagem de Apoio (Opcional)")
    ordem = models.PositiveIntegerField(default=1)

    class Meta:
        ordering = ['ordem']

    def __str__(self):
        return f"Q{self.ordem} ({self.get_tipo_pergunta_display()}): {self.enunciado[:50]}..."

class Alternativa(models.Model):
    pergunta = models.ForeignKey(Pergunta, on_delete=models.CASCADE, related_name='alternativas')
    texto = models.CharField(max_length=255, verbose_name="Texto da Alternativa")
    is_correta = models.BooleanField(default=False, verbose_name="É a resposta correta?")

    def __str__(self):
        return f"[{'X' if self.is_correta else ' '}] {self.texto}"

class RespostaAluno(models.Model):
    aluno = models.ForeignKey(Usuario, on_delete=models.CASCADE, related_name='respostas_atividades')
    pergunta = models.ForeignKey(Pergunta, on_delete=models.CASCADE)
    alternativa = models.ForeignKey(Alternativa, on_delete=models.CASCADE)
    data_resposta = models.DateTimeField(auto_now_add=True)

    class Meta:
        unique_together = ['aluno', 'pergunta']

    def __str__(self):
        return f"{self.aluno.nome} respondeu Q:{self.pergunta.id}"
    
# ==========================================
# MOTOR DE ASSOCIATIVIDADE (LIGAR COLUNAS)
# ==========================================

class ItemAssociacao(models.Model):
    # Funciona assim: O professor cadastra o par correto (ex: Coluna A "Sinal Árvore" -> Coluna B "Árvore")
    # Na hora da prova, o Django vai embaralhar a Coluna B sozinho.
    pergunta = models.ForeignKey(Pergunta, on_delete=models.CASCADE, related_name='itens_associacao')
    coluna_a = models.CharField(max_length=255, verbose_name="Item Esquerdo (Fixo)")
    coluna_b = models.CharField(max_length=255, verbose_name="Item Direito (Correspondente Correto)")

    def __str__(self):
        return f"{self.coluna_a} -> {self.coluna_b}"

class RespostaAssociacaoAluno(models.Model):
    # Guarda exatamente qual foi a ligação que o aluno fez
    aluno = models.ForeignKey(Usuario, on_delete=models.CASCADE, related_name='respostas_associacao')
    pergunta = models.ForeignKey(Pergunta, on_delete=models.CASCADE)
    item_a = models.ForeignKey(ItemAssociacao, on_delete=models.CASCADE)
    
    # O que ele escolheu na coluna B? (Vamos salvar em texto para comparar com a correta depois)
    resposta_aluno_coluna_b = models.CharField(max_length=255)
    data_resposta = models.DateTimeField(auto_now_add=True)

    class Meta:
        unique_together = ['aluno', 'item_a'] # Não deixa o aluno responder o mesmo item duas vezes

    def __str__(self):
        return f"{self.aluno.nome} ligou '{self.item_a.coluna_a}' com '{self.resposta_aluno_coluna_b}'"