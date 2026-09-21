FROM python:3.14-slim

ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    PIP_NO_CACHE_DIR=1 \
    PIP_DISABLE_PIP_VERSION_CHECK=1 \
    WEB_CONCURRENCY=3

# Utilisateur non-root, avec le même UID/GID que l'utilisateur de l'hôte pour pouvoir
# écrire dans les bind mounts data/ et media/.
ARG APP_UID=1000
ARG APP_GID=1000
RUN groupadd --gid ${APP_GID} app \
    && useradd --uid ${APP_UID} --gid ${APP_GID} --no-create-home --shell /usr/sbin/nologin app

WORKDIR /app

# Dépendances d'abord : cette couche n'est reconstruite que si requirements.txt change.
COPY requirements.txt .
RUN pip install -r requirements.txt

COPY . .

# staticfiles/ est un volume nommé partagé avec nginx : le créer ici avec le bon
# propriétaire fait que Docker l'initialise avec ces droits au premier démarrage.
RUN mkdir -p data media staticfiles && chown app:app data media staticfiles

USER app

EXPOSE 8000

# `sh` plutôt que l'exécution directe : ne dépend pas du bit exécutable dans git.
ENTRYPOINT ["sh", "docker/entrypoint.sh"]
# Le nombre de workers vient de WEB_CONCURRENCY (lu nativement par gunicorn).
CMD ["gunicorn", "config.wsgi:application", "--bind", "0.0.0.0:8000", "--access-logfile", "-"]
