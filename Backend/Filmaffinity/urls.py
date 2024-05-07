from django.urls import path
from . import views

urlpatterns = [

    path("movies/", views.MovieListCreateAPIView.as_view(), name="movie-list"),
    path("movies/<int:pk>/", views.MovieDetailAPIView.as_view(), name="movie-detail"),
    path("users/", views.UserRegisterAPIView.as_view(), name="user-register"),
    path("users/login/", views.UserLoginAPIView.as_view(), name="user-login"),
    path("users/logout/", views.UserLogoutAPIView.as_view(), name="user-logout"),
    path("users/info/", views.UserInfoAPIView.as_view(), name="user-info"),
    path("movies/<int:pk>/rating/", views.RatingAPIView.as_view(), name="rating-create"),
]
