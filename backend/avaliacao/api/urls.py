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

from django.urls import path

from . import views

urlpatterns = [
    path(
        "list/",
        views.AvaliacaoListView.as_view(),
        name="avaliacao-list",
    ),
    path(
        "detail/<int:pk>/",
        views.AvaliacaoDetailView.as_view(),
        name="avaliacao-detail",
    ),
    path(
        "calcular-notas/",
        views.CalcularNotasView.as_view(),
        name="calcular-notas",
    ),
    path(
        "notas-por-tecnico/",
        views.NotaPorTecnicoView.as_view(),
        name="notas-por-tecnico",
    ),
    path(
        "save/",
        views.CriarAvaliacaoCompletaView.as_view(),
        name="criar-avaliacao-save",
    ),
    path(
        "ranking-mensal/",
        views.RankingMensalView.as_view(),
        name="ranking-mensal",
    ),
    path(
        "ranking-anual/",
        views.RankingAnualView.as_view(),
        name="ranking-anual",
    ),
]
