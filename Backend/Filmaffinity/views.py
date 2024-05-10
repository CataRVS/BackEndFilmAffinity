from django.shortcuts import render

# Create your views here.
from rest_framework import generics, status
from rest_framework.response import Response
from rest_framework.authtoken.models import Token
from django.core.exceptions import ObjectDoesNotExist
from rest_framework.exceptions import ValidationError
from drf_spectacular.utils import extend_schema, OpenApiResponse
from django.db.utils import IntegrityError
from django.db.models import Avg
from .models import Movies, Rating
from .serializers import (MoviesSerializer,
                          UsersSerializer,
                          LoginSerializer,
                          RatingCreateListSerializer)
from rest_framework.pagination import PageNumberPagination

def is_admin(request):
    """
    By default users created as PlatformUsers are not staff.
    Therefore, we need to check if the user is staff to know if it is an admin.
    """
    token = request.COOKIES.get('session')
    if token is None or not Token.objects.filter(key=token).exists():
        raise ValidationError('No session active')
    user = Token.objects.get(key=token).user
    return user.is_staff


class UserRegisterAPIView(generics.CreateAPIView):
    """
    This view allows the registration of a user.
    """
    serializer_class = UsersSerializer

    def handle_exception(self, exc):
        if isinstance(exc, IntegrityError):
            return Response(status=status.HTTP_409_CONFLICT, data={'error': 'User already exists'})
        else:
            return super().handle_exception(exc)


class UserLoginAPIView(generics.CreateAPIView):
    """
    This view allows the login of a user.
    """
    serializer_class = LoginSerializer

    def post(self, request, *args, **kwargs):
        # If the user has a session active:
        if request.COOKIES.get('session') is not None:
            # And the token exists in the database
            if Token.objects.filter(key=request.COOKIES['session']).exists():
                # We delete the token from the database
                token = Token.objects.get(key=request.COOKIES['session'])
                token.delete()
        serializer = self.get_serializer(data=request.data)
        if serializer.is_valid():
            token, created = Token.objects.get_or_create(user=serializer.validated_data)
            response = Response(status=status.HTTP_201_CREATED)
            response.set_cookie('session', value=token.key, secure=True,
                                httponly=True, samesite='lax')
            return response
        else:
            return Response(status=status.HTTP_400_BAD_REQUEST)

    def handle_exception(self, exc):
        return Response(status=status.HTTP_400_BAD_REQUEST, data={'exception': str(exc)})


class UserInfoAPIView(generics.RetrieveUpdateDestroyAPIView):
    """
    This view returns the information of the user.
    """
    serializer_class = UsersSerializer

    def get_object(self):
        token = self.request.COOKIES.get('session')
        if token is None:
            raise ObjectDoesNotExist('No session active')
        user = Token.objects.get(key=token).user
        return user

    def retrieve(self, request, *args, **kwargs):
        user = self.get_object()
        serializer = self.get_serializer(user)
        return Response(serializer.data)

    def destroy(self, request, *args, **kwargs):
        user = self.get_object()
        user.delete()
        response = Response(status=status.HTTP_204_NO_CONTENT)
        response.delete_cookie('session')
        return response

    def handle_exception(self, exc):
        if isinstance(exc, ObjectDoesNotExist):
            return Response(status=status.HTTP_401_UNAUTHORIZED,
                            data={'error': 'No session active'})
        else:
            return super().handle_exception(exc)


class UserLogoutAPIView(generics.DestroyAPIView):
    """
    This view allows the logout of a user.
    """
    def destroy(self, request, *args, **kwargs):
        # We delete the token from the database
        if request.COOKIES.get('session') is None:
            return Response(status=status.HTTP_401_UNAUTHORIZED,
                            data={'error': 'No session active'})
        response = Response(status=status.HTTP_204_NO_CONTENT)
        response.delete_cookie('session')
        token = Token.objects.get(key=request.COOKIES['session'])
        token.delete()
        return response


