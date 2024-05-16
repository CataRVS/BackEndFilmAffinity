from django.shortcuts import render
from django.db.models import Q

# Create your views here.
from rest_framework import generics, status
from rest_framework.response import Response
from rest_framework.request import Request
from rest_framework.exceptions import NotFound
from rest_framework.authtoken.models import Token
from rest_framework.settings import api_settings
from rest_framework.exceptions import ValidationError
from django.core.exceptions import ObjectDoesNotExist, PermissionDenied
from django.db.utils import IntegrityError
from django.db.models import Avg, F
from drf_spectacular.utils import extend_schema, OpenApiResponse, extend_schema_view
from .models import Movies, Rating, Actors, Directors, Categories
from .serializers import (MoviesSerializer,
                          UsersSerializer,
                          LoginSerializer,
                          RatingCreateListSerializer,
                          UserRatingsSerializer,
                          ActorsSerializer,
                          DirectorsSerializer,
                          CategoriesSerializer)
from rest_framework.pagination import PageNumberPagination

def is_admin(request):
    """
    By default users created as PlatformUsers are not staff.
    Therefore, we need to check if the user is staff to know if it is an admin.
    """
    token = request.COOKIES.get('session')
    if token is None or not Token.objects.filter(key=token).exists():
        raise PermissionDenied('No session active')
    user = Token.objects.get(key=token).user
    return user.is_staff


@extend_schema(
    description='Logged in endpoint',
    responses={
       200: OpenApiResponse(description='The user is logged in.'),
       401: OpenApiResponse(description='No session active.'),
    }
)
class UserIsLoggedAPIView(generics.GenericAPIView):
    """
    This view checks if the user is logged in.
    """
    def get(self, request, *args, **kwargs):
        token = request.COOKIES.get('session')
        if token is None or not Token.objects.filter(key=token).exists():
            return Response(status=status.HTTP_401_UNAUTHORIZED,
                            data={'error': 'No session active'})
        return Response(status=status.HTTP_200_OK)


@extend_schema(
    description='Admin endpoint',
    responses={
       200: OpenApiResponse(description='The user is Admin of the platform.'),
       401: OpenApiResponse(description='The user is not Admin of the platform or no session active.'),
    }
)
class UserIsAdminAPIView(generics.GenericAPIView):
    """
    This view checks if the user is an admin.
    """
    def get(self, request, *args, **kwargs):
        if not is_admin(request):
            return Response(status=status.HTTP_401_UNAUTHORIZED,
                            data={'error': 'The user is not Admin of the platform.'})
        return Response(status=status.HTTP_200_OK)

    def handle_exception(self, exc):
        if isinstance(exc, PermissionDenied):
            return Response(status=status.HTTP_401_UNAUTHORIZED,
                            data={'error': 'No session active'})
        return super().handle_exception(exc)


@extend_schema(
    description='User registration endpoint',
    responses={
       201: OpenApiResponse(description='User registered successfully.'),
       400: OpenApiResponse(description='Invalid data.'),
       409: OpenApiResponse(description='User already exists.'),
    }
)
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


@extend_schema(
    description='User login endpoint',
    responses={
       201: OpenApiResponse(description='User logged in successfully.'),
       401: OpenApiResponse(description='Invalid credentials.'),
    }
)
class UserLoginAPIView(generics.CreateAPIView):
    """
    This view allows the login of a user.
    """
    serializer_class = LoginSerializer

    def post(self, request, *args, **kwargs):
        # If the user has a session active:
        # if request.COOKIES.get('session') is not None:
        #     # And the token exists in the database
        #     if Token.objects.filter(key=request.COOKIES['session']).exists():
        #         # We delete the token from the database
        #         token = Token.objects.get(key=request.COOKIES['session'])
        #         token.delete()
                
        serializer = self.get_serializer(data=request.data)
        if serializer.is_valid():
            # 1. Create token in django model Token
            token, created = Token.objects.get_or_create(user=serializer.validated_data)
            # 2. Set-Cookie -> navegator
            response = Response(status=status.HTTP_201_CREATED)
            response.set_cookie('session', token.key)
            
            return response
        else:
            return Response(status=status.HTTP_401_UNAUTHORIZED, data=serializer.errors)

    def handle_exception(self, exc):
        return Response(status=status.HTTP_401_UNAUTHORIZED, data={'exception': str(exc)})

