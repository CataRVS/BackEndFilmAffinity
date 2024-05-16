import os
import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'Backend.settings')
django.setup()

from Filmaffinity.models import Movies, Actors, Directors, Categories, PlatformUsers, Rating
from Filmaffinity.serializers import MoviesSerializer, UsersSerializer, RatingSerializer
from django.core.files import File


# Get the directory of the current file (create_movies.py)
current_directory = os.path.dirname(os.path.abspath(__file__))

# Build the full path to the image
# poster_path = os.path.join(current_directory, 'Posters_to_load', 'dunkirk.jpg')

# Lista de nuevas películas para agregar
# Todos los posters están en una carpeta fuera del proyecto llamada posters to load
movie_list = [
    {
        'title': 'Dunkirk',
        'synopsis': 'Allied soldiers from Belgium, the British Empire, and France are surrounded ' +
                    'by the German Army and evacuated during a fierce battle in World War II.',
        'duration': 106,
        'release_date': '2017-07-21',
        'language': 'English',
        'director': {'name': 'Christopher', 'surname': 'Nolan'},
        'actors': [{'name': 'Tom', 'surname': 'Hardy'},
                   {'name': 'Cillian', 'surname': 'Murphy'}],
        'genres': ['War', 'Action', 'History'],
        'poster': os.path.join(current_directory, '..', 'Posters_to_load', 'dunkirk.jpeg')
    },
    {
        'title': 'The Dark Knight',
        'synopsis': 'When the menace known as the Joker wreaks havoc and chaos on the people of ' +
                    'Gotham, Batman must accept one of the greatest psychological and physical ' +
                    'tests of his ability to fight injustice.',
        'duration': 152,
        'release_date': '2008-07-18',
        'language': 'English',
        'director': {'name': 'Christopher', 'surname': 'Nolan'},
        'actors': [{'name': 'Christian', 'surname': 'Bale'},
                   {'name': 'Heath', 'surname': 'Ledger'}],
        'genres': ['Action', 'Crime', 'Drama'],
        'poster': os.path.join(current_directory, '..', 'Posters_to_load', 'dark_knight.jpeg')
    },
    {
        'title': 'Blade Runner 2049',
        'synopsis': 'A young blade runner\'s discovery of a long-buried secret leads him to track' +
                    ' down former blade runner Rick Deckard, who\'s been missing for thirty years.',
        'duration': 164,
        'release_date': '2017-10-06',
        'language': 'English',
        'director': {'name': 'Denis', 'surname': 'Villeneuve'},
        'actors': [{'name': 'Ryan', 'surname': 'Gosling'},
                   {'name': 'Harrison', 'surname': 'Ford'}],
        'genres': ['Science Fiction', 'Drama'],
        'poster': os.path.join(current_directory, '..', 'Posters_to_load', 'blade_runner_2049.jpeg')
    },
    {
        'title': 'Arrival',
        'synopsis': 'A linguist works with the military to communicate with alien lifeforms after' +
                    ' twelve mysterious spacecraft appear around the world.',
        'duration': 116,
        'release_date': '2016-11-11',
        'language': 'English',
        'director': {'name': 'Denis', 'surname': 'Villeneuve'},
        'actors': [{'name': 'Amy', 'surname': 'Adams'},
                   {'name': 'Jeremy', 'surname': 'Renner'}],
        'genres': ['Science Fiction', 'Drama', 'Mystery'],
        'poster': os.path.join(current_directory, '..', 'Posters_to_load', 'arrival.jpeg')
    },
    {
        'title': 'Mad Max: Fury Road',
        'synopsis': 'In a post-apocalyptic wasteland, a woman rebels against a tyrannical ruler ' +
                    'in search for her homeland with the aid of a group of female prisoners, a ' +
                    'psychotic worshiper, and a drifter named Max.',
        'duration': 120,
        'release_date': '2015-05-15',
        'language': 'English',
        'director': {'name': 'George', 'surname': 'Miller'},
        'actors': [{'name': 'Tom', 'surname': 'Hardy'},
                   {'name': 'Charlize', 'surname': 'Theron'}],
        'genres': ['Action', 'Adventure', 'Science Fiction'],
        'poster': os.path.join(current_directory, '..', 'Posters_to_load', 'mad_max_fury_road.jpeg')
    },
    {
        'title': 'Inception',
        'synopsis': 'A thief who steals corporate secrets through the use of dream-sharing ' +
                    'technology is given the inverse task of planting an idea into the mind of ' +
                    'a CEO.',
        'duration': 148,
        'release_date': '2010-07-16',
        'language': 'English',
        'director': {'name': 'Christopher', 'surname': 'Nolan'},
        'actors': [{'name': 'Leonardo', 'surname': 'DiCaprio'},
                   {'name': 'Joseph', 'surname': 'Gordon-Levitt'}],
        'genres': ['Action', 'Adventure', 'Science Fiction'],
        'poster': os.path.join(current_directory, '..', 'Posters_to_load', 'inception.jpeg')
    },
    {
        'title': 'La La Land',
        'synopsis': 'A jazz musician and an aspiring actress fall in love while pursuing their ' +
                    'dreams in Los Angeles.',
        'duration': 128,
        'release_date': '2016-12-09',
        'language': 'English',
        'director': {'name': 'Damien', 'surname': 'Chazelle'},
        'actors': [{'name': 'Ryan', 'surname': 'Gosling'},
                   {'name': 'Emma', 'surname': 'Stone'}],
        'genres': ['Drama', 'Music', 'Romance'],
        'poster': os.path.join(current_directory, '..', 'Posters_to_load', 'la_la_land.jpeg')
    },
    {
        'title': 'Moonlight',
        'synopsis': 'A young African-American man grapples with his identity and sexuality while ' +
                    'experiencing the everyday struggles of childhood, adolescence, and ' +
                    'burgeoning adulthood.',
        'duration': 111,
        'release_date': '2016-10-21',
        'language': 'English',
        'director': {'name': 'Barry', 'surname': 'Jenkins'},
        'actors': [{'name': 'Trevante', 'surname': 'Rhodes'},
                   {'name': 'Ashton', 'surname': 'Sanders'}],
        'genres': ['Drama'],
        'poster': os.path.join(current_directory, '..', 'Posters_to_load', 'moonlight.jpeg')
    },
    {
        'title': 'The Social Network',
        'synopsis': 'Harvard student Mark Zuckerberg creates the social networking site that ' +
                    'would become known as Facebook, but is later sued by two brothers who ' +
                    'claimed he stole their idea, and the co-founder who was later squeezed out ' +
                    'of the business.',
        'duration': 120,
        'release_date': '2010-10-01',
        'language': 'English',
        'director': {'name': 'David', 'surname': 'Fincher'},
        'actors': [{'name': 'Jesse', 'surname': 'Eisenberg'},
                   {'name': 'Andrew', 'surname': 'Garfield'}],
        'genres': ['Biography', 'Drama'],
        'poster': os.path.join(current_directory, '..',
                               'Posters_to_load', 'the_social_network.jpeg')
    },
    {
        'title': 'The Grand Budapest Hotel',
        'synopsis': 'A writer encounters the owner of an aging high-class hotel, who tells him ' +
                    'of his early years serving as a lobby boy in the hotel\'s glorious years ' +
                    'under an exceptional concierge.',
        'duration': 99,
        'release_date': '2014-03-28',
        'language': 'English',
        'director': {'name': 'Wes', 'surname': 'Anderson'},
        'actors': [{'name': 'Ralph', 'surname': 'Fiennes'},
                   {'name': 'Tony', 'surname': 'Revolori'}],
        'genres': ['Adventure', 'Comedy', 'Crime'],
        'poster': os.path.join(current_directory, '..',
                               'Posters_to_load', 'the_grand_budapest_hotel.jpeg')
    },
    {
        'title': 'Parasite',
        'synopsis': 'Greed and class discrimination threaten the newly formed symbiotic ' +
                    'relationship between the wealthy Park family and the destitute Kim clan.',
        'duration': 132,
        'release_date': '2019-11-08',
        'language': 'Korean',
        'director': {'name': 'Bong', 'surname': 'Joon-ho'},
        'actors': [{'name': 'Song', 'surname': 'Kang-ho'},
                   {'name': 'Lee', 'surname': 'Sun-kyun'}],
        'genres': ['Comedy', 'Drama', 'Thriller'],
        'poster': os.path.join(current_directory, '..', 'Posters_to_load', 'parasite.jpeg')
    },
    {
        'title': 'Interstellar',
        'synopsis': 'A team of explorers travel through a wormhole in space in an attempt to ' +
                    'ensure humanity\'s survival.',
        'duration': 169,
        'release_date': '2014-11-07',
        'language': 'English',
        'director': {'name': 'Christopher', 'surname': 'Nolan'},
        'actors': [{'name': 'Matthew', 'surname': 'McConaughey'},
                   {'name': 'Anne', 'surname': 'Hathaway'}],
        'genres': ['Adventure', 'Drama', 'Sci-Fi'],
        'poster': os.path.join(current_directory, '..', 'Posters_to_load', 'interstellar.jpeg')
    },
    {
        'title': 'Gone Girl',
        'synopsis': 'With his wife\'s disappearance having become the focus of an intense media ' +
                    'circus, a man sees the spotlight turned on him when it\'s suspected that he ' +
                    'may not be innocent.',
        'duration': 149,
        'release_date': '2014-10-03',
        'language': 'English',
        'director': {'name': 'David', 'surname': 'Fincher'},
        'actors': [{'name': 'Ben', 'surname': 'Affleck'},
                   {'name': 'Rosamund', 'surname': 'Pike'}],
        'genres': ['Drama', 'Mystery', 'Thriller'],
        'poster': os.path.join(current_directory, '..', 'Posters_to_load', 'gone_girl.jpeg')
    },
    {
        'title': 'Whiplash',
        'synopsis': 'A promising young drummer enrolls at a cut-throat music conservatory where ' +
                    'his dreams of greatness are mentored by an instructor who will stop at ' +
                    'nothing to realize a student\'s potential.',
        'duration': 107,
        'release_date': '2014-10-15',
        'language': 'English',
        'director': {'name': 'Damien', 'surname': 'Chazelle'},
        'actors': [{'name': 'Miles', 'surname': 'Teller'},
                   {'name': 'J.K.', 'surname': 'Simmons'}],
        'genres': ['Drama', 'Music'],
        'poster': os.path.join(current_directory, '..', 'Posters_to_load', 'whiplash.jpeg')
    },
    {
        'title': 'Birdman',
        'synopsis': 'A washed-up superhero actor attempts to revive his fading career by writing,' +
                    ' directing, and starring in a Broadway production.',
        'duration': 119,
        'release_date': '2014-10-17',
        'language': 'English',
        'director': {'name': 'Alejandro', 'surname': 'Iñárritu'},
        'actors': [{'name': 'Michael', 'surname': 'Keaton'},
                   {'name': 'Emma', 'surname': 'Stone'}],
        'genres': ['Comedy', 'Drama'],
        'poster': os.path.join(current_directory, '..', 'Posters_to_load', 'birdman.jpeg')
    },
    {
        'title': 'Spotlight',
        'synopsis': 'The true story of how the Boston Globe uncovered the massive scandal of ' +
                    'child molestation and cover-up within the local Catholic Archdiocese, ' +
                    'shaking the entire Catholic Church to its core.',
        'duration': 128,
        'release_date': '2015-11-20',
        'language': 'English',
        'director': {'name': 'Tom', 'surname': 'McCarthy'},
        'actors': [{'name': 'Mark', 'surname': 'Ruffalo'},
                   {'name': 'Michael', 'surname': 'Keaton'}],
        'genres': ['Drama', 'History'],
        'poster': os.path.join(current_directory, '..', 'Posters_to_load', 'spotlight.jpeg')
    }
]


