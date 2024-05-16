import os
import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'Backend.settings')
django.setup()

from Filmaffinity.models import Movies, Actors, Directors, Categories, PlatformUsers, Rating
from Filmaffinity.serializers import MoviesSerializer, UsersSerializer, RatingSerializer
from django.core.files import File


# Get the directory of the current file (create_movies.py)
current_directory = os.path.dirname(os.path.abspath(__file__))

if __name__ == "__main__":
    # Vaciamos la base de datos
    Movies.objects.all().delete()
    Directors.objects.all().delete()
    Categories.objects.all().delete()
    Actors.objects.all().delete()
    Rating.objects.all().delete()
    PlatformUsers.objects.all().delete()