# TODO: Documentate the UserInfoAPIView
@extend_schema_view(
    destroy=extend_schema(
        description='User logout endpoint',
        responses={
            204: OpenApiResponse(description='User logged out successfully.'),
            401: OpenApiResponse(description='No session active.'),
        }
    )
)
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
        if token is None or not Token.objects.filter(key=token).exists():
            raise PermissionDenied('No session active')

        # We get the user from the token
        user = Token.objects.get(key=token).user
        return user

    @extend_schema(
        description='Get user information endpoint',
        responses={
            200: OpenApiResponse(description='User information returned successfully'),
            401: OpenApiResponse(description='No session active.'),
        }
    )
    def retrieve(self, request, *args, **kwargs):
        """
        Return the user information.
        """
        user = self.get_object()
        serializer = self.get_serializer(user)
        data = serializer.data

        return Response(data)

    @extend_schema(
        description='Delete user information endpoint',
        responses={
        204: OpenApiResponse(description='User information deleted successfully'),
        401: OpenApiResponse(description='No session active.'),
        }
    )
    def destroy(self, request, *args, **kwargs):
        """
        Performs the logout of the user.
        """
        user = self.get_object()
        user.delete()
        response = Response(status=status.HTTP_204_NO_CONTENT)
        response.delete_cookie('session')
        return response

    @extend_schema(
        description='Update user information endpoint',
        responses={
        204: OpenApiResponse(description='User information updated successfully'),
        401: OpenApiResponse(description='No session active.'),
        }
    )
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
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    def handle_exception(self, exc):
        if isinstance(exc, PermissionDenied):
            return Response(status=status.HTTP_401_UNAUTHORIZED,
                            data={'error': 'No session active'})
        else:
            return super().handle_exception(exc)


@extend_schema(
    description='User logout endpoint',
    responses={
        204: OpenApiResponse(description='User logged out successfully.'),
        401: OpenApiResponse(description='No session active.'),
    }
)
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

@extend_schema(
    description='User reviews endpoint',
    responses={
        200: OpenApiResponse(description='List of reviews returned successfully'),
        401: OpenApiResponse(description='No session active'),
    }
)
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
        if token is None or not Token.objects.filter(key=token).exists():
            raise PermissionDenied('No session active')

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

    def handle_exception(self, exc):
        if isinstance(exc, PermissionDenied):
            return Response(status=status.HTTP_401_UNAUTHORIZED,
                            data={'error': 'No session active'})
        return super().handle_exception(exc)

@extend_schema_view(
    list=extend_schema(
        description='List of movies endpoint',
        responses={
            200: OpenApiResponse(description='List of movies returned successfully'),
            400: OpenApiResponse(description='Invalid data'),
        }
    ),
    create=extend_schema(
        description='Create a movie endpoint',
        responses={
            201: OpenApiResponse(description='Movie created successfully'),
            400: OpenApiResponse(description='Invalid data'),
            401: OpenApiResponse(description='Only admins can create movies.'),
        }
    )
)
class MovieListCreateAPIView(generics.ListCreateAPIView):
    """
    This view allows the creation of a movie and the list of movies.
    It consists of a filter to search for movies by title, director,
    genre, actor, rating, synopsis and language.

    The movies are returned with the average rating.
    """
    queryset = Movies.objects.all().order_by(F('title'))
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

        Inside the movie data we can add the following filters:
        - title
        - director
        - genre
        - actor
        - rating
        - synopsis
        - language
        - page_size
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

        if request.query_params.get('page_size') is not None:
            self.pagination_class.page_size = int(request.query_params.get('page_size'))
            if self.pagination_class.page_size < 1:
                raise ValueError('Page size must be greater than 0')
        else:
            self.pagination_class.page_size = api_settings.PAGE_SIZE
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
        if not is_admin(request):
            raise PermissionDenied('Only admins can create movies')

        # Transform the data if is not in the correct type
        data = request.data

        # We can receive the director as a dictionary instead of the PK
        # in the field directr_data. If that is the case, we create the director

        if "director_data" in data and not data.get('director'):
            data['director'] = validate_director(data.get('director_data'), self.get_serializer())
        
        if "genres_data" in data and not data.get('genres'):
            data['genres'] = validate_genres(data.get('genres_data', []), self.get_serializer())
        
        if "actors_data" in data and not data.get('actors'):
            data['actors'] = validate_actors(data.get('actors_data', []), self.get_serializer())

        # Procede as the super class
        # Modify the request and use the super create method
        serializer = self.get_serializer(data=data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        else:
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    def handle_exception(self, exc):
        if isinstance(exc, PermissionDenied):
            return Response(status=status.HTTP_401_UNAUTHORIZED,
                            data={'error': 'Only admins can create movies.'})
        if isinstance(exc, ObjectDoesNotExist):
            return Response(status=status.HTTP_401_UNAUTHORIZED,
                            data={'error': 'Only admins can create movies.'})
        if isinstance(exc, ValidationError):
            return Response(status=status.HTTP_400_BAD_REQUEST,
                            data={'error': str(exc)})
        if isinstance(exc, NotFound):
            return Response(status=status.HTTP_400_BAD_REQUEST,
                            data={'error': str(exc)})
        if isinstance(exc, ValueError):
            return Response(status=status.HTTP_400_BAD_REQUEST,
                            data={'error': str(exc)})
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

    def get_object(self):
        """
        This function returns the movie with the id 'pk'.
        """
        movie_id = self.kwargs.get('pk')
        return Movies.objects.get(id=movie_id)

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
            raise PermissionDenied('Only admins can update movies')
       
        # Only update the fields of the movie if they have changed
        instance = self.get_object()

        # Transform the data if is not in the correct type
        # request.data is a form so we need to transform it to a dictionary
        data = request.data
        if "director_data" in data and not data.get('director'):
            data['director'] = validate_director(data.get('director_data'), self.get_serializer())

        if "genres_data" in data and not data.get('genres'):
            data['genres'] = validate_genres(data.get('genres_data', []), self.get_serializer())
        
        if "actors_data" in data and not data.get('actors'):
            data['actors'] = validate_actors(data.get('actors_data', []), self.get_serializer())

        serializer = self.get_serializer(instance, data=data, partial=True)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data)
        else:
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    # Only admins can delete
    def delete(self, request, *args, **kwargs):
        """
        If the user is an admin, we delete the movie.
        """
        if not is_admin(request):
            raise PermissionDenied('Only admins can delete movies')
        return super().delete(request, *args, **kwargs)

    def handle_exception(self, exc):
        if isinstance(exc, ObjectDoesNotExist):
            return Response(status=status.HTTP_404_NOT_FOUND,
                            data={'error': 'Movie does not exist'})
        return super().handle_exception(exc)


