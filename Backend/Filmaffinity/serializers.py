import re
from rest_framework import serializers, exceptions
from django.contrib.auth import authenticate
from . import models
from django.core.validators import RegexValidator
from rest_framework.authtoken.models import Token

class UsersSerializer(serializers.ModelSerializer):
    class Meta:

        model = models.PlatformUsers
        fields = ['id', 'first_name', 'last_name', 'email', 'password']
        extra_kwargs = {
            'password': {'write_only': True}
        }

    def validate_password(self, value):
        pattern = '^(?=.*[0-9])(?=.*[A-Z])(?=.*[a-z]).*$'
        valid_password = re.match(pattern, value) and len(value) >= 8
        if valid_password:
            return value
        else:
            raise exceptions.ValidationError('Invalid password format')

    def create(self, validated_data):
        return models.PlatformUsers.objects.create_user(username=validated_data['email'], **validated_data)

    def update(self, instance, validated_data):
        if (validated_data.get('password')):
            instance.set_password(validated_data.pop('password'))
        return super().update(instance, validated_data)


class LoginSerializer(serializers.Serializer):

    email = serializers.CharField()
    password = serializers.RegexField('^(?=.*[0-9])(?=.*[A-Z])(?=.*[a-z]).*$', min_length=8)

    def validate(self, data):
        data2 = {'username': data.get('email'), 'password': data.get('password')}
        user = authenticate(**data2)

        if user:
            return user
        else:
            raise exceptions.AuthenticationFailed('Invalid credentials')


class CategoriesSerializer(serializers.ModelSerializer):
    class Meta:
        model = models.Categories
        fields = '__all__'
        extra_kwargs = {
            'name': {'validators': [RegexValidator("^[a-zA-Z ]+$")]}
        }

    def create(self, validated_data):
        return models.Categories.objects.create(**validated_data)
    
    def update(self, instance, validated_data):
        instance.name = validated_data.get('name', instance.name)
        instance.save()
        return instance
    

class MoviesSerializer(serializers.ModelSerializer):

    class Meta:
        model = models.Movies
        fields = '__all__'

    def validate_duration(self, value):
        if value < 0:
            raise serializers.ValidationError("Duration must be a positive number")
        return value

    def create(self, validated_data):
        genres = validated_data.pop('genres', [])
        actors = validated_data.pop('actors', [])
        director = validated_data.pop('director', None)

        movie = models.Movies.objects.create(director=director, **validated_data)
        movie.genres.set(genres)
        movie.actors.set(actors)
        return movie

    def update(self, instance, validated_data):
        # TODO: probar que funciona
        instance.title = validated_data.get('title', instance.title)
        instance.synopsis = validated_data.get('synopsis', instance.sinopsis)
        instance.genres = validated_data.get('genres', instance.genres)
        instance.duration = validated_data.get('duration', instance.duration)
        instance.director = validated_data.get('director', instance.director)
        instance.actors = validated_data.get('actors', instance.actors)
        instance.release_date = validated_data.get('release_date', instance.release_date)
        instance.language = validated_data.get('language', instance.language)
        instance.save()
        return instance


class ActorsSerializer(serializers.ModelSerializer):
    class Meta:
        model = models.Actors
        fields = '__all__'
        extra_kwargs = {
            'name': {'validators': [RegexValidator("^[a-zA-Z ]+$")]}
        }

    def create(self, validated_data):
        return models.Actors.objects.create(**validated_data)

    def update(self, instance, validated_data):
        # TODO: probar que funciona
        instance.name = validated_data.get('name', instance.name)
        instance.surname = validated_data.get('surname', instance.surname)
        instance.save()
        return instance


class DirectorsSerializer(serializers.ModelSerializer):
    class Meta:
        model = models.Directors
        fields = '__all__'
        extra_kwargs = {
            'name': {'validators': [RegexValidator("^[a-zA-Z ]+$")]}
        }

    def create(self, validated_data):
        return models.Directors.objects.create(**validated_data)

    def update(self, instance, validated_data):
        # TODO: probar que funciona
        instance.name = validated_data.get('name', instance.name)
        instance.surname = validated_data.get('surname', instance.surname)
        instance.save()
        return instance


class RatingSerializer(serializers.ModelSerializer):
    class Meta:
        model = models.Rating
        fields = '__all__'

    def validate_rating(self, value):
        min_rating = 1 
        max_rating = 10
        if value < min_rating or value > max_rating:
            raise serializers.ValidationError(f"Rating must be between {min_rating} and {max_rating}")
        return value

    def create(self, validated_data):
        return models.Rating.objects.create(**validated_data)

    def update(self, instance, validated_data):
        # TODO probar que funciona
        instance.user = validated_data.get('user', instance.user)
        instance.movie = validated_data.get('movie', instance.movie)
        instance.rating = validated_data.get('rating', instance.rating)
        instance.comment = validated_data.get('comment', instance.comment)
        instance.save()
        return instance


class RatingCreateListSerializer(serializers.ModelSerializer):
    # The user field is not mandatory when rating a movie
    # but it will be return when listing the ratings
    user = serializers.SlugRelatedField(slug_field='email', read_only=True)

    class Meta:
        model = models.Rating
        fields = ['rating', 'comment', 'user']
    
    def validate_rating(self, value):
        try:
            value = float(value)
        except ValueError:
            raise serializers.ValidationError('Rating must be a number')
        min_rating = 1 
        max_rating = 10
        if value < min_rating or value > max_rating:
            raise serializers.ValidationError(f"Rating must be between {min_rating} and {max_rating}")
        return value

    def create(self, validated_data):

        # We get the user from the cookie "session"
        if "session" not in self.context['request'].COOKIES:
            raise exceptions.AuthenticationFailed('You must be logged in to rate a movie')

        # Save the token in a variable
        cookie = self.context['request'].COOKIES['session']
        try:
            user = Token.objects.get(key=cookie).user
        except models.PlatformUsers.DoesNotExist:
            raise exceptions.AuthenticationFailed('You must be logged in to rate a movie')

        # We get the movie from the URL
        movie_id = self.context['view'].kwargs.get('pk')
        try:
            movie = models.Movies.objects.get(pk=movie_id)
        except models.Movies.DoesNotExist:
            raise exceptions.NotFound('Movie not found')

        # Check if the user has already rated the movie
        if models.Rating.objects.filter(user=user, movie=movie).exists():
            raise exceptions.ValidationError('You have already rated this movie')

        return models.Rating.objects.create(user=user, movie=movie, **validated_data)
