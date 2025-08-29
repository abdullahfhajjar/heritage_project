# heritage_site/urls.py
from django.contrib import admin
from django.urls import path, include
from django.conf import settings
from django.conf.urls.static import static
from django.views.generic import RedirectView  # ← add this
from archive.admin_site import admin_site

urlpatterns = [
    # i18n (language switching)
    path("i18n/", include("django.conf.urls.i18n")),

    # Admin - using custom Turath admin site
    path("admin/", admin_site.urls),
    # Keep default admin as fallback
    path("admin-default/", admin.site.urls),

    # ✅ Force /accounts/login/ to use Google OAuth (no local form)
    path("accounts/login/", RedirectView.as_view(url="/accounts/google/login/", permanent=False)),

    # allauth URLs (must come after the override above)
    path("accounts/", include("allauth.urls")),

    # Your app routes
    path("", include("archive.urls")),
]

# media in dev
if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)