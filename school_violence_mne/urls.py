from django.contrib import admin
from django.urls import path, include
from django.conf import settings
from django.conf.urls.static import static
from django.contrib.auth.decorators import login_required
from school_violence_mne import views  # import your home view

urlpatterns = [
    path("admin/", admin.site.urls),

    # Root URL shows dashboard, requires login
    path("", login_required(views.home), name="home"),

    path("data/", include("data_collection.urls")),
    path("indicators/", include("indicators.urls")),
    path("visualization/", include("visualization.urls")),
    path("reports/", include("reports.urls")),
    path("settings/", include("settings.urls")),

    # Django’s built-in login/logout/password reset views
    path("accounts/", include("django.contrib.auth.urls")),
]

if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