class RatingAPIView(generics.ListCreateAPIView):
    """Create a rating for a movie and list all the ratings of a movie."""
    serializer_class = RatingCreateListSerializer
    pagination_class = None

    def get_queryset(self):
        """
        This method returns the list of ratings for a movie identified by 'pk'.
        """
        movie_id = self.kwargs.get('pk')
        return Rating.objects.filter(movie=movie_id)

    def create(self, request, *args, **kwargs):
        """
        This method creates a rating for a movie.
        """
        # We get the user from the token
        token = request.COOKIES.get('session')
        if token is None or not Token.objects.filter(key=token).exists():
            raise PermissionDenied('You must be logged in to rate a movie')

        # We get the user from the token
        user = Token.objects.get(key=token).user

        # We get the movie from the URL
        movie_id = self.kwargs.get('pk')
        try:
            movie = Movies.objects.get(pk=movie_id)
        except Movies.DoesNotExist:
            raise NotFound('Movie does not exist')

        # We check if the user has already rated the movie
        if Rating.objects.filter(user=user, movie=movie).exists():
            raise IntegrityError('You have already rated this movie')

        # We create the rating
        serializer = self.get_serializer(data=request.data)
        if serializer.is_valid():
            serializer.save(user=user, movie=movie)
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        else:
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    def handle_exception(self, exc):
        if isinstance(exc, PermissionDenied):
            return Response(status=status.HTTP_401_UNAUTHORIZED,
                            data={'error': 'You must be logged in to rate a movie'})
        if isinstance(exc, ValidationError):
            return Response(status=status.HTTP_400_BAD_REQUEST,
                            data={'error': str(exc)})
        if isinstance(exc, IntegrityError):
            return Response(status=status.HTTP_409_CONFLICT,
                            data={'error': 'You have already rated this movie'})
        if isinstance(exc, NotFound):
            return Response(status=status.HTTP_404_NOT_FOUND,
                            data={'error': 'Movie does not exist'})
        return super().handle_exception(exc)

class RatingUserMovieAPIView(generics.RetrieveUpdateDestroyAPIView):
    """Get, update or delete the rating of the user for a movie."""
    serializer_class = RatingCreateListSerializer

    def get_object(self):
        """
        This method returns the rating of the user for the movie.
        """
        movie_id = self.kwargs.get('pk')
        token = self.request.COOKIES.get('session')
        if token is None or not Token.objects.filter(key=token).exists():
            raise PermissionDenied('No session active')
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
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    def destroy(self, request, *args, **kwargs):
        """
        This method deletes the rating of the user for the movie.
        """
        rating = self.get_object()
        rating.delete()
        return Response(status=status.HTTP_204_NO_CONTENT)

    def handle_exception(self, exc):
        if isinstance(exc, PermissionDenied):
            return Response(status=status.HTTP_401_UNAUTHORIZED,
                            data={'error': 'No session active'})
        if isinstance(exc, ObjectDoesNotExist):
            return Response(status=status.HTTP_404_NOT_FOUND,
                            data={'error': 'Rating does not exist'})
        return super().handle_exception(exc)