user_data_list = [
    {'first_name': 'Luis', 'last_name': 'Martinez',
     'email': 'luis.martinez@example.com', 'password': 'Pass1234'},
    {'first_name': 'Sofia', 'last_name': 'Castro',
     'email': 'sofia.castro@example.com', 'password': 'Pass1234'},
    {'first_name': 'Carlos', 'last_name': 'Reyes',
     'email': 'carlos.reyes@example.com', 'password': 'Pass1234'},
    {'first_name': 'Ana', 'last_name': 'Lopez',
     'email': 'ana.lopez@example.com', 'password': 'Pass1234'},
    {'first_name': 'Juan', 'last_name': 'Diaz',
     'email': 'juan.diaz@example.com', 'password': 'Pass1234'},
    {'first_name': 'Marta', 'last_name': 'Gomez',
     'email': 'marta.gomez@example.com', 'password': 'Pass1234'},
    {'first_name': 'Diego', 'last_name': 'Perez',
     'email': 'diego.perez@example.com', 'password': 'Pass1234'}
]

ratings_data = [
    {'user_email': 'luis.martinez@example.com', 'movie_title': 'Dunkirk',
     'rating': 8, 'comment': 'Impressive cinematography!'},
    {'user_email': 'luis.martinez@example.com', 'movie_title': 'The Dark Knight',
     'rating': 10, 'comment': 'Masterpiece!'},
    {'user_email': 'luis.martinez@example.com', 'movie_title': 'Blade Runner 2049',
     'rating': 9, 'comment': 'A visual spectacle!'},
    {'user_email': 'luis.martinez@example.com', 'movie_title': 'Arrival',
     'rating': 3, 'comment': 'Boring...'},
    {'user_email': 'sofia.castro@example.com', 'movie_title': 'The Dark Knight',
     'rating': 9, 'comment': 'Best Batman movie ever!'},
    {'user_email': 'sofia.castro@example.com', 'movie_title': 'Blade Runner 2049',
     'rating': 10, 'comment': 'A masterpiece!'},
    {'user_email': 'sofia.castro@example.com', 'movie_title': 'Arrival',
     'rating': 8, 'comment': 'Great movie!'},
    {'user_email': 'sofia.castro@example.com', 'movie_title': 'Mad Max: Fury Road',
     'rating': 7, 'comment': 'Not my type.'},
    {'user_email': 'carlos.reyes@example.com', 'movie_title': 'Blade Runner 2049',
     'rating': 7, 'comment': 'Visually stunning, but a bit slow.'},
    {'user_email': 'carlos.reyes@example.com', 'movie_title': 'Arrival',
     'rating': 9, 'comment': 'Thought-provoking and beautifully executed.'},
    {'user_email': 'carlos.reyes@example.com', 'movie_title': 'Gone Girl',
     'rating': 8, 'comment': 'Great thriller!'},
    {'user_email': 'carlos.reyes@example.com', 'movie_title': 'Whiplash',
     'rating': 10, 'comment': 'Amazing movie!'},
    {'user_email': 'ana.lopez@example.com', 'movie_title': 'Arrival',
     'rating': 9, 'comment': 'Thought-provoking and beautifully executed.'},
    {'user_email': 'ana.lopez@example.com', 'movie_title': 'La La Land',
     'rating': 10, 'comment': 'Beautiful movie!'},
    {'user_email': 'ana.lopez@example.com', 'movie_title': 'Moonlight',
     'rating': 8, 'comment': 'Great movie!'},
    {'user_email': 'ana.lopez@example.com', 'movie_title': 'The Social Network',
     'rating': 5, 'comment': 'Boring at best'},
    {'user_email': 'juan.diaz@example.com', 'movie_title': 'Mad Max: Fury Road',
     'rating': 8, 'comment': 'What a ride!'},
    {'user_email': 'juan.diaz@example.com', 'movie_title': 'Inception',
     'rating': 9, 'comment': 'Mind-bending!'},
    {'user_email': 'juan.diaz@example.com', 'movie_title': 'Birdman',
     'rating': 7, 'comment': 'Interesting movie.'},
    {'user_email': 'juan.diaz@example.com', 'movie_title': 'Spotlight',
     'rating': 10, 'comment': 'Great movie!'},
    {'user_email': 'marta.gomez@example.com', 'movie_title': 'Inception',
     'rating': 10, 'comment': 'Mind-bending!'},
    {'user_email': 'marta.gomez@example.com', 'movie_title': 'The Grand Budapest Hotel',
     'rating': 8, 'comment': 'Quirky and fun!'},
    {'user_email': 'marta.gomez@example.com', 'movie_title': 'Parasite',
     'rating': 9, 'comment': 'Great movie!'},
    {'user_email': 'marta.gomez@example.com', 'movie_title': 'Interstellar',
     'rating': 10, 'comment': 'Mind-bending!'},
    {'user_email': 'diego.perez@example.com', 'movie_title': 'La La Land',
     'rating': 7, 'comment': 'Great music and visuals, but not my type.'},
    {'user_email': 'diego.perez@example.com', 'movie_title': 'Moonlight',
     'rating': 9, 'comment': 'Great movie!'},
    {'user_email': 'diego.perez@example.com', 'movie_title': 'The Social Network',
     'rating': 8, 'comment': 'Great movie!'},
    {'user_email': 'diego.perez@example.com', 'movie_title': 'The Grand Budapest Hotel',
     'rating': 9, 'comment': 'Quirky and fun!'},
]


