from django.test import TestCase
from django.urls import reverse

from modulos.models import Modulo


class HomeViewTests(TestCase):
    def test_home_shows_placeholder_when_cover_file_is_missing(self):
        Modulo.objects.create(
            titulo="Módulo teste",
            descricao="Descrição de teste",
            ordem=1,
            imagem_capa="capas/arquivo-nao-existe.jpg",
        )

        response = self.client.get(reverse("home"))

        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "bi-image")
        self.assertNotContains(response, "/media/capas/arquivo-nao-existe.jpg")
