from django.db import models
from django.conf import settings

class TCLE(models.Model):
    usuario = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='tcles')
    aceitou = models.BooleanField(default=False)
    data_aceite = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"TCLE - {self.usuario.nome} - {'Aceito' if self.aceitou else 'Pendente'}"
    
from django.db import models

class ConfiguracaoSite(models.Model):
    video_apresentacao = models.FileField(
        upload_to='site_media/videos/', 
        blank=True, 
        null=True, 
        help_text="Faça o upload do vídeo principal (MP4)."
    )
    imagem_fundo = models.ImageField(
        upload_to='site_media/imagens/', 
        blank=True, 
        null=True, 
        help_text="Imagem de fundo da seção inicial."
    )
    
    # --- NOVO CAMPO ADICIONADO AQUI ---
    opacidade_fundo = models.FloatField(
        default=0.92,
        help_text="Transparência do branco sobre a imagem. Use valores de 0.0 (totalmente transparente) a 1.0 (totalmente branco). Ex: 0.92 ou 0.85"
    )

    class Meta:
        verbose_name = "Configuração do Site"
        verbose_name_plural = "Configurações do Site"

    def save(self, *args, **kwargs):
        # GARANTIA DE SINGLETON: Força a salvar sempre no ID 1. 
        self.pk = 1 
        super(ConfiguracaoSite, self).save(*args, **kwargs)

    def __str__(self):
        return "Configurações Globais (Capa e Vídeo)"