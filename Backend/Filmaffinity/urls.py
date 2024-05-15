from django.urls import path
from . import views

urlpatterns = [
    # Movie endpoints
    path("movies/", views.MovieListCreateAPIView.as_view(), name="movie-list"),
    path("movies/<int:pk>/", views.MovieDetailAPIView.as_view(), name="movie-detail"),
    # User endpoints
    path("users/", views.UserRegisterAPIView.as_view(), name="user-register"),
    path("users/login/", views.UserLoginAPIView.as_view(), name="user-login"),
    path("users/logout/", views.UserLogoutAPIView.as_view(), name="user-logout"),
    path("users/info/", views.UserInfoAPIView.as_view(), name="user-info"),
    path("users/check-session/", views.UserIsLoggedAPIView.as_view(), name="user-islogged"),
    path("users/check-admin/", views.UserIsAdminAPIView.as_view(), name="user-isadmin"),
    path("users/ratings/", views.UserReviewsListAPIView.as_view(), name="user-ratings"),
    # Rating endpoints
    path("movies/<int:pk>/rating/", views.RatingAPIView.as_view(), name="rating-create"),
    path("movies/<int:pk>/rating/user-rating/", views.RatingUserMovieAPIView.as_view(), name="rating-user-movie"),
    # Other models endpoints
    path("actors/", views.ActorsListCreateAPIView.as_view(), name="actor-list"),
    path("directors/", views.DirectorListCreateAPIVIew.as_view(), name="director-list"),
    path("categories/", views.CategoriesListCreateAPIView.as_view(), name="rating-list"),
]
