from django.db import models

# Create your models here.
from django.db import models
from django.contrib.auth.models import AbstractUser, Group, Permission
from django.core.validators import RegexValidator
from django.utils.text import slugify

class PlatformUsers(AbstractUser):
    """
    This class defines the user model.
    A user has the following fields:
    - username: username of the user
    - name: first name of the user
    - surname: surname of the user
    - email: email of the user
    - password: password of the user
    """
    # The username cannot contain spaces but
    # can contain lowercase letters, numbers and underscores
    # Also, this field is mandatory
    username = models.CharField(max_length=128,
                                unique=True,
                                validators=[RegexValidator("^[a-z0-9_]+$")],
                                blank=False)

    # The name cannot contain numbers
    name = models.CharField(max_length=256,
                              validators=[RegexValidator("^[a-zA-Z ]+$")])

    # The surname cannot contain numbers
    surname = models.CharField(max_length=256,
                                validators=[RegexValidator("^[a-zA-Z ]+$")])

    # The email must be unique
    email = models.EmailField(max_length=128)
    password = models.CharField(max_length=128)

    # Resolving reverse accessor clashes by defining related_name
    groups = models.ManyToManyField(
        Group,
        verbose_name='groups',
        blank=True,
        help_text='The groups this user belongs to. A user will get all permissions granted to each of their groups.',
        related_name="platformuser_set",
        related_query_name="platformuser",
    )
    user_permissions = models.ManyToManyField(
        Permission,
        verbose_name='user permissions',
        blank=True,
        help_text='Specific permissions for this user.',
        related_name="platformuser_set",
        related_query_name="platformuser",
    )

    def save(self, *args, **kwargs):
        if not self.username:
            self.username = self.name.lower() + self.surname.lower()
        super().save(*args, **kwargs)


class Categories(models.Model):
    """
    In this table we define the categories of the movies.
    Only the admin can add new categories and these
    cannot be repeated.
    
    A category has the following fields:
    - name: name of the category.
    """

    # The name of the category cannot contain numbers
    # But can conain lowercase and uppercase letters
    name = models.CharField(max_length=50,
                            unique=True,
                            validators=[RegexValidator("^[a-zA-Z ]+$")])

    class Meta: 
        # We order the categories by name in alphabetical order
        ordering=('name',)

    def __str__(self):
        # The first letter of each word is capitalized
        return self.name.title()
    
    def save(self, *args, **kwargs):
        # Normalize the name of the category
        self.name = slugify(self.name, allow_unicode=True).replace('-', ' ').title()
        super().save(*args, **kwargs)

    @classmethod
    def get_or_create_normalized(cls, name):
        """
        When doing get_or_create, it compares regarding upper cases
        but we save the names in lower case. We define this method
        to normalize the names before doing the get_or_create, in order
        to avoid trying to create the same category with different cases,
        which would raise an IntegrityError.
        """
        normalized_name = slugify(name, allow_unicode=True).replace('-', ' ').title()

        # Usa get_or_create con los datos normalizados
        return cls.objects.get_or_create(
            name=normalized_name,
            defaults={'name': normalized_name}
        )


class Actors(models.Model):
    """
    This class defines the actors.
    An actor has the following fields:
    - name: name of the actor
    - surname: surname of the actor
    """

    # The name of the actor cannot contain numbers
    # But can conain lowercase and uppercase letters
    name = models.CharField(max_length=256,
                            validators=[RegexValidator("^[a-zA-Z ]+$")])
    surname = models.CharField(max_length=256,
                            validators=[RegexValidator("^[a-zA-Z ]+$")])

    class Meta:
        # We order the actors by name in alphabetical order
        ordering=('name',)
        unique_together = ('name', 'surname')

    def __str__(self):
        # Return Name + Surame capitalized
        return f"{self.name.title()} {self.surname.title()}"

    def save(self, *args, **kwargs):
        # Normalize the name of the actor
        self.name = slugify(self.name, allow_unicode=True).replace('-', ' ').title()
        self.surname = slugify(self.surname, allow_unicode=True).replace('-', ' ').title()
        super().save(*args, **kwargs)

    @classmethod
    def get_or_create_normalized(cls, name, surname):
        """
        When doing get_or_create, it compares regarding upper cases
        but we save the names in lower case. We define this method
        to normalize the names before doing the get_or_create, in order
        to avoid trying to create the same actor with different cases,
        which would raise an IntegrityError.
        """
        normalized_name = slugify(name, allow_unicode=True).replace('-', ' ').title()
        normalized_surname = slugify(surname, allow_unicode=True).replace('-', ' ').title()

        # Usa get_or_create con los datos normalizados
        return cls.objects.get_or_create(
            name=normalized_name,
            surname=normalized_surname,
            defaults={'name': normalized_name, 'surname': normalized_surname}
        )


