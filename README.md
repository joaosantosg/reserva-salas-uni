# Reserva de Salas UNI

Sistema de reserva de salas para universidades, desenvolvido com FastAPI e arquitetura limpa.

## 🚀 Sobre o Projeto

O Reserva de Salas UNI é uma aplicação web para gerenciamento de reservas de salas em ambiente universitário. O sistema permite que usuários (professores, alunos, etc.) reservem salas para aulas, reuniões e outros eventos.

### Principais Funcionalidades

- Autenticação e autorização de usuários
- Gerenciamento de blocos e salas
- Reservas únicas e recorrentes
- Notificações por email
- Interface REST API
- Documentação automática com Swagger/OpenAPI

## 🏗️ Arquitetura

O projeto segue os princípios da Arquitetura Limpa (Clean Architecture) e utiliza:

- FastAPI para a API REST
- SQLAlchemy para ORM
- PostgreSQL como banco de dados
- Dependency Injection para injeção de dependências
- JWT para autenticação
- Pydantic para validação de dados

### Estrutura de Models

O sistema possui os seguintes modelos principais:

- `Usuario`: Gerenciamento de usuários do sistema
- `Bloco`: Representa um bloco de salas
- `Sala`: Representa uma sala específica
- `Reserva`: Gerenciamento de reservas únicas
- `ReservaRecorrente`: Gerenciamento de reservas recorrentes
- `Auditoria`: Registro de ações no sistema

## 🛠️ Requisitos

- Python 3.10+
- Poetry para gerenciamento de dependências
- Docker e Docker Compose (opcional)
- PostgreSQL 15+

## 🚀 Como Executar

### Usando Poetry

1. Instale as dependências:
```bash
poetry install
```

2. Configure as variáveis de ambiente:
```bash
cp .env.example .env
# Edite o arquivo .env com suas configurações
```

3. Inicie o servidor:
```bash
poetry run uvicorn app.main:app --reload
```

> **Nota**: Atualmente, as tabelas são criadas automaticamente ao iniciar a aplicação. Futuramente, quando o modelo de dados estiver totalmente definido, serão implementadas migrations com Alembic para um controle mais preciso das alterações do banco de dados.

### Usuário Inicial

Ao iniciar a aplicação pela primeira vez, um super usuário é criado automaticamente com as seguintes credenciais:
admin@admin.com
admin


### Usando Docker Compose

1. Configure as variáveis de ambiente:
```bash
cp .env.example .env
# Edite o arquivo .env com suas configurações
```

2. Inicie os containers:
```bash
docker-compose up -d
```

## 📝 Testes

### Testes Unitários

Execute os testes com cobertura:
```bash
# Executar testes com relatório de cobertura no terminal
poetry run pytest --cov=app --cov-report=term-missing

# Executar testes com relatório HTML
poetry run pytest --cov=app --cov-report=html
```

## 📝 Variáveis de Ambiente

Crie um arquivo `.env` baseado no `.env.example` com as seguintes variáveis:

```env
# Environment
ENV=dev

# Database
DB=postgresql
DB_USER=seu_usuario
DB_PASSWORD=sua_senha
DB_HOST=localhost
DB_PORT=5432
DB_NAME=nome_do_banco

# Auth
SECRET_KEY=sua_chave_secreta

# CORS
BACKEND_CORS_ORIGINS=["*"]

# Email (Mailgun)
MAILGUN_API_KEY=sua_chave_api
MAILGUN_DOMAIN=seu_dominio
```

## 📚 Documentação da API

Após iniciar o servidor, acesse:
- Swagger UI: http://localhost:8000/docs
- ReDoc: http://localhost:8000/redoc

## 📄 Docker



## 📄 Licença

Este projeto está sob a licença MIT. Veja o arquivo [LICENSE](LICENSE) para mais detalhes.

## ✅ Requisitos Atendidos

### 1. Cadastro de Blocos e Salas
- ✅ Endpoints `/api/v1/blocos` e `/api/v1/salas` para CRUD completo
- ✅ Validação de dados com Pydantic
- ✅ Associação entre blocos e salas com SQLAlchemy

### 2. Gerenciamento de Reservas
- ✅ Endpoint `/api/v1/reservas` para:
  - Criar reservas com todas as informações necessárias
  - Visualizar disponibilidade
  - Cancelar reservas
- ✅ Validação completa de dados e regras de negócio

### 3. Compartilhamento de Espaços
- ✅ Sistema de permissões flexível
- ✅ Validação de disponibilidade considerando restrições
- ✅ Regras configuráveis por sala

### 4. Conflitos de Agendamento
- ✅ Validação automática de conflitos de horário
- ✅ Sistema de reservas recorrentes implementado
- ✅ Tratamento de exceções para casos especiais

### 5. Notificações e Relatórios
- ✅ Sistema de notificações via email usando Mailgun
- ✅ Endpoints para relatórios de utilização
- ✅ Logs detalhados de todas as operações

### Bônus Implementados
- ✅ **REST API Completa**
  - Uso correto de verbos HTTP
  - Status codes apropriados
  - Documentação OpenAPI/Swagger

- ✅ **Banco de Dados Otimizado**
  - Modelagem eficiente com PostgreSQL
  - Índices otimizados
  - Relacionamentos bem definidos

- ✅ **Autenticação e Segurança**
  - JWT Authentication
  - Refresh tokens
  - Controle de acesso por papel

- ✅ **Testes Automatizados**
  - Testes unitários
  - Testes de integração
  - Cobertura de código

## 🌐 API Publicada

URL: [Em breve]

## Interface Web:
URL: 

## 💭 Considerações Finais

Este projeto foi bem divertido, adorei desenhar e modelar o sistema de reservas de salas. 
Embora, depois de começar o frontend, tenha percebido que faria várias coisas de maneira diferente, o desafio de backend realmente fez minha noite mais divertida. 
Foi um ótimo exercício que trouxe muito aprendizado e me deixou empolgado para continuar desenvolvendo!
Atualmente, estou trabalhando em um frontend para dar vida aos dados e tornar essa solução ainda mais incrível. Como estamos falando de uma POC (Prova de Conceito), o projeto está sempre evoluindo – o que você vê aqui provavelmente já passou por várias melhorias e novas funcionalidades desde que este texto foi escrito. Afinal, sempre que tenho um tempinho, estou lá ajustando e incrementando o código.
É claro, algumas das regras de negócio e validações podem ser bem diferentes do que os usuários realmente precisam. Em um cenário real, essas decisões seriam tomadas junto com os stakeholders antes de colocar as mãos no código. Mas a ideia por trás desse projeto é justamente mostrar como se pode construir algo técnico e bem organizado, sem perder o foco na escalabilidade.

No fim das contas, esse foi um projeto super divertido de desenvolver, que me permitiu explorar várias tecnologias modernas e aplicar boas práticas de desenvolvimento, tudo enquanto me divertia!

## 📝 Licença

Este projeto está sob a licença MIT. Veja o arquivo [LICENSE](LICENSE) para mais detalhes.
