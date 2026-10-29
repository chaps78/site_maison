"""Configuration Django, entièrement pilotée par l'environnement (voir .env.example)."""

from pathlib import Path

import environ
from django.core.exceptions import ImproperlyConfigured

BASE_DIR = Path(__file__).resolve().parent.parent

env = environ.Env()
# En local, on lit .env ; dans Docker, les variables viennent déjà de l'environnement
# (les vraies variables d'environnement l'emportent toujours sur le fichier).
if (BASE_DIR / ".env").exists():
    environ.Env.read_env(BASE_DIR / ".env")

# Pas de valeur par défaut : sans configuration, l'appli refuse de démarrer.
SECRET_KEY = env("SECRET_KEY")
DEBUG = env.bool("DEBUG")

if not DEBUG and SECRET_KEY.startswith("change-me"):
    raise ImproperlyConfigured("SECRET_KEY d'exemple avec DEBUG=False : en définir une vraie.")

ALLOWED_HOSTS = env.list("ALLOWED_HOSTS", default=[])
CSRF_TRUSTED_ORIGINS = env.list("CSRF_TRUSTED_ORIGINS", default=[])

# nginx termine le TLS et transmet le schéma d'origine dans cet en-tête.
SECURE_PROXY_SSL_HEADER = ("HTTP_X_FORWARDED_PROTO", "https")
if not DEBUG:
    SESSION_COOKIE_SECURE = True
    CSRF_COOKIE_SECURE = True


INSTALLED_APPS = [
    # Nos apps d'abord : leurs templates priment sur ceux de django.contrib.
    "apps.core",
    "apps.recettes",
    "apps.calendrier",
    "apps.taches",
    "django.contrib.admin",
    "django.contrib.auth",
    "django.contrib.contenttypes",
    "django.contrib.sessions",
    "django.contrib.messages",
    "django.contrib.staticfiles",
]

AUTH_USER_MODEL = "core.User"

LOGIN_URL = "core:connexion"
LOGIN_REDIRECT_URL = "core:accueil"
LOGOUT_REDIRECT_URL = "core:connexion"

MIDDLEWARE = [
    "django.middleware.security.SecurityMiddleware",
    "django.contrib.sessions.middleware.SessionMiddleware",
    "django.middleware.common.CommonMiddleware",
    "django.middleware.csrf.CsrfViewMiddleware",
    "django.contrib.auth.middleware.AuthenticationMiddleware",
    # Toutes les vues exigent une connexion par défaut (foyer partagé, pas d'inscription) ;
    # une vue s'en exempte explicitement avec @login_not_required (ex. l'écran de connexion).
    "django.contrib.auth.middleware.LoginRequiredMiddleware",
    "django.contrib.messages.middleware.MessageMiddleware",
    "django.middleware.clickjacking.XFrameOptionsMiddleware",
]

ROOT_URLCONF = "config.urls"

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
                # Alimente le menu latéral (core/base.html) avec les points du mois en cours.
                "apps.taches.context_processors.points_du_mois",
            ],
        },
    },
]

WSGI_APPLICATION = "config.wsgi.application"


# SQLite dans data/ (volume Docker). Plusieurs workers gunicorn écrivent dans la même
# base : le mode WAL permet les lectures pendant une écriture, IMMEDIATE prend le verrou
# d'écriture dès le début de la transaction (évite les « database is locked » en cours
# de route) et timeout laisse patienter 20 s avant d'échouer.
DATABASES = {
    "default": {
        "ENGINE": "django.db.backends.sqlite3",
        "NAME": BASE_DIR / "data" / "db.sqlite3",
        "OPTIONS": {
            "transaction_mode": "IMMEDIATE",
            "timeout": 20,
            "init_command": "PRAGMA journal_mode=WAL; PRAGMA synchronous=NORMAL;",
        },
    }
}


AUTH_PASSWORD_VALIDATORS = [
    {"NAME": "django.contrib.auth.password_validation.UserAttributeSimilarityValidator"},
    {"NAME": "django.contrib.auth.password_validation.MinimumLengthValidator"},
    {"NAME": "django.contrib.auth.password_validation.CommonPasswordValidator"},
    {"NAME": "django.contrib.auth.password_validation.NumericPasswordValidator"},
]


LANGUAGE_CODE = "fr-fr"
# Les datetimes sont stockés en UTC (USE_TZ) et affichés dans ce fuseau.
TIME_ZONE = "America/Argentina/Buenos_Aires"
USE_I18N = True
USE_TZ = True


# Sources dans apps/<app>/static/ ; collectstatic les copie dans STATIC_ROOT,
# dossier partagé avec nginx.
STATIC_URL = "static/"
STATIC_ROOT = BASE_DIR / "staticfiles"

# Photos envoyées par les utilisateurs, servies par nginx.
MEDIA_URL = "media/"
MEDIA_ROOT = BASE_DIR / "media"

DEFAULT_AUTO_FIELD = "django.db.models.BigAutoField"


# Par défaut Django n'écrit les erreurs 500 sur la console qu'en DEBUG ; on veut les
# voir dans `docker compose logs` en production aussi.
LOGGING = {
    "version": 1,
    "disable_existing_loggers": False,
    "handlers": {"console": {"class": "logging.StreamHandler"}},
    "root": {"handlers": ["console"], "level": "WARNING"},
}
