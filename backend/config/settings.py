
"""Configurações principais do backend.

Este módulo centraliza as configurações do Django e do Django REST
Framework, incluindo variáveis de ambiente, segurança, aplicações,
middlewares, banco de dados, idioma e fuso horário.
"""

import os
from pathlib import Path

from django.core.exceptions import ImproperlyConfigured
from dotenv import load_dotenv

# Diretório raiz do backend, utilizado para localizar arquivos do projeto.
BASE_DIR = Path(__file__).resolve().parent.parent

# Carrega as variáveis de ambiente definidas no arquivo .env.
load_dotenv(BASE_DIR / ".env")


def env_bool(name: str, default: bool = False) -> bool:
    """Obtém uma variável de ambiente e a converte para booleano.

    Args:
        name: Nome da variável de ambiente.
        default: Valor utilizado quando a variável não estiver definida.

    Returns:
        True quando o valor for "1", "true" ou "yes", ignorando
        diferenças entre maiúsculas e minúsculas. False nos demais casos.
    """
    return os.environ.get(name, str(default)).strip().lower() in ("1", "true", "yes")


def env_list(name: str, default: str = "") -> list[str]:
    """Obtém uma variável de ambiente como lista de strings.

    Os valores devem estar separados por vírgulas. Espaços extras
    e elementos vazios são removidos.

    Args:
        name: Nome da variável de ambiente.
        default: Valor utilizado quando a variável não estiver definida.

    Returns:
        Lista de strings obtidas a partir da variável de ambiente.
    """
    return [item.strip() for item in os.environ.get(name, default).split(",") if item.strip()]


# Ativa ou desativa o modo de depuração. Por padrão, permanece desativado.
DEBUG = env_bool("DEBUG", False)

# Chave utilizada pelo Django em mecanismos de segurança e assinatura.
# Em desenvolvimento, permite uma chave fixa caso DEBUG esteja ativado.
# Fora desse modo, exige que SECRET_KEY esteja definida no ambiente.
SECRET_KEY = os.environ.get("SECRET_KEY")
if not SECRET_KEY:
    if DEBUG:
        SECRET_KEY = "insecure-dev-key-apenas-para-desenvolvimento"
    else:
        raise ImproperlyConfigured("Defina a variável de ambiente SECRET_KEY.")

# Define os hosts autorizados a acessar a aplicação.
ALLOWED_HOSTS = env_list("ALLOWED_HOSTS", "localhost,127.0.0.1")

# Registra os aplicativos nativos do Django e o Django REST Framework.
INSTALLED_APPS = [
    "django.contrib.admin",
    "django.contrib.auth",
    "django.contrib.contenttypes",
    "django.contrib.sessions",
    "django.contrib.messages",
    "django.contrib.staticfiles",
    "rest_framework",
]

# Define os middlewares responsáveis pelo processamento das requisições,
# incluindo segurança, sessões, autenticação e proteção contra CSRF.
MIDDLEWARE = [
    "django.middleware.security.SecurityMiddleware",
    "django.contrib.sessions.middleware.SessionMiddleware",
    "django.middleware.common.CommonMiddleware",
    "django.middleware.csrf.CsrfViewMiddleware",
    "django.contrib.auth.middleware.AuthenticationMiddleware",
    "django.contrib.messages.middleware.MessageMiddleware",
    "django.middleware.clickjacking.XFrameOptionsMiddleware",
]

# Indica o módulo responsável pelas rotas principais do backend.
ROOT_URLCONF = "config.urls"

# Configura o mecanismo de templates utilizado pelo Django,
# incluindo os templates da interface administrativa.
TEMPLATES = [
    {
        "BACKEND": "django.template.backends.django.DjangoTemplates",
        "DIRS": [],
        "APP_DIRS": True,
        "OPTIONS": {
            "context_processors": [
                "django.template.context_processors.request",
                "django.contrib.auth.context_processors.auth",
                "django.contrib.messages.context_processors.messages",
            ],
        },
    },
]

# Define a aplicação WSGI utilizada para servir o projeto.
WSGI_APPLICATION = "config.wsgi.application"

# Configura o SQLite como banco de dados padrão do projeto.
DATABASES = {
    "default": {
        "ENGINE": "django.db.backends.sqlite3",
        "NAME": BASE_DIR / "db.sqlite3",
    }
}

# Estabelece regras de validação de senhas dos usuários Django,
# verificando similaridade, tamanho mínimo e senhas comuns ou numéricas.
AUTH_PASSWORD_VALIDATORS = [
    {"NAME": "django.contrib.auth.password_validation.UserAttributeSimilarityValidator"},
    {"NAME": "django.contrib.auth.password_validation.MinimumLengthValidator"},
    {"NAME": "django.contrib.auth.password_validation.CommonPasswordValidator"},
    {"NAME": "django.contrib.auth.password_validation.NumericPasswordValidator"},
]

# Define o idioma padrão da aplicação como português brasileiro.
LANGUAGE_CODE = "pt-br"

# Define o fuso horário utilizado pelo sistema.
TIME_ZONE = "America/Sao_Paulo"

# Habilita os recursos de internacionalização do Django.
USE_I18N = True

# Armazena datas e horários com suporte a fuso horário.
USE_TZ = True

# Define o caminho base dos arquivos estáticos da aplicação.
STATIC_URL = "static/"

# Utiliza identificadores inteiros de 64 bits como chave primária
# automática nos modelos que não definirem explicitamente um campo ID.
DEFAULT_AUTO_FIELD = "django.db.models.BigAutoField"
