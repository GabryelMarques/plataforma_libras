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
    
    # Substituímos a URL pelo upload direto do arquivo
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

    def __str__(self):
        return self.titulo

class ProgressoAula(models.Model):
    # Quem é o aluno?
    aluno = models.ForeignKey(Usuario, on_delete=models.CASCADE, related_name='progressos_aulas')
    
    # Qual aula ele está assistindo?
    aula = models.ForeignKey('Videoaula', on_delete=models.CASCADE)
    
    # Ele terminou a aula?
    concluida = models.BooleanField(default=False)
    
    # Quando foi a última vez que ele mexeu nessa aula? (Isso alimenta o card "Continue de onde parou")
    ultimo_acesso = models.DateTimeField(auto_now=True)

    class Meta:
        # Garante que não teremos duas anotações da mesma aula para o mesmo aluno
        unique_together = ['aluno', 'aula']
        verbose_name = "Progresso de Aula"
        verbose_name_plural = "Progressos de Aulas"

    def __str__(self):
        status = "Concluída" if self.concluida else "Em andamento"
        return f"{self.aluno.nome} - {self.aula.titulo} ({status})"