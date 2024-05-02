"""
URL configuration for ProjectReinoCatalina project.

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/5.0/topics/http/urls/
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
from django.contrib import admin
from django.urls import path
from .BackEnd import views
from django.conf.urls.static import static
from django.conf import settings

urlpatterns = [
    path("admin/", admin.site.urls),
    path("movies/", views.MovieListCreateAPIView.as_view(), name="movie-list"),
    path("movies/<int:pk>/", views.MovieDetailAPIView.as_view(), name="movie-detail"),
] + static(settings.POSTERS_URL, document_root=settings.POSTERS_DIR)
