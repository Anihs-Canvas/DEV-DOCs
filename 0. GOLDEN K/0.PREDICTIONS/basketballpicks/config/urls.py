"""Root URL configuration [bball-01 §1].

Read-only dashboard pages at the site root and the token-authed /api/v1/
surface. Admin keeps the write paths. The api/dashboard url modules are
STUBS owned by later agents — they ship with empty urlpatterns so this
include() wiring resolves and the project runs from day one.
"""

from django.conf import settings
from django.contrib import admin
from django.urls import include, path, re_path

urlpatterns = [
    path("admin/", admin.site.urls),
    path("api/v1/", include("apps.api.urls")),
    path("", include("apps.dashboard.urls")),
]

if settings.DEBUG:
    # Finders-based static serving in DEBUG — also under gunicorn (the compose
    # quickstart), where runserver's automatic handler does not exist.
    from django.contrib.staticfiles import views as staticfiles_views

    urlpatterns += [re_path(r"^static/(?P<path>.*)$", staticfiles_views.serve)]
