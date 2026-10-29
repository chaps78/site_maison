from django.conf import settings
from django.conf.urls.static import static
from django.contrib import admin
from django.urls import include, path

urlpatterns = [
    path("admin/", admin.site.urls),
    path("", include("apps.core.urls")),
    path("recettes/", include("apps.recettes.urls")),
    path("calendrier/", include("apps.calendrier.urls")),
    path("taches/", include("apps.taches.urls")),
]

# En développement (runserver), Django sert lui-même les photos ; en production c'est nginx
# (cette fonction ne fait rien quand DEBUG est False).
urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