def create_users(user_data_list):
    for user_data in user_data_list:
        # Creamos usando el user serializer
        serializer = UsersSerializer(data=user_data)
        if serializer.is_valid():
            user = serializer.save()
            print(f"User '{user.first_name} {user.last_name}' added successfully " +
                  f"with ID: {user.id}")


def add_movie(movie_data):
    director_data = movie_data.pop('director')
    director, created = Directors.get_or_create_normalized(**director_data)

    actors_data = movie_data.pop('actors')
    actor_ids = []
    for actor_data in actors_data:
        actor, created = Actors.get_or_create_normalized(**actor_data)
        actor_ids.append(actor.id)

    genres_data = movie_data.pop('genres')
    genre_ids = []
    for genre_name in genres_data:
        genre, created = Categories.get_or_create_normalized(name=genre_name.strip().title())
        genre_ids.append(genre.id)

    poster_path = movie_data.pop('poster', None)
    movie_data.update({'director': director.id, 'actors': actor_ids, 'genres': genre_ids})

    serializer = MoviesSerializer(data=movie_data)
    if serializer.is_valid():
        movie = serializer.save()
        if poster_path:
            with open(poster_path, 'rb') as f:
                movie.poster.save(os.path.basename(poster_path), File(f), save=True)
        print(f"Movie '{movie.title}' added successfully with ID: {movie.id}")
    else:
        print(f"Failed to add movie '{movie_data.get('title')}': {serializer.errors}")


