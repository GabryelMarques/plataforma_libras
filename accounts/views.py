from django.shortcuts import render, redirect
from django.contrib.auth import login
from django.contrib import messages
from .models import Escola, Usuario

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
            
            # 6. Redireciona para a Home (ou futuramente para a página do TCLE)
            return redirect('home')
            
        except Exception as e:
            messages.error(request, f"Erro ao criar conta: {str(e)}")
            return render(request, 'cadastro.html', {'escolas': escolas})

    # Se for apenas um acesso normal à página (método GET), mostra o formulário vazio
    return render(request, 'cadastro.html', {'escolas': escolas})