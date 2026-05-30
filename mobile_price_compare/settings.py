from pathlib import Path
import os

BASE_DIR = Path(__file__).resolve().parent.parent

# =========================
# ENV FILE LOADER
# =========================
ENV_FILE = BASE_DIR / "nexovio.env"

# FOR PRODUCTION LATER:
# ENV_FILE = Path("/etc/nexovio.env")

if ENV_FILE.exists():
    with open(ENV_FILE) as f:
        for line in f:
            line = line.strip()

            if not line or line.startswith("#"):
                continue

            if "=" in line:
                key, value = line.split("=", 1)
                os.environ[key] = value


# =========================
# SECURITY
# =========================
SECRET_KEY = os.environ.get("SECRET_KEY")

DEBUG = os.environ.get(
    "DEBUG",
    "False"
).lower() == "true"

# DEBUG = False

ALLOWED_HOSTS = [
    host.strip()
    for host in os.environ.get(
        "ALLOWED_HOSTS",
        ""
    ).split(",")
    if host.strip()
]

# ALLOWED_HOSTS = [
#     "127.0.0.1",
#     "localhost",
# ]

CSRF_TRUSTED_ORIGINS = [
    origin.strip()
    for origin in os.environ.get(
        "CSRF_TRUSTED_ORIGINS",
        ""
    ).split(",")
    if origin.strip()
]


# =========================
# INSTALLED APPS
# =========================
INSTALLED_APPS = [
    "django.contrib.admin",
    "django.contrib.auth",
    "django.contrib.contenttypes",
    "django.contrib.sessions",
    "django.contrib.messages",
    "django.contrib.staticfiles",
    "mobiles",
    "users",
]


# =========================
# MIDDLEWARE
# =========================
MIDDLEWARE = [
    "django.middleware.security.SecurityMiddleware",
    "django.contrib.sessions.middleware.SessionMiddleware",
    "django.middleware.common.CommonMiddleware",
    "django.middleware.csrf.CsrfViewMiddleware",
    "django.contrib.auth.middleware.AuthenticationMiddleware",
    "django.contrib.messages.middleware.MessageMiddleware",
]


ROOT_URLCONF = "mobile_price_compare.urls"


# =========================
# TEMPLATES
# =========================
TEMPLATES = [
    {
        "BACKEND": "django.template.backends.django.DjangoTemplates",
        "DIRS": [BASE_DIR / "templates"],
        "APP_DIRS": True,
        "OPTIONS": {
            "context_processors": [
                "django.template.context_processors.debug",
                "django.template.context_processors.request",
                "django.contrib.auth.context_processors.auth",
                "django.contrib.messages.context_processors.messages",
                "mobiles.context_processors.wishlist_count",
            ],
        },
    },
]


WSGI_APPLICATION = "mobile_price_compare.wsgi.application"


# =========================
# DATABASE
# =========================
DATABASE_ENGINE = os.environ.get(
    "DATABASE_ENGINE",
    "django.db.backends.sqlite3"
)

DATABASE_NAME = os.environ.get(
    "DATABASE_NAME",
    "db.sqlite3"
)

DATABASES = {
    "default": {
        "ENGINE": DATABASE_ENGINE,
        "NAME": (
            BASE_DIR / DATABASE_NAME
            if DATABASE_ENGINE == "django.db.backends.sqlite3"
            else DATABASE_NAME
        ),
        "USER": os.environ.get("DATABASE_USER"),
        "PASSWORD": os.environ.get("DATABASE_PASSWORD"),
        "HOST": os.environ.get("DATABASE_HOST"),
        "PORT": os.environ.get("DATABASE_PORT"),
    }
}


# =========================
# STATIC
# =========================
STATIC_URL = "/static/"

STATICFILES_DIRS = [
    BASE_DIR / "static",
]

STATIC_ROOT = BASE_DIR / "staticfiles"


DEFAULT_AUTO_FIELD = "django.db.models.BigAutoField"


# =========================
# AUTH
# =========================
LOGIN_URL = "/login/"
LOGIN_REDIRECT_URL = "/"
LOGOUT_REDIRECT_URL = "/login/"


# =========================
# EMAIL
# =========================
EMAIL_BACKEND = "django.core.mail.backends.smtp.EmailBackend"
EMAIL_HOST = "smtp.gmail.com"
EMAIL_PORT = 587
EMAIL_USE_TLS = True

EMAIL_HOST_USER = os.environ.get("EMAIL_HOST_USER")
EMAIL_HOST_PASSWORD = os.environ.get("EMAIL_HOST_PASSWORD")
DEFAULT_FROM_EMAIL = os.environ.get("DEFAULT_FROM_EMAIL")
