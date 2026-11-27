# Trabalho Prático - Gerenciamento de Projeto de Software 
## Sistema Web para Agendamento de Quadras de Tênis
Planejamento e acompanhamento do desenvolvimento de um sistema web em Flutter para agendamento de quadras de tênis. Organização da Estrutura Analítica do Projeto (EAP) em entregas e pacotes de trabalho, contemplando documentação, desenvolvimento, testes e entrega final.

## Backend — Django REST Framework

O backend do GPS utiliza Python 3.12, Django 5.2 LTS,
Django REST Framework e SQLite para desenvolvimento.

### 1. Criar o ambiente virtual

Na raiz do projeto:

```powershell
py -3.12 -m venv backend\.venv
```

### 2. Ativar o ambiente virtual

```powershell
.\backend\.venv\Scripts\Activate.ps1
```

### 3. Instalar as dependências

```powershell
python -m pip install -r backend\requirements.txt
```

### 4. Configurar as variáveis de ambiente

```powershell
Copy-Item backend\.env.example backend\.env
```

Gere uma chave secreta:

```powershell
python -c "from django.core.management.utils import get_random_secret_key; print(get_random_secret_key())"
```

Substitua o valor de `SECRET_KEY` no arquivo `backend/.env`
pela chave gerada.

O arquivo `.env` é local e não deve ser enviado ao GitHub.

### 5. Preparar o banco de dados

```powershell
cd backend
python manage.py check
python manage.py migrate
```

O SQLite será criado localmente. O arquivo `db.sqlite3`
não deve ser versionado.

### 6. Executar os testes

```powershell
python manage.py test
```

### 7. Iniciar o servidor

```powershell
python manage.py runserver
```

Servidor: http://127.0.0.1:8000/

Administração: http://127.0.0.1:8000/admin/

Para encerrar, pressione Ctrl+C.

O servidor `runserver` deve ser utilizado apenas
para desenvolvimento.
