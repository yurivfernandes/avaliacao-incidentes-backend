"""
URL configuration for backend project.

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/4.2/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""

from django.conf import settings
from django.conf.urls.static import static
from django.contrib import admin
from django.urls import include, path
from django.views.static import serve

urlpatterns = [
    path("admin/", admin.site.urls),
    path("api/access/", include("access.api.urls")),
    path("api/cadastro/", include("cadastro.api.urls")),
    path("api/dw_analytics/", include("dw_analytics.api.urls")),
    path("api/premissas/", include("premissas.api.urls")),
    path("api/service_now/", include("service_now.api.urls")),
    path("api/avaliacao/", include("avaliacao.api.urls")),
    path(
        "api/docs/<path:path>",
        serve,
        {
            "document_root": settings.MKDOCS_BUILD_DIR,
        },
    ),
    path(
        "api/docs/",
        serve,
        {"document_root": settings.MKDOCS_BUILD_DIR, "path": "index.html"},
    ),
] + static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)
