from django.db import models

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