class MovieListCreateAPIView(generics.ListCreateAPIView):
    """
    This view allows the creation of a movie and the list of movies.
    It consists of a filter to search for movies by title, director,
    genre, actor, rating, synopsis and language.

    The movies are returned with the average rating.
    """
    queryset = Movies.objects.all()
    serializer_class = MoviesSerializer
    pagination_class = PageNumberPagination

    def get_queryset(self):
        """
        To call this function to retrieve the movies appliyin the filters
        a code similar to the following must be used:

        import requests

        url = 'http://127.0.0.1:8000/filmaffinity/movies/'

        # Data to filter
        movie_data = {
            "title": "Inception",
        }

        response = requests.get(url, params=movie_data)
        print(response)

        Inside the movie data we can add the following filters:
        - title
        - director
        - genre
        - actor
        - rating
        - synopsis
        - language
        """

        # The queryset contais all the object Movies of the database
        queryset = super().get_queryset()

        # Get the posible params of the request
        title = self.request.query_params.get('title')
        director = self.request.query_params.get('director')
        genre = self.request.query_params.get('genre')
        actor = self.request.query_params.get('actor')
        rating = self.request.query_params.get('rating')
        synopsis = self.request.query_params.get('synopsis')
        release_date = self.request.query_params.get('release_date')
        language = self.request.query_params.get('language')

        # Validate that the params are present in the request
        # We can not have different params than those allowed
        allowed_params = {'title',
                          'rating',
                          'page',
                          'director',
                          'genre',
                          'actor',
                          'synopsis',
                          'language',
                          'page_size',}

        request_params = set(self.request.query_params.keys())
        invalid_params = request_params - allowed_params

        # If there are invalid params, we raise an error
        if invalid_params:
            raise ValidationError(f'Not Valid Params: {invalid_params}')

        # Validate that the params are valid
        try:
            # The rating must be a number
            if rating is not None:
                rating = float(rating)

                # The rating must be between 1 and 10
                if rating < 1 or rating > 10:
                    raise ValidationError('Rating must be between 1 and 10')

        except ValueError:
            raise ValidationError('Rating must be a float')

        # Filter the queryset with the params
        if title is not None:
            queryset = queryset.filter(title__icontains=title)

        # Filter for the movies directed by the director
        if director is not None:

            director = director.split()
            director_name = director[0]

            # If the director has a name and a surname
            # we assume that the name is complete and the surname
            # can be incomplete
            if len(director) > 1:

                director_surname = ' '.join(director[1:])

                # We get the movies directed by directors that have that name
                # and contain the surname
                queryset = queryset.filter(director__name=director_name,
                                           director__surname__icontains=director_surname).distinct()

            # We look for those that contain the name
            else:
                queryset = queryset.filter(director__name__icontains=director_name).distinct()

        # Filter for the movies that contain the genre
        if genre is not None:
            queryset = queryset.filter(genres__name__icontains=genre).distinct()

        # Filter for the movies that contain the actor
        if actor is not None:
            actor = actor.split()
            actor_name = actor[0]

            # If the actor has a name and a surname
            # we assume that the name is complete and the surname
            # can be incomplete
            if len(actor) > 1:

                actor_surname = ' '.join(actor[1:])

                # We get the movies that have that actor
                queryset = queryset.filter(actors__name=actor_name,
                                           actors__surname__icontains=actor_surname).distinct()

            # We look for those that contain the name
            else:
                queryset = queryset.filter(actors__name__icontains=actor_name).distinct()

        # Filter for the movies that have a rating greater than the rating
        if rating is not None:
            # The mean of the ratings of the movie must be greater than the rating
            # If the movie has no ratings, the mean is 0
            queryset = queryset.annotate(avg_rating=Avg('ratings__rating')
                                         ).filter(avg_rating__gte=rating)

        # Filter for the movies that contain the synopsis
        if synopsis is not None:
            queryset = queryset.filter(synopsis__icontains=synopsis).distinct()

        # Filter for the movies that have the release date
        if release_date is not None:
            queryset = queryset.filter(release_date__icontains=release_date)

        # Filter for the movies that contain the language
        if language is not None:
            queryset = queryset.filter(language__icontains=language).distinct()

        return queryset

    def list(self, request, *args, **kwargs):
        """
        This function returns the list of the movies with the average rating.
        """
        queryset = self.filter_queryset(self.get_queryset())

        # First look for the pagination
        paginator = self.pagination_class()
        page = paginator.paginate_queryset(queryset, request)

        if page is not None:
            serializer = self.get_serializer(page, many=True)
            data = []
            for i, movie in enumerate(page):
                movie_data = serializer.data[i]
                data.append(self.enrich_movie(movie, movie_data))
            return paginator.get_paginated_response(data)


        # If there is not a page we return the whole queryset filtered
        queryset = self.filter_queryset(self.get_queryset())

        # We get the serializer of the queryset, retrieving
        # the movies of the filter in JSON format
        serializer = self.get_serializer(queryset, many=True)

        # We add the rating to the movies
        data = []
        for i, movie in enumerate(queryset):
            movie_data = serializer.data[i]
            data.append(self.enrich_movie(movie, movie_data))

        return Response(data)

    # Only admins can create
    def create(self, request, *args, **kwargs):
        """
        If the user is not an admin, we raise an error.
        If not we create the movie with the data of the request.
        """
        token = request.COOKIES.get('session')
        if token is None or not Token.objects.filter(key=token).exists():
            raise ValidationError('No session active')
        user = Token.objects.get(key=token).user
        if not user.is_staff:
            raise ValidationError('Only admins can create movies')
        return super().create(request, *args, **kwargs)

    def handle_exception(self, exc):
        if isinstance(exc, ObjectDoesNotExist):
            return Response(status=status.HTTP_401_UNAUTHORIZED,
                            data={'error': 'No session active'})
        return super().handle_exception(exc)

    def enrich_movie(self, movie, movie_data):
        """
        This function returns the movie with the average rating.
        """
        rating_avg = movie.ratings.aggregate(avg_rating=Avg('rating')).get('avg_rating')

        # We add the rating to the movie
        movie_data['average_rating'] = rating_avg

        # We change the director and actors to a string
        movie_data['title'] = str(movie.title)
        movie_data['director'] = str(movie.director)
        movie_data['actors'] = [str(actor) for actor in movie.actors.all()]
        movie_data['genres'] = [str(genre) for genre in movie.genres.all()]

        return movie_data


