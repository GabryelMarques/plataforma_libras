# 🧬 Evolução em Libras - Plataforma Digital Educacional

![Status](<https://img.shields.io/badge/Status-Em%20Desenvolvimento-success>)
![Django](https://img.shields.io/badge/Django-6.0-092E20?logo=django)
![Python](https://img.shields.io/badge/Python-3.x-3776AB?logo=python&logoColor=white)
![Bootstrap](https://img.shields.io/badge/Bootstrap-5-7952B3?logo=bootstrap&logoColor=white)

## 📖 Sobre o Projeto

A **Evolução em Libras** é uma plataforma digital acessível, desenvolvida como produto tecnológico educacional para uma pesquisa de mestrado da **Universidade Federal do Tocantins (UFT)**.

O sistema oferece um Ambiente Virtual de Aprendizagem (AVA) bilíngue, focado na comunidade surda, utilizando a Língua Brasileira de Sinais (Libras) como principal meio de instrução para o ensino de conceitos de Evolução Biológica. Além do viés educacional, a aplicação funciona como instrumento de pesquisa acadêmica para coleta estruturada de dados de aprendizagem.

## ✨ Principais Funcionalidades

A plataforma foi arquitetada com um fluxo restrito para garantir o rigor metodológico da pesquisa:

* **Autenticação Customizada:** Sistema de login/cadastro vinculado a instituições de ensino.
* **Gestão de Ética (TCLE):** Registro obrigatório do Termo de Consentimento Livre e Esclarecido.
* **Avaliações Diagnósticas e Formativas:** Aplicação de Pré-teste antes do acesso aos conteúdos e Pós-teste ao final.
* **Módulos de Aprendizagem:** Trilhas de conteúdo sequenciais contendo videoaulas em Libras (hospedagem própria) e atividades interativas.
* **Painel Administrativo:** Interface completa para cadastro de escolas, módulos, aulas, elaboração de testes e extração de métricas de respostas.

## 🛠️ Tecnologias Utilizadas

A stack foi escolhida visando estabilidade, segurança e facilidade de manutenção:

* **Backend:** Python & Django (Arquitetura MVT)
* **Banco de Dados:** SQLite (Desenvolvimento) / PostgreSQL (Produção)
* **Frontend:** HTML5, CSS3 Customizado, JavaScript e Bootstrap 5
* **Controle de Versão:** Git & GitHub

## 🚀 Como Executar o Projeto Localmente

Siga as instruções abaixo para clonar e rodar o projeto na sua máquina local para fins de desenvolvimento e teste.

### Pré-requisitos

* Python 3.x instalado.
* Git instalado.

### Passo a Passo

1. **Clone o repositório:**

```bash
git clone [https://github.com/GabryelMarques/plataforma_libras.git](https://github.com/GabryelMarques/plataforma_libras.git)
Acesse a pasta do projeto:

Bash
cd plataforma_libras
Crie e ative o ambiente virtual:

Windows:

Bash
python -m venv venv
venv\Scripts\activate
Linux/Mac:

Bash
python3 -m venv venv
source venv/bin/activate
Instale as dependências (Django e Pillow para imagens):

Bash
pip install django Pillow
Execute as migrações para criar o banco de dados local:

Bash
python manage.py makemigrations
python manage.py migrate
Crie um superusuário para acessar o painel administrativo:

Bash
python manage.py createsuperuser
Inicie o servidor de desenvolvimento:

Bash
python manage.py runserver
A aplicação estará disponível em http://127.0.0.1:8000/. Para acessar o painel de administração, vá até http://127.0.0.1:8000/admin/.

📁 Estrutura do Projeto
O sistema foi modularizado (Apps) para garantir uma arquitetura limpa:

accounts/: Gerenciamento de Usuários, Autenticação e cadastro de Escolas.

core/: Views principais (Home, Páginas institucionais) e modelo de registro do TCLE.

modulos/: Entidades de ensino (Módulos, Videoaulas e Atividades).

avaliacoes/: Modelagem estrutural do Pré-teste, Pós-teste, Questões e captação de Respostas/Tentativas.

🎓 Contexto Acadêmico
Desenvolvido no âmbito do Programa de Mestrado em Ensino de Ciências e Matemática (UFT). Toda a coleta de dados da plataforma é anonimizada e segue rigorosamente as diretrizes do Comitê de Ética em Pesquisa (CEP).

Projeto desenvolvido pela equipe de pesquisa UFT - 2026
```
