# Reserva de Salas UNI

Sistema de reserva de salas para universidades, desenvolvido com FastAPI e arquitetura limpa.

*CODIGO NAO SERÁ MAIS ATUALIZADO NO REPO PÚBLICO*

Movido para [Reserva Salas API](https://joaosantosg@dev.azure.com/joaosantosg/reserva-salas-api/_git/reserva-salas-api)

## 🚀 Sobre o Projeto

O **Reserva de Salas UNI** é uma aplicação web para gerenciamento de reservas de salas em ambientes universitários.
O sistema permite que usuários, como professores e coordenadores, possam reservar salas para aulas, reuniões e outros eventos de forma simples e eficaz.

### Principais Funcionalidades

- Autenticação e autorização de usuários
- Gerenciamento de blocos e salas
- Reservas únicas e recorrentes
- Notificações por email
- Interface REST API
- Documentação automática com Swagger/OpenAPI

## 🏗️ Arquitetura

O projeto segue os princípios da Arquitetura Limpa (Clean Architecture) e utiliza:

- **FastAPI** para a API REST
- **SQLAlchemy** para ORM
- **PostgreSQL** como banco de dados
- **Dependency Injection** para injeção de dependências
- **JWT** para autenticação
- **Pydantic** para validação de dados

### Estrutura de Models

O sistema possui os seguintes modelos principais:

- `Usuario`: Gerenciamento de usuários do sistema
- `Bloco`: Representa um bloco de salas
- `Sala`: Representa uma sala específica
- `Reserva`: Gerenciamento de reservas únicas
- `ReservaRecorrente`: Gerenciamento de reservas recorrentes
- `Auditoria`: Registro de ações no sistema
- `Semestre`: Para registrar inicio e fim dos semestres e gerenciar as reservas semestrais

## 🛠️ Requisitos

- Python 3.10+
- Poetry para gerenciamento de dependências
- Docker e Docker Compose (opcional)
- PostgreSQL 15+
- **Mailgun**: Necessário para envio de notificações por email. Para usar este recurso, será necessário configurar a chave API e o domínio no Mailgun (veja a seção de variáveis de ambiente abaixo).

---

## 🎬 Como rodar esse bicho?  

### Com Poetry  

1️⃣ Instale as dependências:  
```bash
poetry install
```

2️⃣ Configure as variáveis de ambiente:  
```bash
cp .env.example .env
# Edite o arquivo .env com suas configurações
```

3️⃣ Inicie o servidor:  
```bash
poetry run uvicorn app.main:app --reload
```

💡 **Nota sobre o banco de dados:** Atualmente, as tabelas são criadas automaticamente, mas no futuro teremos migrations com **Alembic** para deixar tudo mais controlado.  

### Rodando com Docker Compose  

1️⃣ Configure as variáveis de ambiente:  
```bash
cp .env.example .env
# Edite o arquivo .env com suas configurações
```

2. Inicie os containers:
```bash
docker-compose up -d
```
---

## 🎭 Controle de Acesso  

- 🔒 **Usuários** (`/api/v1/usuarios/*`)  
  - Só superusuários podem mexer aqui.  
- 🔓 **Blocos, Salas e Reservas**  
  - Qualquer usuário autenticado pode acessar.  

💡 **Usuário inicial:**  
Ao rodar pela primeira vez, um superusuário é criado automaticamente:  
```text
Email: admin@admin.com  
Senha: admin  
Matrícula: 1234567890  
```

---

## 🧪 Testes (Porque Código Sem Teste é Código Suspeito)  

Para rodar os testes e conferir a cobertura:  

```bash
poetry run pytest --cov=app --cov-report=term-missing
```

Ou, se quiser um relatório HTML bonitão:  

```bash
poetry run pytest --cov=app --cov-report=html
```

---

## 📬 Notificações por E-mail  

Este sistema usa o **Mailgun** para enviar e-mails. Configure suas variáveis no `.env`:  

```env
MAILGUN_API_KEY=sua_chave_api  
MAILGUN_DOMAIN=seu_dominio  
```

---

## 📚 Documentação da API  

Acesse a documentação gerada automaticamente pelo **Swagger**:  
🔗 [Swagger UI](https://joaosantosg.github.io/reserva-salas-uni)  

Ou veja a interface web experimental:  
🔗 `https://redesigned-palm-tree-ten.vercel.app/`

---

## ✅ O que já está pronto?  

- **✔️ Cadastro de Blocos e Salas** – CRUD completo, validação e tudo mais  
- **✔️ Gerenciamento de Reservas** – criar, visualizar e cancelar reservas  
- **✔️ Controle de Conflitos** – nada de duas reservas no mesmo horário!  
- **✔️ Notificações e Logs** – e-mails automáticos e logs detalhados  
- **✔️ API REST bem feita** – com status codes corretos e documentação linda  
- **✔️ Segurança** – JWT, refresh tokens e controle de acesso  

---

## 🔜 Próximos Passos  

Agora, algumas coisinhas que ainda estão na lista (mas que eu ainda não tive paciência pra terminar kkk):  

- [ ] Bater **100% de cobertura de testes** (tem uns quebrados, mas eu chego lá)  
- [ ] Melhorar as **notificações** (talvez WebSockets, ao invés de só e-mail)  
- [ ] Criar um sistema de **aprovações** (tipo, alunos solicitam salas e coordenadores aprovam)  
- [ ] Implementar **SSO (Single Sign-On)**  
- [ ] Adicionar **recuperação de senha** (importante, né?)  

---

## 💡 Considerações Finais  

Esse projeto foi super divertido de desenvolver! 😃  

Depois de começar o frontend, percebi que mudaria várias coisas, mas tudo bem. O importante é que foi legal e um ótimo exercício.
O projeto continua evoluindo e, sempre que sobra um tempo, dou um jeito de melhorar algo.  
Claro, algumas regras podem ser ajustadas conforme o uso real. 
Mas o foco sempre foi mostrar como construir algo bem estruturado e escalável!  


---

## 📝 Licença  

Este projeto é open-source sob a **Licença MIT**, mas não pode ser usado para fins comerciais sem meu consentimento. Quer usar? Me chama antes! 🚀