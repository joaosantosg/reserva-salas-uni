# 🎓 Reserva de Salas UNI  

Um sistema de reservas de salas universitárias feito com **FastAPI**, uma pitada de organização e talvez mais alguma coisa

---

## 🚀 O que é isso?  

O **Reserva de Salas UNI** é um sistema web que ajuda professores, coordenadores e afins a garantirem um espacinho na universidade sem precisar sair caçando uma sala vazia pelo campus. A ideia é simples: você reserva, usa e pronto! Nada de conflitos, bagunça ou salas ocupadas sem avisar.  

### 📌 O que dá pra fazer?  

- 🔑 **Autenticação e autorização** – porque segurança é coisa séria!  
- 🏫 **Gerenciar blocos e salas** – tudo organizadinho, como deve ser.  
- 📆 **Criar reservas únicas e recorrentes** – sem precisar preencher tudo de novo toda semana.  
- ✉️ **Receber notificações por e-mail** – "Ei, você tem uma sala reservada amanhã!"  
- 📡 **Consumir uma API REST bem feita** – com **Swagger/OpenAPI** de brinde!  

---

## 🏗️ Arquitetura: Porque Código Bonito é Código Feliz  

Esse projeto segue a **Arquitetura Limpa (Clean Architecture)**. Ou seja, nada de código confuso e desorganizado.  

**Tecnologias envolvidas:**  

- 🚀 **FastAPI** para a API REST  
- 🏗 **SQLAlchemy** para o ORM  
- 🗄 **PostgreSQL** como banco de dados  
- 📦 **Dependency Injection** para facilitar a vida  
- 🔐 **JWT** para autenticação  
- ✅ **Pydantic** para validar os dados  

---

## 📂 Modelos do Sistema  

Dando nome aos bois, aqui estão os principais modelos do sistema:  

- 👤 `Usuario`: Gerencia usuários do sistema  
- 🏢 `Bloco`: Representa um bloco de salas  
- 🚪 `Sala`: Representa uma sala específica  
- 📆 `Reserva`: Para quem precisa de uma sala em um horário único  
- 🔁 `ReservaRecorrente`: Para quem precisa sempre da mesma sala  
- 🕵️ `Auditoria`: Para manter um histórico de tudo que acontece  

---

## 🛠️ O que você precisa para rodar isso?  

- Python 3.10+  
- **Poetry** para gerenciar as dependências  
- Docker e Docker Compose (opcional, mas recomendado)  
- PostgreSQL 15+  
- Uma conta no **Mailgun** (caso queira receber e-mails do sistema)  

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

2️⃣ Suba os containers:  
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