class ActorsListCreateAPIView(generics.ListCreateAPIView):
    """
    This view allows the creation of an actor and the list of actors.
    """
    serializer_class = ActorsSerializer
    pagination_class = None
    queryset = Actors.objects.all()

    def create(self, request, *args, **kwargs):
        """
        This method creates an actor.
        """
        # Only admins can create
        if not is_admin(request):
            raise PermissionDenied('Only admins can create actors')

        return super().create(request, *args, **kwargs)

    def handle_exception(self, exc):
        if isinstance(exc, PermissionDenied):
            return Response(status=status.HTTP_401_UNAUTHORIZED,
                            data={'error': 'Only admins can create actors'})
    
        # If there is an error in the creation of the actor
        # we return a 409 status code
        if isinstance(exc, IntegrityError):
            return Response(status=status.HTTP_409_CONFLICT,
                            data={'error': 'Actor already exists'})
        return super().handle_exception(exc)


class DirectorListCreateAPIVIew(generics.ListCreateAPIView):
    """
    This view allows the creation of a director and the list of directors.
    """
    serializer_class = DirectorsSerializer
    pagination_class = None
    queryset = Directors.objects.all()

    def create(self, request, *args, **kwargs):
        """
        This method creates a director.
        """
        # Only admins can create
        if not is_admin(request):
            raise PermissionDenied('Only admins can create directors')

        return super().create(request, *args, **kwargs)

    def handle_exception(self, exc):
        if isinstance(exc, PermissionDenied):
            return Response(status=status.HTTP_401_UNAUTHORIZED,
                            data={'error': 'Only admins can create directors'})
    
        # If there is an error in the creation of the director
        # we return a 409 status code
        if isinstance(exc, IntegrityError):
            return Response(status=status.HTTP_409_CONFLICT,
                            data={'error': 'Director already exists'})
        return super().handle_exception(exc)


class CategoriesListCreateAPIView(generics.ListCreateAPIView):
    """
    This view allows the creation of a category and the list of categories.
    """
    serializer_class = CategoriesSerializer
    pagination_class = None
    queryset = Categories.objects.all()

    def create(self, request, *args, **kwargs):
        """
        This method creates a category.
        """
        # Only admins can create
        if not is_admin(request):
            raise PermissionDenied('Only admins can create categories')

        return super().create(request, *args, **kwargs)

    def handle_exception(self, exc):
        if isinstance(exc, PermissionDenied):
            return Response(status=status.HTTP_401_UNAUTHORIZED,
                            data={'error': 'Only admins can create categories'})
    
        # If there is an error in the creation of the category
        # we return a 409 status code
        if isinstance(exc, IntegrityError):
            return Response(status=status.HTTP_409_CONFLICT,
                            data={'error': 'Category already exists'})
        return super().handle_exception(exc)



# FUNCTIONS
def validate_actors(value, serializer):
    if not value:
        raise ValidationError("At least one actor is required")
    
    # If value[0] is not of type Actor, we check if it is a dict
    # containing the name and surname of the actor and we get or create it

    actors = []
    for actor in value:

        # Check that it is a dictionary
        if not isinstance(actor, dict):
            raise serializer.ValidationError("Actors must be a list of dictionaries")

        name = actor.get('name')
        surname = actor.get('surname')

        # If name and surname are not none
        if name and surname:
            actor, created = Actors.get_or_create_normalized(name=name, surname=surname)
            actors.append(actor.pk)
        else:
            raise ValidationError("Name and surname are required")
    return actors

    # if not, we return the list of actors
    return value

def validate_director(value, serializer):
    if not value:
        raise ValidationError("Director is required")
    # Check that it is a dictionary
    if not isinstance(value, dict):
        raise ValidationError("Director data must be a dictionary")

    name = value.get('name')
    surname = value.get('surname')


    # If name and surname are not none
    if name and surname:
        director, created = Directors.get_or_create_normalized(name=name, surname=surname)
        return director.pk
    else:
        raise ValidationError("Name and surname are required")

    # if not, we return the director
    return value


def validate_genres(value, serializer):
    if not value:
        raise ValidationError("At least one genre is required")
    
    # If value[0] is not of type Category, we check if it is a string
    # containing the name of the category and we get or create it
    genres = []
    for genre in value:

        # Check that it is a string
        if not isinstance(genre, str):
            raise ValidationError("Genres must be a list of strings")

        # If name is not none
        if genre:
            genre, created = Categories.get_or_create_normalized(name=genre)
            genres.append(genre.pk)
        else:
            raise ValidationError("Name is required")
    return genres

    # if not, we return the list of genres
    return value