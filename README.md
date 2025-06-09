# Sistema de Gerenciamento de Cinema

Projeto web desenvolvido com **Django** e banco de dados **PostgreSQL** (hospedado na plataforma [Neon](https://neon.tech)) e arquivos de media armazenados no Cloudinary, com funcionalidades completas para gerenciamento de **usuários**, **reservas**, **emissão de bilhetes**, **gestão de filmes.** e **sessões** do cinema Inclui também uma interface de dashboard para administradores.


## Funcionalidades Principais

- Autenticação e registro de usuários (com token)
- Diferenciação entre usuários regulares e administradores
- CRUD completo de reservas
- Painel administrativo para gestão de reservas, usuários, filmes e sessões de filmes
- API RESTful documentada
- Suporte a filtros, atualização de status e estatísticas de reservas e sessões
- Conexão segura com banco PostgreSQL remoto via Neon
- armazenamento seguro no Cloudinary


## 🛠️ Tecnologias Utilizadas

- [Python 3.11+](https://www.python.org/)
- [Django 4.x](https://www.djangoproject.com/)
- [PostgreSQL](https://www.postgresql.org/) (via [Neon](https://neon.tech))
- [Django REST Framework](https://www.django-rest-framework.org/)
- Token Authentication
- HTML/CSS/JAVASCRIPT para o painel 



## 🧪 Instalação Local (Desenvolvimento)

1. **Clone o projeto**

```bash
git clone https://github.com/ximana/cinema.git
cd seu-repositorio
````

2. **Crie um ambiente virtual e ative**

```bash
python -m venv venv
source venv/bin/activate  # Linux/macOS
venv\Scripts\activate     # Windows
```

3. **Instale as dependências**

```bash
pip install -r requirements.txt
```

4. **Configure variáveis de ambiente**

Crie um arquivo `.env` na raiz com os dados da sua base Neon:

```env
# Cloudinary Configuration
CLOUDINARY_CLOUD_NAME=xxxxx
CLOUDINARY_API_KEY=xxxxxx
CLOUDINARY_API_SECRET=xxxxxx

# Django Configuration
SECRET_KEY=sua_secret_key_aqui
DEBUG=True
ALLOWED_HOSTS=localhost,127.0.0.1

# Base de dados
DATABASE_URL = "postgresql://xxxxxx"
```

5. **Aplique as migrações e rode o servidor**

```bash
python manage.py migrate
python manage.py runserver
```

---

## Autenticação

A API utiliza **Token Authentication**. Após o login, inclua o token no cabeçalho de todas as requisições autenticadas:

```
Authorization: Token seu_token_aqui
```

---

## Endpoints da API

Alguns endpoints disponíveis:

| Método | Endpoint                             | Descrição                     |
| ------ | ------------------------------------ | ----------------------------- |
| POST   | /api/usuarios/registro/              | Registro de usuário           |
| POST   | /api/usuarios/login/                 | Login e obtenção de token     |
| GET    | /api/usuarios/meu-perfil/            | Ver perfil do usuário         |
| POST   | /api/reservas/reservas/              | Criar nova reserva            |
| GET    | /api/reservas/reservas/              | Listar reservas do usuário    |
| PATCH  | /api/reservas/{id}/update\_status/   | Atualizar status da reserva   |
| GET    | /api/reservas/reservas/estatisticas/ | Ver estatísticas das reservas |



## Dashboard Admin

O sistema possui uma interface de dashboard para administração de usuários, reservas, filmes e sessões,  acessível para usuários com permissão de administrador.



## Permissões

* **Usuário regular**: pode registrar-se, autenticar, gerenciar seu perfil e suas reservas.
* **Administrador**: acesso completo a todos os dados, estatísticas e funcionalidades do painel.

---

## Notas Finais

* Tokens não expiram automaticamente, mas podem ser revogados via logout.
* O sistema segue boas práticas RESTful e validações de entrada.
* O projeto está em constante evolução. Contribuições são bem-vindas!


## Versão

* **v1.0**
* Última atualização: **Junho de 2025**



## Licença

Este projeto está sob a licença [MIT](LICENSE).


---
