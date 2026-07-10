from django.db import models
from django.conf import settings

class TCLE(models.Model):
    usuario = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='tcles')
    aceitou = models.BooleanField(default=False)
    data_aceite = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"TCLE - {self.usuario.nome} - {'Aceito' if self.aceitou else 'Pendente'}"