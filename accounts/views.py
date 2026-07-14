from django.shortcuts import render, redirect
from django.contrib.auth import login, authenticate, logout
from django.contrib import messages
from .models import Escola, Usuario
from django.contrib.auth.decorators import login_required
from django.shortcuts import render


def cadastro(request):
    # Puxa as escolas para preencher o select
    escolas = Escola.objects.all().order_by('nome')
    
    # Se o usuário clicou no botão "Criar Conta" (método POST)
    if request.method == 'POST':
        nome = request.POST.get('nome')
        email = request.POST.get('email')
        escola_id = request.POST.get('escola')
        senha = request.POST.get('senha')
        confirmar_senha = request.POST.get('confirmar_senha')

        # 1. Validação: Verifica se as senhas são iguais
        if senha != confirmar_senha:
            messages.error(request, "As senhas não coincidem. Tente novamente.")
            return render(request, 'cadastro.html', {'escolas': escolas})
        
        # 2. Validação: Verifica se o e-mail já existe no banco
        if Usuario.objects.filter(email=email).exists():
            messages.error(request, "Este e-mail já está cadastrado. Faça login.")
            return render(request, 'cadastro.html', {'escolas': escolas})

        # 3. Busca a escola escolhida no banco
        escola_instancia = None
        if escola_id:
            escola_instancia = Escola.objects.get(id=escola_id)

        # 4. Cria o usuário no banco de dados
        try:
            user = Usuario.objects.create_user(
                username=email,  # No nosso sistema, o e-mail é o username
                email=email,
                password=senha,
                nome=nome,
                escola=escola_instancia,
                tipo='ESTUDANTE'
            )
            
            # 5. Loga o usuário automaticamente após o cadastro
            login(request, user)
            
            # 6. Redireciona para o dashboard ou para a página de TCLE
            return redirect('dashboard')
            
        except Exception as e:
            messages.error(request, f"Erro ao criar conta: {str(e)}")
            return render(request, 'cadastro.html', {'escolas': escolas})

    # Se for apenas um acesso normal à página (método GET), mostra o formulário vazio
    return render(request, 'cadastro.html', {'escolas': escolas})

def fazer_login(request):
    # Se o usuário já estiver logado e tentar acessar a página de login, manda pra Home
    if request.user.is_authenticated:
        return redirect('home')

    if request.method == 'POST':
        email = request.POST.get('email')
        senha = request.POST.get('senha')

        # O Django tenta encontrar o usuário com esse email e senha
        user = authenticate(request, username=email, password=senha)

        if user is not None:
            login(request, user)
            return redirect('dashboard') # Redireciona para o dashboard após login bem-sucedido
        else:
            messages.error(request, "E-mail ou senha incorretos. Tente novamente.")
            
    return render(request, 'login.html')

def sair(request):
    logout(request)
    return redirect('home')


@login_required(login_url='/login/')
def meu_perfil(request):
    return render(request, 'perfil.html')