from django.shortcuts import render

# Create your views here.
from rest_framework import generics
from rest_framework.response import Response
from rest_framework.exceptions import ValidationError
from django.db.models import Avg
from .models import Movies
from .serializers import MoviesSerializer

# Only ADMIN can perform CRUD operations in the movies
# The users can only see the movies
# def is_admin(user):
#     return user.is_superuser

# class MovieCreateAPIView(generics.CreateAPIView):
#     queryset = Movies.objects.all()
#     serializer_class = MoviesSerializer

#     def perform_create(self, serializer):
#         """
#         This function is called when a movie is created
#         """
#         # We check if the user is an admin
#         if not is_admin(self.request.user):
#             raise ValidationError('Only admins can create movies')

#         # We create the movie
#         serializer.save()


class MovieListAPIView(generics.ListAPIView):
    queryset = Movies.objects.all()
    serializer_class = MoviesSerializer

    def get_queryset(self):
        """
        To call this function to retrieve the moovies appliyin the filters
        a code similar to the following must be used:
        
        import requests

        url = 'http://127.0.0.1:8000/movies/filterMovies/'

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
                          'language'}

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
                                           director__surname__icontains=director_surname)

            # We look for those that contain the name
            else:
                queryset = queryset.filter(director__name__icontains=director_name)
        
        # Filter for the movies that contain the genre
        if genre is not None:
            queryset = queryset.filter(genres__icontains=genre)

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
                                           actors__surname__icontains=actor_surname)

            # We look for those that contain the name
            else:
                queryset = queryset.filter(actors__name__icontains=actor_name)
        
        # Filter for the movies that have a rating greater than the rating
        if rating is not None:
            # The mean of the ratings of the movie must be greater than the rating
            # If the movie has no ratings, the mean is 0
            queryset = queryset.annotate(avg_rating=Avg('ratings__rating')).filter(avg_rating__gte=rating)
        
        # Filter for the movies that contain the synopsis
        if synopsis is not None:
            queryset = queryset.filter(synopsis__icontains=synopsis)
        
        # Filter for the movies that have the release date
        if release_date is not None:
            queryset = queryset.filter(release_date__icontains=release_date)
        
        # Filter for the movies that contain the language
        if language is not None:
            queryset = queryset.filter(language__icontains=language)

        return queryset
    
    def list(self, request, *args, **kwargs):
        """
        This function returns the list of the movies with the average rating.
        """
        queryset = self.filter_queryset(self.get_queryset())

        # We get the serializer of the queryset, retrieving
        # the movies of the filter in JSON format
        serializer = self.get_serializer(queryset, many=True)

        # We add the rating to the movies
        data = []
        for i, movie in enumerate(queryset):
            rating_avg = movie.ratings.aggregate(avg_rating=Avg('rating')).get('avg_rating')
            if rating_avg is None:
                rating_avg = 0  # If there are no ratings, we assign a mean of 0
            movie_data = serializer.data[i]
            movie_data['average_rating'] = rating_avg

            # We change the director and actors to a string
            movie_data['director'] = str(movie.director)
            movie_data['actors'] = [str(actor) for actor in movie.actors.all()]
            movie_data['genres'] = [str(genre) for genre in movie.genres.all()]
            data.append(movie_data)

        print(data)
        return Response(data)