def add_review():
    for rating_data in ratings_data:
        user_email = rating_data.pop('user_email')
        movie_title = rating_data.pop('movie_title')

        try:
            user = PlatformUsers.objects.get(email=user_email)
        except PlatformUsers.DoesNotExist:
            print(f"User with email '{user_email}' not found.")
            continue

        try:
            movie = Movies.objects.get(title=movie_title)
        except Movies.DoesNotExist:
            print(f"Movie with title '{movie_title}' not found.")
            continue

        rating_data.update({'user': user.id, 'movie': movie.id})
        rating_serializer = RatingSerializer(data=rating_data)
        if rating_serializer.is_valid():
            rating = rating_serializer.save()
            print(f"Rating for movie '{movie.title}' by user '{user.email}' " +
                  f"added successfully with ID: {rating.id}")
        else:
            print(f"Failed to add rating for movie '{movie_title}' " +
                  f"by user '{user_email}': {rating_serializer.errors}")


# Ejecutar la adición de películas
if __name__ == "__main__":
    # Vaciamos la base de datos
    Movies.objects.all().delete()
    Directors.objects.all().delete()
    Categories.objects.all().delete()
    Actors.objects.all().delete()
    Rating.objects.all().delete()

    # Borramos todos los usuarios salvo admin
    PlatformUsers.objects.all().delete()
    admin = PlatformUsers.objects.create(first_name='super',
                                         last_name='admin',
                                         email='admin@email.com',
                                         is_staff=True)
    admin.set_password('Pass1234')
    admin.save()

    # Borramos las imágenes en la carpeta de posters
    posters_directory = os.path.join(current_directory, 'posters')

    # Solo si la carpeta existe
    if os.path.exists(posters_directory):
        for file in os.listdir(posters_directory):
            os.remove(os.path.join(posters_directory, file))

    # Cargamos el poster por defecto a la carpeta de posters
    default_poster_path = os.path.join(current_directory, '..', 'Posters_to_load', 'default.png')
    with open(default_poster_path, 'rb') as f:
        default_poster_path = os.path.join(posters_directory, 'default.png')
        with open(default_poster_path, 'wb') as poster_file:
            poster_file.write(f.read())

    for movie in movie_list:
        add_movie(movie)

    create_users(user_data_list)

    add_review()