class Directors(models.Model):
    """
    This class defines the directors.
    A director has the following fields:
    - name: name of the director
    - surname: surname of the director
    """

    # The name of the director cannot contain numbers
    # But can conain lowercase and uppercase letters
    name = models.CharField(max_length=256,
                            validators=[RegexValidator("^[a-zA-Z ]+$")])
    surname = models.CharField(max_length=256,
                            validators=[RegexValidator("^[a-zA-Z ]+$")])

    class Meta:
        # We order the directors by name in alphabetical order
        ordering=('name',)
        unique_together = ('name', 'surname')

    def __str__(self):
        # Return Name + Surame capitalized
        return f"{self.name.title()} {self.surname.title()}"

    def save(self, *args, **kwargs):
        # Normalize the name of the director
        self.name = slugify(self.name, allow_unicode=True).replace('-', ' ').title()
        self.surname = slugify(self.surname, allow_unicode=True).replace('-', ' ').title()
        super().save(*args, **kwargs)

    @classmethod
    def get_or_create_normalized(cls, name, surname):
        """
        When doing get_or_create, it compares regarding upper cases
        but we save the names in lower case. We define this method
        to normalize the names before doing the get_or_create, in order
        to avoid trying to create the same director with different cases,
        which would raise an IntegrityError.
        """
        normalized_name = slugify(name, allow_unicode=True).replace('-', ' ').title()
        normalized_surname = slugify(surname, allow_unicode=True).replace('-', ' ').title()

        print(normalized_name, normalized_surname)

        # Usa get_or_create con los datos normalizados
        return cls.objects.get_or_create(
            name=normalized_name,
            surname=normalized_surname,
            defaults={'name': normalized_name, 'surname': normalized_surname}
        )


class Movies(models.Model):
    """
    This class defines the movies.
    A movie has the following fields:
    - title: title of the movie
    - synopsis: synopsis of the movie
    - genres: category of the movie
    - director: director of the movie
    - actors: actors of the movie
    - duration: duration of the movie
    - release_date: release date of the movie
    - language: language of the movie
    """

    # In difference with the user, we allow any character in the title
    # because the title of a movie can contain any character
    # Also, there can be different movies with the same title
    title = models.CharField(max_length=150)
    synopsis = models.TextField()

    # A movie can have several categories
    # the related_name is to access the movies of a category
    genres = models.ManyToManyField(Categories, related_name='movies')

    # Foreign key to the director and actors
    director = models.ForeignKey(Directors, on_delete=models.CASCADE)
    actors = models.ManyToManyField(Actors, related_name='movies')

    # Aditional information
    duration = models.IntegerField()
    release_date = models.DateField()
    language = models.CharField(max_length=50)

    # Poster of the movie
    poster = models.ImageField(upload_to='posters/',
                               blank=True,
                               null=True,
                               default=None)

    class Meta:
        # Ordenamos las películas por orden alfabético 
        ordering=('title',)

    def __str__(self):
        return self.title.title()

    def save(self, *args, **kwargs):
        # Title is normalized
        self.title = slugify(self.title, allow_unicode=True).replace('-', ' ')
        super().save(*args, **kwargs)


class Rating(models.Model):
    """
    A user that has been registered can rate a movie
    with a score and a comment.
    In addition, a user cannot rate a movie more than once.

    A rating has the following fields:
    - user: user that has rated the movie
    - movie: rated movie
    - score: movie score
    - comment: movie comment
    """

    user = models.ForeignKey(PlatformUsers, on_delete=models.CASCADE)
    movie = models.ForeignKey(Movies, on_delete=models.CASCADE, related_name='ratings')
    rating = models.IntegerField()
    comment = models.TextField()

    class Meta:
        # We order the ratings by the id
        ordering=('id',)

        # A user cannot rate a movie more than once
        unique_together = ('user', 'movie')

    def __str__(self):
        return f"{self.usuario.username} has rated {self.movie.title} with a {self.rating}."
