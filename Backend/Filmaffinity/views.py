from django.shortcuts import render
from django.db.models import Q

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
                          RatingCreateListSerializer,
                          UserRatingsSerializer)
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

class UserIsLoggedAPIView(generics.GenericAPIView):
    """
    This view checks if the user is logged in.
    """
    def get(self, request, *args, **kwargs):
        if request.COOKIES.get('session') is None:
            return Response(status=status.HTTP_401_UNAUTHORIZED,
                            data={'error': 'No session active'})
        return Response(status=status.HTTP_200_OK)

class UserIsAdminAPIView(generics.GenericAPIView):
    """
    This view checks if the user is an admin.
    """
    def get(self, request, *args, **kwargs):
        if not is_admin(request):
            return Response(status=status.HTTP_401_UNAUTHORIZED,
                            data={'error': 'No session active'})
        return Response(status=status.HTTP_200_OK)

    def handle_exception(self, exc):
        if isinstance(exc, ValidationError):
            return Response(status=status.HTTP_401_UNAUTHORIZED,
                            data={'error': 'No session active'})
        return super().handle_exception(exc)

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
        """
        Function to get the user from the token.
        """
        # We get the user from the token
        token = self.request.COOKIES.get('session')

        # If the token does not exist, we raise an error
        if token is None:
            raise ObjectDoesNotExist('No session active')

        # We get the user from the token
        user = Token.objects.get(key=token).user
        return user

    def retrieve(self, request, *args, **kwargs):
        """
        Return the user information.
        """
        user = self.get_object()
        serializer = self.get_serializer(user)
        data = serializer.data

        return Response(data)

    def destroy(self, request, *args, **kwargs):
        """
        Performs the logout of the user.
        """
        user = self.get_object()
        user.delete()
        response = Response(status=status.HTTP_204_NO_CONTENT)
        response.delete_cookie('session')
        return response

    def update(self, request, *args, **kwargs):
        """
        Update the user information.
        """
        # Retreive the user
        user = self.get_object()

        # Only update the fields provided in the request
        # if they have changed
        serializer = self.get_serializer(user, data=request.data, partial=True)

        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data)
        else:
            return Response(serializer.errors)

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


class UserReviewsListAPIView(generics.ListAPIView):
    """
    This view returns the reviews of the user.
    """
    serializer_class = UserRatingsSerializer

    def get_object(self):
        """
        Function to get the user from the token.
        """
        # We get the user from the token
        token = self.request.COOKIES.get('session')

        # If the token does not exist, we raise an error
        if token is None:
            raise ObjectDoesNotExist('No session active')

        # We get the user from the token
        user = Token.objects.get(key=token).user
        return user

    def list(self, request, *args, **kwargs):
        """
        This function returns the reviews of the user.
        """
        user = self.get_object()
        ratings = user.ratings.all()
        serializer = self.get_serializer(ratings, many=True)
        return Response(serializer.data)


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

            # Design the query to filter the movies that contain the director name
            director_name_query = Q(director__name__icontains=director[0])
        
            # Check if the director has a name and a surname
            if len(director) > 1:

                # Design the query to filter the movies that contain the director surname
                # concating all the words after the name
                director_surname_query = Q(director__surname__icontains=' '.join(director[1:]))
            
            else:
                # Check if the first word is the name or the surname
                director_surname_query = Q(director__surname__icontains=director[0])

            # Filter the queryset with the director name or surname
            queryset = queryset.filter(director_name_query | director_surname_query).distinct()
    

        # Filter for the movies that contain the genre
        if genre is not None:
            queryset = queryset.filter(genres__name__icontains=genre).distinct()

        # Filter for the movies that contain the actor
        if actor is not None:
            actor = actor.split()
            
            # Design the query to filter the movies that contain the actor name
            actor_name_query = Q(actors__name__icontains=actor[0])

            # Check if the actor has a name and a surname
            if len(actor) > 1:
                    
                # Design the query to filter the movies that contain the actor surname
                # concating all the words after the name
                actor_surname_query = Q(actors__surname__icontains=' '.join(actor[1:]))
            
            else:
                # Check if the first word is the name or the surname
                actor_surname_query = Q(actors__surname__icontains=actor[0])
            
            # Filter the queryset with the actor name or surname
            queryset = queryset.filter(actor_name_query | actor_surname_query).distinct()



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
    pagination_class = None

    def get_queryset(self):
        """
        This method returns the list of ratings for a movie identified by 'pk'.
        """
        movie_id = self.kwargs.get('pk')
        return Rating.objects.filter(movie=movie_id)


class RatingUserMovieAPIView(generics.RetrieveUpdateDestroyAPIView):
    serializer_class = RatingCreateListSerializer

    def get_object(self):
        """
        This method returns the rating of the user for the movie.
        """
        movie_id = self.kwargs.get('pk')
        token = self.request.COOKIES.get('session')
        if token is None or not Token.objects.filter(key=token).exists():
            raise ValidationError('No session active')
        user = Token.objects.get(key=token).user
        return Rating.objects.get(user=user, movie=movie_id)

    def update(self, request, *args, **kwargs):
        """
        This method updates the rating of the user for the movie.
        """
        rating = self.get_object()
        serializer = self.get_serializer(rating, data=request.data, partial=True)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data)
        else:
            return Response(serializer.errors)

    def destroy(self, request, *args, **kwargs):
        """
        This method deletes the rating of the user for the movie.
        """
        rating = self.get_object()
        rating.delete()
        return Response(status=status.HTTP_204_NO_CONTENT)

    def handle_exception(self, exc):
        if isinstance(exc, ObjectDoesNotExist):
            return Response(status=status.HTTP_404_NOT_FOUND,
                            data={'error': 'Rating does not exist'})
        return super().handle_exception(exc)
