# 🧬 Evolução em Libras - Plataforma Digital Educacional

![Status](<https://img.shields.io/badge/Status-Em%20Desenvolvimento-success>)
![Python](https://img.shields.io/badge/Python-3.x-3776AB?logo=python&logoColor=white)
![Django](https://img.shields.io/badge/Django-6.0-092E20?logo=django)
![Bootstrap](https://img.shields.io/badge/Bootstrap-5-7952B3?logo=bootstrap&logoColor=white)
![License](https://img.shields.io/badge/Licença-Acadêmica-blue)

---

# 📖 Sobre o Projeto

**Evolução em Libras** é uma plataforma digital educacional acessível desenvolvida como produto tecnológico de uma pesquisa de mestrado da **Universidade Federal do Tocantins (UFT)**.

A plataforma tem como objetivo apoiar o ensino de conceitos de **Evolução Biológica** para estudantes surdos do Ensino Fundamental e Médio, utilizando a **Língua Brasileira de Sinais (Libras)** como principal meio de comunicação.

Além do ambiente virtual de aprendizagem, o sistema também funciona como instrumento para coleta de dados científicos da pesquisa, permitindo a aplicação de avaliações diagnósticas e o acompanhamento do desempenho dos participantes durante todo o estudo.

---

# ✨ Funcionalidades

A plataforma foi projetada para seguir o fluxo metodológico da pesquisa.

### Área do Estudante

- Cadastro de usuário
- Login autenticado
- Aceite do TCLE (Termo de Consentimento Livre e Esclarecido)
- Realização do Pré-teste
- Acesso aos módulos de aprendizagem
- Videoaulas em Libras
- Atividades interativas
- Realização do Pós-teste
- Acompanhamento do progresso

### Área Administrativa

- Dashboard administrativo
- Cadastro de módulos
- Cadastro de videoaulas
- Cadastro de atividades
- Cadastro de testes
- Cadastro de questões
- Gerenciamento de usuários
- Gerenciamento de escolas
- Exportação dos dados da pesquisa

---

# 🛠️ Tecnologias Utilizadas

## Backend

- Python 3
- Django 6 (MVT)

## Banco de Dados

- SQLite (Desenvolvimento)
- PostgreSQL (Produção)

## Frontend

- HTML5
- CSS3
- Bootstrap 5
- JavaScript

## Bibliotecas

- Pillow
- Django Admin

## Versionamento

- Git
- GitHub

---

# 🚀 Como Executar o Projeto

## Pré-requisitos

- Python 3 instalado
- Git instalado

---

## 1. Clone o repositório

```bash
git clone https://github.com/GabryelMarques/plataforma_libras.git

cd plataforma_libras
```

---

## 2. Crie o ambiente virtual

### Windows

```bash
python -m venv venv
venv\Scripts\activate
```

### Linux / Mac

```bash
python3 -m venv venv
source venv/bin/activate
```

---

## 3. Instale as dependências

```bash
pip install -r requirements.txt
```

---

## 4. Execute as migrações

```bash
python manage.py makemigrations

python manage.py migrate
```

---

## 5. Crie um Superusuário

```bash
python manage.py createsuperuser
```

---

## 6. Execute o servidor

```bash
python manage.py runserver
```

Acesse:

```
http://127.0.0.1:8000/
```

Painel Administrativo:

```
http://127.0.0.1:8000/admin/
```

---

# 📁 Estrutura do Projeto

```
plataforma_libras/

├── accounts/
│   ├── models.py
│   ├── views.py
│   └── ...

├── core/
│   ├── models.py
│   ├── views.py
│   └── ...

├── modulos/
│   ├── models.py
│   ├── views.py
│   └── ...

├── atividades/
│   └── ...

├── avaliacoes/
│   └── ...

├── media/
│   ├── capas/
│   ├── thumbs/
│   └── videos/

├── static/
│   ├── css/
│   ├── js/
│   └── img/

├── templates/

├── requirements.txt

├── manage.py

└── db.sqlite3
```

---

# 🧩 Arquitetura

O sistema foi dividido em aplicativos independentes seguindo a arquitetura do Django.

## accounts

Responsável por:

- Usuários
- Login
- Cadastro
- Controle de permissões
- Escolas

---

## core

Responsável por:

- Página inicial
- Páginas institucionais
- Registro do TCLE

---

## modulos

Responsável por:

- Módulos
- Videoaulas
- Atividades

---

## atividades

Responsável pelas funcionalidades relacionadas às atividades propostas durante os módulos.

---

## avaliacoes

Responsável por:

- Pré-teste
- Pós-teste
- Questões
- Alternativas
- Tentativas
- Respostas

---

# 🎯 Fluxo da Pesquisa

O sistema segue o fluxo metodológico definido para a pesquisa.

```
Página Inicial

↓

Conheça o Projeto

↓

Cadastro

↓

Login

↓

Aceite do TCLE

↓

Pré-teste

↓

Módulo 1

↓

Atividade

↓

Módulo 2

↓

Atividade

↓

...

↓

Pós-teste

↓

Fim da Pesquisa
```

---

# 🎓 Contexto Acadêmico

Este projeto é desenvolvido como produto tecnológico vinculado ao Programa de Pós-Graduação em Ensino de Ciências e Matemática da Universidade Federal do Tocantins (UFT).

A plataforma será utilizada como instrumento de pesquisa para coleta de dados relacionados ao processo de aprendizagem de estudantes surdos, respeitando as diretrizes do Comitê de Ética em Pesquisa (CEP) e da legislação brasileira aplicável.

---

# 📄 Licença

Este projeto foi desenvolvido exclusivamente para fins acadêmicos.

Todos os direitos reservados aos autores.

---

# 👨‍💻 Autor

**Gabryel Soares Marques**

Curso de Ciência da Computação

Universidade Federal do Tocantins (UFT)

GitHub:

> https://github.com/GabryelMarques

---

## 🙏 Agradecimentos

- Universidade Federal do Tocantins (UFT)
- Programa de Pós-Graduação em Ensino de Ciências e Matemática
- Comunidade Django
- Comunidade Python
- Todos os colaboradores envolvidos no desenvolvimento da pesquisa
