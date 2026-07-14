"""
URL configuration for plataforma_libras project.

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/6.0/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""
from django.contrib import admin
from django.urls import path
from django.conf import settings
from django.conf.urls.static import static
from core.views import home, dashboard, detalhe_modulo, assistir_aula, responder_atividade, painel_pesquisador, exportar_dados_csv, gestao_modulos, criar_modulo, editar_modulo, excluir_modulo
from accounts.views import cadastro, fazer_login, sair, meu_perfil


urlpatterns = [
    path('admin/', admin.site.urls),
    path('', home, name='home'),
    path('cadastro/', cadastro, name='cadastro'),
    path('login/', fazer_login, name='login'),
    path('sair/', sair, name='sair'),
    path('dashboard/', dashboard, name='dashboard'),
    path('modulo/<int:modulo_id>/', detalhe_modulo, name='detalhe_modulo'),
    path('perfil/', meu_perfil, name='meu_perfil'),
    path('aula/<int:aula_id>/', assistir_aula, name='assistir_aula'),
    path('atividade/<int:atividade_id>/', responder_atividade, name='responder_atividade'),
    path('painel-pesquisador/', painel_pesquisador, name='painel_pesquisador'),
    path('exportar-dados-csv/', exportar_dados_csv, name='exportar_dados_csv'),
    path('gestao-modulos/', gestao_modulos, name='gestao_modulos'),
    path('criar-modulo/', criar_modulo, name='criar_modulo'),
    path('gestao/modulos/<int:modulo_id>/editar/', editar_modulo, name='editar_modulo'),
    path('gestao/modulos/<int:modulo_id>/excluir/', excluir_modulo, name='excluir_modulo'), 

]

if settings.DEBUG:
    urlpatterns += static(
        settings.MEDIA_URL,
        document_root=settings.MEDIA_ROOT
    )