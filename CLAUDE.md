# Site maison

Application web de gestion de la maison, pour un seul foyer. Auto-hébergée sur un vieux
portable Ubuntu, accessible uniquement via Tailscale (HTTPS, certificats `tailscale cert`).

Le propriétaire est à l'aise en Python mais peu en JavaScript : garder le JS minimal,
explicite et commenté. Répondre et commenter en français.

## Stack (imposée : ne pas proposer d'alternative)

- Python 3.14 (image `python:3.14-slim`), Django 5.2 LTS (`>=5.2.8` pour Python 3.14)
- SQLite, fichier `data/db.sqlite3`
- Templates Django + HTMX pour l'interactivité ; FullCalendar uniquement pour la vue calendrier
- **Aucune chaîne de build JS** : ni npm, ni webpack, ni node. Les libs JS sont des fichiers
  statiques versionnés dans le dépôt
- gunicorn derrière nginx, le tout en docker compose
- pytest-django pour les tests, ruff pour le lint et le format

## Périmètre

- v1 : trois apps, `core`, `recettes`, `calendrier`
- Prévu plus tard : `courses`, `budget`, `taches` (l'architecture doit les accueillir sans refonte)
- Hors périmètre v1 : événements récurrents. Le champ `Evenement.rrule` existe mais n'est
  **pas utilisé** ; ne pas l'exploiter sans demande explicite

## Arborescence

```
config/            projet Django (settings.py unique, urls.py, wsgi.py)
apps/<app>/        une app par domaine : models, admin, views, urls, templates, static, tests
  templates/<app>/ templates namespacés par app
  static/<app>/    CSS/JS de l'app ; libs tierces dans static/<app>/vendor/<lib>-<version>/
  tests/           tests de l'app
docker/            entrypoint.sh, template nginx
data/  media/      volumes persistants (ignorés par git, sauf .gitkeep)
staticfiles/       sortie de collectstatic, partagée avec nginx (ignorée par git)
```

## Architecture

- **Foyer partagé** : tout le monde voit tout, pas de permissions fines. Les modèles de
  contenu héritent de `core.models.Traced` (`created_by`, `created_at`, `updated_at`).
  `created_by` est renseigné par les vues (et par l'admin via `TracedAdmin`) ; sa FK est en
  `SET_NULL` pour qu'effacer un compte n'efface pas ses données.
- **Utilisateur** : `core.User` (sous-classe vide de `AbstractUser`), à référencer par
  `settings.AUTH_USER_MODEL`. Auth Django standard ; les comptes sont créés à la main via
  l'admin, il n'y a pas d'inscription.
- **Ajouter une app** : `mkdir apps/<nom>` puis `python manage.py startapp <nom> apps/<nom>`,
  `name = "apps.<nom>"` dans son `AppConfig`, l'ajouter à `INSTALLED_APPS`. Le label reste `<nom>`.
- **Configuration** : uniquement par variables d'environnement (`django-environ`), lues dans
  `.env` (jamais versionné) ; `.env.example` est versionné et doit rester à jour. `SECRET_KEY` et
  `DEBUG` n'ont pas de valeur par défaut et ne sont jamais écrits en dur.
- **Fuseau horaire** : `TIME_ZONE = "America/Argentina/Buenos_Aires"`, `USE_TZ = True`. Les
  datetimes sont stockés en UTC et affichés en heure de Buenos Aires. Ne jamais utiliser de
  datetime naïf ni `datetime.now()` : utiliser `django.utils.timezone`. Pour filtrer « un jour
  local », `debut__date=...` convertit correctement ; ne pas comparer avec des dates UTC.
- **Statique** : les sources sont dans `apps/<app>/static/<app>/`. `collectstatic` copie tout
  dans `staticfiles/`, que nginx sert sur `/static/`. nginx sert aussi `/media/` (photos) sans
  passer par Django : elles ne sont donc pas protégées par le login (accès limité par Tailscale).
- **HTMX** : les vues qui répondent à HTMX renvoient un fragment (template préfixé `_`, ex.
  `_form.html`) quand l'en-tête `HX-Request` est présent, la page complète sinon. Le jeton CSRF
  est envoyé via `hx-headers` sur `<body>` dans `core/base.html`.
- **SQLite** : mode WAL et `transaction_mode = IMMEDIATE` (voir `DATABASES`) pour supporter
  plusieurs workers gunicorn.

## Conventions de code

- Vocabulaire du domaine **en français** : modèles, champs, URLs, noms de vues et de templates
  (`Recette`, `temps_preparation`, `liste_recettes`). Pas d'accents dans les identifiants ;
  accents dans les `verbose_name`, textes et commentaires. Les noms techniques Django/Python
  restent standards (`get_queryset`, `Meta`, `save`).
- Commentaires et docstrings en français, courts, qui expliquent le *pourquoi*.
- Chaque app déclare `app_name` dans ses `urls.py` ; noms d'URL de la forme `recettes:liste`.
- Ruff : `ruff check .` et `ruff format .` doivent passer avant un commit.
- Tests : pytest-django, dans `apps/<app>/tests/`, fixtures partagées dans `conftest.py`.
  Toute logique de dates/fuseaux est couverte (voir `apps/calendrier/tests/test_fuseau.py`).
- Migrations : toujours committées ; `python manage.py makemigrations --check --dry-run` doit
  être vide avant un commit.
- Dépendances : `requirements.txt` (prod, versions épinglées) et `requirements-dev.txt`.

## Commandes utiles

Développement local (Python 3.14 ; nécessite le paquet `python3.14-venv` sur Ubuntu) :

```
python3 -m venv .venv && source .venv/bin/activate
pip install -r requirements-dev.txt
cp .env.example .env               # puis adapter si besoin
python manage.py migrate
python manage.py createsuperuser
python manage.py runserver

pytest                             # tous les tests
pytest apps/calendrier -k fuseau   # un sous-ensemble
ruff check . && ruff format .
python manage.py makemigrations --check --dry-run
```

Production (sur le portable) :

```
docker compose up -d --build       # construit et démarre web + nginx
docker compose logs -f web
docker compose exec web python manage.py createsuperuser
docker compose exec nginx nginx -s reload      # après renouvellement des certificats
```

Certificats TLS (à renouveler avant ~90 jours, idéalement par cron sur l'hôte) :

```
sudo tailscale cert --cert-file "$CERTS_DIR/$TAILSCALE_HOSTNAME.crt" \
                    --key-file  "$CERTS_DIR/$TAILSCALE_HOSTNAME.key" "$TAILSCALE_HOSTNAME"
```

Sauvegarde : ne **pas** copier `data/db.sqlite3` à chaud (mode WAL). Utiliser :

```
sqlite3 data/db.sqlite3 ".backup '/chemin/vers/sauvegarde.sqlite3'"
```

et sauvegarder `media/` avec un simple `rsync`.

## Git

- Branche `main`, remote `origin` en SSH (`git@github.com:chaps78/site_maison.git`).
- Messages de commit en français, à l'impératif, courts. Un commit = un changement cohérent.
- Ne jamais committer `.env`, `data/`, `media/`, `staticfiles/`.
- Ne committer ou pousser que sur demande explicite ; jamais de `push --force`.

## Pièges connus

- Bind mounts : le conteneur tourne avec `APP_UID`/`APP_GID` (voir `.env`), qui doivent
  correspondre à l'utilisateur propriétaire de `data/` et `media/`, sinon SQLite ne peut pas écrire.
- Événements « journée entière » : FullCalendar attend des dates, la base stocke des datetimes.
  Convention à respecter partout : début à 00:00 heure locale, fin = début du jour suivant.
- `CSRF_TRUSTED_ORIGINS` doit contenir l'origine HTTPS complète (`https://<hôte>.ts.net`),
  sinon tous les formulaires POST sont refusés derrière nginx.
