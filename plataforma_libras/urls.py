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
from accounts.views import cadastro, fazer_login, sair, meu_perfil
from core.views import home, dashboard, detalhe_modulo, assistir_aula, responder_atividade, painel_pesquisador, exportar_dados_csv, gestao_modulos, criar_modulo, editar_modulo, excluir_modulo
from core.views import gestao_videoaulas, criar_videoaula, editar_videoaula, excluir_videoaula, gestao_atividades
from core.views import criar_atividade, editar_atividade, excluir_atividade, gerenciar_perguntas
from core.views import criar_pergunta, configurar_pergunta, excluir_alternativa, excluir_item_associacao
from core.views import editar_pergunta, excluir_pergunta, busca_global_ajax, detalhe_participante



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
    path('pesquisa/exportar/csv/', exportar_dados_csv, name='exportar_dados_csv'),
    path('gestao-modulos/', gestao_modulos, name='gestao_modulos'),
    path('criar-modulo/', criar_modulo, name='criar_modulo'),
    path('gestao/modulos/<int:modulo_id>/editar/', editar_modulo, name='editar_modulo'),
    path('gestao/modulos/<int:modulo_id>/excluir/', excluir_modulo, name='excluir_modulo'), 
    path('gestao/videoaulas/', gestao_videoaulas, name='gestao_videoaulas'),        
    path('criar-videoaula/', criar_videoaula, name='criar_videoaula'),
    path('gestao/videoaulas/<int:aula_id>/editar/', editar_videoaula, name='editar_videoaula'),
    path('gestao/videoaulas/<int:aula_id>/excluir/', excluir_videoaula, name='excluir_videoaula'),
    path('gestao/atividades/', gestao_atividades, name='gestao_atividades'),
    path('criar-atividade/', criar_atividade, name='criar_atividade'),
    path('gestao/atividades/<int:atividade_id>/editar/', editar_atividade, name='editar_atividade'),
    path('gestao/atividades/<int:atividade_id>/excluir/', excluir_atividade, name='excluir_atividade'),
    path('gestao/atividades/<int:atividade_id>/perguntas/', gerenciar_perguntas, name='gerenciar_perguntas'),
    path('gestao/atividades/<int:atividade_id>/perguntas/nova/<str:tipo>/', criar_pergunta, name='criar_pergunta'),
    path('gestao/perguntas/<int:pergunta_id>/configurar/', configurar_pergunta, name='configurar_pergunta'),
    path('gestao/alternativas/<int:alternativa_id>/excluir/', excluir_alternativa, name='excluir_alternativa'),
    path('gestao/associacoes/<int:item_id>/excluir/', excluir_item_associacao, name='excluir_item_associacao'),
    path('gestao/perguntas/<int:pergunta_id>/editar/', editar_pergunta, name='editar_pergunta'),
    path('gestao/perguntas/<int:pergunta_id>/excluir/', excluir_pergunta, name='excluir_pergunta'),
    path('pesquisa/ajax/', busca_global_ajax, name='busca_global_ajax'),
    path('pesquisa/participante/<int:aluno_id>/', detalhe_participante, name='detalhe_participante'),
]

if settings.DEBUG:
    urlpatterns += static(
        settings.MEDIA_URL,
        document_root=settings.MEDIA_ROOT
    )