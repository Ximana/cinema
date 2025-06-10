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
cd cinema
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

# Base de dados
DATABASE_URL = "postgresql://xxxxxx"
```

5. **Aplique as migrações e rode o servidor**

```bash
python manage.py makemigrations
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
### Endpoints de Usuarios

| Método |                 Endpoint                      |            Descrição                                  |
| ------ | --------------------------------------------- | ---------------------------------------------------------------------- |
| POST   | /api/usuarios/registro/                       | Registro de usuário                                                    |
| POST   | /api/usuarios/login/                          | Login e obtenção de token                                              |
| POST   | /api/usuarios/logout/                         | Invalida o token do usuário                                            |
| GET    | /api/usuarios/meu-perfil/                     | Ver perfil do usuário                                                  |


### Endpoints de Filmes
| Método |                 Endpoint                      |            Descrição                                  |
| ------ | --------------------------------------------- | ---------------------------------------------------------------------- |
| GET    | /api/filmes/filmes/                           | Lista os filmes com sessões disponíveis                                |
| GET    | /api/filmes/filmes/{id}/                      | Retorna informações detalhadas de um filme                             |
| GET    | /api/filmes/filmes/{id}/sessoes/              | Retorna detalhes do filme com todas as suas sessões disponíveis        |
| GET    | /api/filmes/filmes/por-genero/{genero}/       | Lista filmes de um gênero específico                                   |
| GET    | /api/filmes/filmes/por-cinema/{cinema_id}/    | Lista filmes disponíveis em um cinema específico                       |
| GET    | /api/filmes/generos/                          | Retorna lista de gêneros de filmes com sessões disponíveis             |
| GET    | /api/filmes/filmes-com-sessoes/               | Lista simples de filmes com sessões disponíveis                        |


### Endpoints de Sessões e Reservas
| Método |                 Endpoint                      |            Descrição                                  |
| ------ | --------------------------------------------- | ---------------------------------------------------------------------- |
| GET    | /api/filmes/filmes-com-sessoes/               | Lista simples de filmes com sessões disponíveis                        |
| GET    | /api/reservas/minhas-reservas/                | Retorna todas as reservas do usuário, ordenadas por data (mais recentes|
| POST   | /api/reservas/minhas-reservas/                | Cria uma nova reserva para o usuário autenticado                       |
| GET    | /api/reservas/minhas-reservas/{id}/           | Retorna os detalhes completos de uma reserva específica                |
| POST   | /api/reservas/minhas-reservas/{id}/cancelar/  | Cancela uma reserva específica. Até 2 horas antes da sessão            |
| POST   | /api/reservas/minhas-reservas/{id}/confirmar/ | Confirma o pagamento de uma reserva pendente                           |
| DELETE | /api/reservas/minhas-reservas/{id}/           | Ver estatísticas das reservas                                          |
| GET    | /api/reservas/minhas-reservas/historico/      | Retorna o histórico completo de reservas com filtros opcionais         |



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