class MovieDetailAPIView(generics.RetrieveUpdateDestroyAPIView):
    """
    This view allows the update and deletion of a movie as well as
    just seing the movie with the average rating.
    """
    queryset = Movies.objects.all()
    serializer_class = MoviesSerializer

    def retrieve(self, request, *args, **kwargs):
        """
        This function returns the movie with the average rating.
        """
        instance = self.get_object()
        serializer = self.get_serializer(instance)
        rating_avg = instance.ratings.aggregate(avg_rating=Avg('rating')).get('avg_rating')
        data = serializer.data
        data['average_rating'] = rating_avg

        # We change the director and actors to a string
        data['director'] = str(instance.director)
        data['actors'] = [str(actor) for actor in instance.actors.all()]
        data['genres'] = [str(genre) for genre in instance.genres.all()]
        return Response(data)

    # Only admins can update
    def update(self, request, *args, **kwargs):
        """
        If the user is an admin, we update the movie with the data of the request.
        """
        if not is_admin(request):
            raise ValidationError('Only admins can update movies')
        return super().update(request, *args, **kwargs)

    # Only admins can delete
    def delete(self, request, *args, **kwargs):
        """
        If the user is an admin, we delete the movie.
        """
        if not is_admin(request):
            raise ValidationError('Only admins can delete movies')
        return super().delete(request, *args, **kwargs)


class RatingAPIView(generics.ListCreateAPIView):
    serializer_class = RatingCreateListSerializer

    def get_queryset(self):
        """
        This method returns the list of ratings for a movie identified by 'pk'.
        """
        movie_id = self.kwargs.get('pk')
        return Rating.objects.filter(movie=movie_id)
