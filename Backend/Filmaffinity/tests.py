from django.test import TestCase, Client
from django.urls import reverse
from rest_framework import status
from rest_framework.authtoken.models import Token
from .models import Movies, Rating, Actors, Directors, Categories, PlatformUsers
import json


class UserViewsTestCase(TestCase):
    def setUp(self):
        # Create a user
        self.user = PlatformUsers.objects.create(first_name='testUserName',
                                                 last_name="testUserSurname",
                                                 email='test@example.com')
        self.user.set_password('Contraseña0')
        self.user.save()
        self.admin = PlatformUsers.objects.create(first_name='adminName',
                                                  last_name="adminSurname",
                                                  email="admin@email.com",
                                                  is_staff=True)
        self.admin.set_password('Contraseña0')
        self.admin.save()

        # Create a token for the user
        self.token = Token.objects.create(user=self.user)
        self.admin_token = Token.objects.create(user=self.admin)

        # Create a movie
        self.movie = Movies.objects.create(title='Movie 1',
                                            director=Directors.get_or_create_normalized(name='Director1', surname='SurnameD1')[0],
                                            release_date='2021-01-01',
                                            duration=120,
                                            synopsis='Movie 1 synopsis, boy, car',
                                            language='English')
        self.movie.genres.add(Categories.get_or_create_normalized(name='Action')[0].pk)
        self.movie.actors.add(Actors.get_or_create_normalized(name='Actor1', surname='Surname1')[0].pk)
        self.movie.actors.add(Actors.get_or_create_normalized(name='Actor2', surname='Surname2')[0].pk)

        # Create a rating for the movie
        Rating.objects.create(user=self.user, movie=self.movie, rating=8, comment='Good movie')

        # Create a client
        self.client = Client()

    def test_user_login(self):
        """Tests to check the login endpoint"""
        url = reverse('user-login')

        # Invalid login (wrong password)
        data = {'email': 'test@example.com', 'password': 'Contraseña'}
        response = self.client.post(url, data)
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

        # Invalid login (wrong data)
        data = {'email': 'test@example.com'}
        response = self.client.post(url, data)
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

        # Valid login
        data = {'email': 'test@example.com', 'password': 'Contraseña0'}
        response = self.client.post(url, data)
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)

    def test_user_logout(self):
        """Tests to check the logout endpoint"""
        url = reverse('user-logout')

        # Invalid logout
        response = self.client.delete(url)
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

        # Valid logout
        self.client.cookies['session'] = self.token.key
        response = self.client.delete(url)
        self.assertEqual(response.status_code, status.HTTP_204_NO_CONTENT)

    def test_user_is_logged_in(self):
        """Tests to check the isloggedIn endpoint"""
        url = reverse('user-islogged')

        # Invalid isLogged
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

        # Valid isLogged
        self.client.cookies['session'] = self.token.key
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)

    def test_user_is_admin(self):
        """Tests to check the isAdmin endpoint"""
        url = reverse('user-isadmin')

        # Invalid isAdmin (not logged in)
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

        # Invalid isAdmin (logged in but not admin)
        self.client.cookies['session'] = self.token.key
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

        # Valid isAdmin
        self.client.cookies['session'] = self.admin_token.key
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)

    def test_user_register_invalid(self):
        """Tests to check the register endpoint"""
        url = reverse('user-register')

        # Invalid register (no data)
        response = self.client.post(url)
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

        # Invalid register (wrong data)
        data = {'first_name': 'UserTestName',
                'last_name': 'UserTestSurname'}
        response = self.client.post(url, data)
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

        # Invalid register (wrong name)
        data = {'first_name': 'UserTestName3',
                'last_name': 'UserTestSurname',
                'email': 'test2@gmail.com',
                'password': 'Contraseña0'}
        response = self.client.post(url, data)
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

        # Invalid register (wrong surname)
        data = {'first_name': 'UserTestName',
                'last_name': 'UserTestSurname3',
                'email': 'test2@gmail.com',
                'password': 'Contraseña0'}
        response = self.client.post(url, data)
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

        # Invalid register (wrong email)
        data = {'first_name': 'UserTestName',
                'last_name': 'UserTestSurname',
                'email': 'test2gmail.com',
                'password': 'Contraseña0'}
        response = self.client.post(url, data)
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

        # Invalid register (wrong password)
        data = {'first_name': 'UserTestName',
                'last_name': 'UserTestSurname',
                'email': 'test2@gmail.com',
                'password': 'Contr'}

        # Invalid register (email already exists)
        data = {'first_name': 'UserTestName',
                'last_name': 'UserTestSurname',
                'email': 'test@example.com',
                'password': 'Contraseña0'}
        response = self.client.post(url, data)
        self.assertEqual(response.status_code, status.HTTP_409_CONFLICT)

    def test_user_register_valid(self):
        """Tests to check the register endpoint"""
        url = reverse('user-register')
        # Valid register
        data = {'first_name': 'UserTestName',
                'last_name': 'UserTestSurname',
                'email': 'test2@gmail.com',
                'password': 'Contraseña0'}
        response = self.client.post(url, data)
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertNotIn('password', response.json())

    def test_user_info(self):
        """Tests to check the info endpoint"""
        url = reverse('user-info')

        # Invalid info
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

        # Valid info
        self.client.cookies['session'] = self.token.key
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertIn('first_name', response.json())
        self.assertIn('last_name', response.json())
        self.assertIn('email', response.json())
        self.assertNotIn('password', response.json())

    def test_user_ratings(self):
        """Tests to check the ratings endpoint"""
        url = reverse('user-ratings')

        # Invalid ratings
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

        # Valid ratings
        self.client.cookies['session'] = self.token.key
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)


class MoviesViewsTestCase(TestCase):
    def setUp(self):
        # Create two normal users and an admin
        self.user1 = PlatformUsers.objects.create(first_name='testUserName',
                                                 last_name="testUserSurname",
                                                 email='test@example.com')
        self.user1.set_password('Contraseña0')
        self.user1.save()
        self.user2 = PlatformUsers.objects.create(first_name='testUserNameTwo',
                                                 last_name="testUserSurnameTwo",
                                                 email='test2@example.com')
        self.user2.set_password('Contraseña0')
        self.user2.save()
        self.admin = PlatformUsers.objects.create(first_name='adminName',
                                                  last_name="adminSurname",
                                                  email="admin@email.com",
                                                  is_staff=True)
        self.admin.set_password('Contraseña0')
        self.admin.save()

        # Create a token for the users
        self.token1 = Token.objects.create(user=self.user1)
        self.token2 = Token.objects.create(user=self.user2)
        self.admin_token = Token.objects.create(user=self.admin)

        # Create three movies
        self.movie1 = Movies.objects.create(title='Movie 1',
                                            director=Directors.get_or_create_normalized(name='Director1', surname='SurnameD1')[0],
                                            release_date='2021-01-01',
                                            duration=120,
                                            synopsis='Movie 1 synopsis, boy, car',
                                            language='English')
        self.movie1.genres.add(Categories.get_or_create_normalized(name='Action')[0].pk)
        self.movie1.actors.add(Actors.get_or_create_normalized(name='Actor1', surname='Surname1')[0].pk)
        self.movie1.actors.add(Actors.get_or_create_normalized(name='Actor2', surname='Surname2')[0].pk)
        self.movie2 = Movies.objects.create(title='Movie 2',
                                            director=Directors.get_or_create_normalized(name='director2', surname='SurnameD2')[0],
                                            release_date='2021-01-01',
                                            duration=248,
                                            synopsis='Movie 2 synopsis, woman, food',
                                            language='Spanish')
        self.movie2.genres.add(Categories.get_or_create_normalized(name='Drama')[0].pk)
        self.movie2.actors.add(Actors.get_or_create_normalized(name='Actor2', surname='Surname2')[0].pk)
        self.movie2.actors.add(Actors.get_or_create_normalized(name='Actor3', surname='Surname3')[0].pk)

        self.movie3 = Movies.objects.create(title='Movie 3',
                                            director=Directors.get_or_create_normalized(name='Director2', surname='SurnameD2')[0],
                                            release_date='2021-01-01',
                                            duration=180,
                                            synopsis='Movie 3 synopsis, woman, dog',
                                            language='English')
        self.movie3.genres.add(Categories.get_or_create_normalized(name='Drama')[0].pk)
        self.movie3.genres.add(Categories.get_or_create_normalized(name='action')[0].pk)
        self.movie3.actors.add(Actors.get_or_create_normalized(name='actor2', surname='Surname2')[0].pk)
        self.movie3.actors.add(Actors.get_or_create_normalized(name='Actor3', surname='Surname3')[0].pk)
        self.movie3.actors.add(Actors.get_or_create_normalized(name='Actor4', surname='Surname4')[0].pk)

        # Create ratings for the movies
        # The first movie has two ratings, the second one has one and the third one has none
        Rating.objects.create(user=self.user1, movie=self.movie1, rating=8, comment='Good movie')
        Rating.objects.create(user=self.user1, movie=self.movie2, rating=3, comment='Bad movie')
        Rating.objects.create(user=self.user2, movie=self.movie1, rating=5, comment='Average movie')

        # Create a client
        self.client = Client()

    def test_movie_list(self):
        """Tests to check the list endpoint with no filters."""
        url = reverse('movie-list')
        # Valid list with no filters
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)

    def test_movie_list_standard_filters(self):
        """Tests to check the list endpoint with standard fields filters."""
        url = reverse('movie-list')
        # Valid list with title filter
        filters = {'title': '1'}
        response = self.client.get(url, filters)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.json().get('results', [])), 1)

        # Valid list with rating filter
        filters = {'rating': '5'}
        response = self.client.get(url, filters)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.json().get('results', [])), 1)

        # Valid list with language filter
        filters = {'language': 'Spanish'}
        response = self.client.get(url, filters)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.json().get('results', [])), 1)

        # Valid list with synopsis filter
        filters = {'synopsis': "woman"}
        response = self.client.get(url, filters)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.json().get('results', [])), 2)

    def test_movie_list_FK_filters(self):
        """Tests to check the list endpoint with FK fields filters."""
        url = reverse('movie-list')

        # Valid list with genre filter
        filters = {'genre': 'Action'}
        response = self.client.get(url, filters)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.json().get('results', [])), 2)

        # Valid list with actor filter with only name
        filters = {'actor': 'Actor3'}
        response = self.client.get(url, filters)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.json().get('results', [])), 2)

        # Valid list with actor filter with name and surname
        filters = {'actor': 'Actor4 Surname4'}
        response = self.client.get(url, filters)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.json().get('results', [])), 1)

        # Valid list with actor filter with name and surname incomplete
        filters = {'actor': 'Actor Surname'}
        response = self.client.get(url, filters)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.json().get('results', [])), 3)

        # Valid list with director filter
        filters = {'director': 'Director2'}
        response = self.client.get(url, filters)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.json().get('results', [])), 2)

        # Valid list with multiple filters
        filters = {'genre': 'Action', 'actor': 'Actor3'}
        response = self.client.get(url, filters)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.json().get('results', [])), 1)

    def test_movie_list_pagination_filters(self):
        """Tests to check the list endpoint with pagination filters."""
        url = reverse('movie-list')
        # Valid list with valid page filter
        filters = {'page': '1'}
        response = self.client.get(url, filters)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.json().get('results', [])), 3)

        # Valid list with invalid page filter
        filters = {'page': '2'}
        response = self.client.get(url, filters)
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

        # Valid list with invalid page filter (not a number)
        filters = {'page': 'a'}
        response = self.client.get(url, filters)
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

        # Valid list with invalid page filter (negative number)
        filters = {'page': '-1'}
        response = self.client.get(url, filters)
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

        # Valid list with invalid page filter (zero)
        filters = {'page': '0'}
        response = self.client.get(url, filters)
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

        # Valid list with page_size filter
        filters = {'page_size': '1'}
        response = self.client.get(url, filters)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.json().get('results', [])), 1)

        # Valid list with page_size and page filters
        filters = {'page_size': '1', 'page': '2'}
        response = self.client.get(url, filters)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.json().get('results', [])), 1)

        # Valid list with invalid page_size filter (not a number)
        filters = {'page_size': 'a'}
        response = self.client.get(url, filters)
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

        # Valid list with invalid page_size filter (negative number)
        filters = {'page_size': '-1'}
        response = self.client.get(url, filters)
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

        # Valid list with invalid page_size filter (zero)
        filters = {'page_size': '0'}
        response = self.client.get(url, filters)
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_movie_detail(self):
        """Tests to check the detail endpoint."""
        # Valid detail with existing movie
        url = reverse('movie-detail', kwargs={'pk': self.movie1.id})
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)

        # Invalid detail with non-existing movie
        url = reverse('movie-detail', kwargs={'pk': 999})
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)

    def test_movie_create_invalid_basic(self):
        """Tests to check the create endpoint with invalid data."""
        url = reverse('movie-list')

        # Invalid create (not logged in)
        response = self.client.post(url)
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

        # Invalid create (logged in but not admin)
        self.client.cookies['session'] = self.token1.key
        response = self.client.post(url)
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

        # Now we log in as an admin
        self.client.cookies['session'] = self.admin_token.key

        # Invalid create with no data provided
        response = self.client.post(url)
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

        # Invalid create with wrong data: mandatory fields missing
        data = {'title': 'Movie 4'}
        response = self.client.post(url, data)
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_movie_create_using_data_option(self):
        """Tests to check the create endpoint using the _data option."""
        url = reverse('movie-list')
        # Now we log in as an admin
        self.client.cookies['session'] = self.admin_token.key

        # Invalid create with missing genre
        data = {'title': 'Movie 1',
                'director_data': {'name': 'Director1', 'surname': 'SurnameD1'},
                'release_date': '2021-01-01',
                'duration': 120,
                'synopsis': 'Movie 1 synopsis',
                'language': 'English',
                'actors_data': [{'name': 'Actor1', 'surname': 'Surname1'},
                           {'name': 'Actor2', 'surname': 'Surname2'}]}
        response = self.client.post(url, json.dumps(data), content_type='application/json')
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

        # Invalid create with missing actor
        data = {'title': 'Movie 1',
                'director_data': {'name': 'Director1', 'surname': 'SurnameD1'},
                'release_date': '2021-01-01',
                'duration': 120,
                'synopsis': 'Movie 1 synopsis',
                'language': 'English',
                'genres_data': ['Action']}
        response = self.client.post(url, json.dumps(data), content_type='application/json')
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

        # Invalid create with missing director
        data = {'title': 'Movie 1',
                'release_date': '2021-01-01',
                'duration': 120,
                'synopsis': 'Movie 1 synopsis',
                'language': 'English',
                'genres_data': ['Action'],
                'actors_data': [{'name': 'Actor1', 'surname': 'Surname1'},
                           {'name': 'Actor2', 'surname': 'Surname2'}]}
        response = self.client.post(url, json.dumps(data), content_type='application/json')
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

        # Invalid create (wrong director)
        data = {'title': 'Movie 4',
                'director_data': 'Director4 SurnameD4',
                'release_date': '2021-01-01',
                'duration': 120,
                'synopsis': 'Movie 4 synopsis',
                'language': 'English'}
        response = self.client.post(url, data)
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

        # Invalid create (wrong genre)
        data = {'title': 'Movie 4',
                'director_data': 'Director4 SurnameD4',
                'release_date': '2021-01-01',
                'duration': 120,
                'synopsis': 'Movie 4 synopsis',
                'language': 'English',
                'genres_data': ['Action', 'Comedy']}
        response = self.client.post(url, data)
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

        # Invalid create (wrong actor)
        data = {'title': 'Movie 4',
                'director_data': 'Director4 SurnameD4',
                'release_date': '2021-01-01',
                'duration': 120,
                'synopsis': 'Movie 4 synopsis',
                'language': 'English',
                'actors_data': [{'name': 'Actor1', 'surname': 'Surname1'},
                           {'name': 'Actor2', 'surname': 'Surname2'},
                           {'name': 'Actor3', 'surname': 'Surname3'}]}
        response = self.client.post(url, data)
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

        # Valid create
        data = {'title': 'Movie 4',
                'director_data': {'name': 'Director4', 'surname': 'SurnameD4'},
                'release_date': '2021-01-01',
                'duration': 120,
                'synopsis': 'Movie 4 synopsis',
                'language': 'English',
                'genres_data': ['Action'],
                'actors_data': [{'name': 'Actor1', 'surname': 'Surname1'},
                           {'name': 'Actor2', 'surname': 'Surname2'}]}
        response = self.client.post(url, json.dumps(data), content_type='application/json')
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)

    def test_movie_create_using_pk_option(self):
        """Tests to check the create endpoint using the pk option."""
        url = reverse('movie-list')
        # Now we log in as an admin
        self.client.cookies['session'] = self.admin_token.key

        # Invalid create with wrong director
        data = {'title': 'Movie 4',
                'director': 'Director4 SurnameD4',
                'release_date': '2021-01-01',
                'duration': 120,
                'synopsis': 'Movie 4 synopsis',
                'language': 'English',
                'genres': [Categories.get_or_create_normalized(name='Action')[0].pk],
                'actors': [Actors.get_or_create_normalized(name='Actor1', surname='Surname1')[0].pk,
                           Actors.get_or_create_normalized(name='Actor2', surname='Surname2')[0].pk]}
        response = self.client.post(url, data)
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

        # Invalid create with no director
        data = {'title': 'Movie 4',
                'release_date': '2021-01-01',
                'duration': 120,
                'synopsis': 'Movie 4 synopsis',
                'language': 'English',
                'genres': [Categories.get_or_create_normalized(name='Action')[0].pk],
                'actors': [Actors.get_or_create_normalized(name='Actor1', surname='Surname1')[0].pk,
                           Actors.get_or_create_normalized(name='Actor2', surname='Surname2')[0].pk]}
        response = self.client.post(url, data)
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

        # Invalid create with wrong genre
        data = {'title': 'Movie 4',
                'director': Directors.get_or_create_normalized(name='Director4', surname='SurnameD4')[0].pk,
                'release_date': '2021-01-01',
                'duration': 120,
                'synopsis': 'Movie 4 synopsis',
                'language': 'English',
                'genres': ['Action', 'Comedy'],
                'actors': [Actors.get_or_create_normalized(name='Actor1', surname='Surname1')[0].pk,
                           Actors.get_or_create_normalized(name='Actor2', surname='Surname2')[0].pk]}
        response = self.client.post(url, data)
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

        # Invalid create with no genre
        data = {'title': 'Movie 4',
                'director': Directors.get_or_create_normalized(name='Director4', surname='SurnameD4')[0].pk,
                'release_date': '2021-01-01',
                'duration': 120,
                'synopsis': 'Movie 4 synopsis',
                'language': 'English',
                'actors': [Actors.get_or_create_normalized(name='Actor1', surname='Surname1')[0].pk,
                            Actors.get_or_create_normalized(name='Actor2', surname='Surname2')[0].pk]}
        response = self.client.post(url, data)
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

        # Invalid create with wrong actor
        data = {'title': 'Movie 4',
                'director': Directors.get_or_create_normalized(name='Director4', surname='SurnameD4')[0].pk,
                'release_date': '2021-01-01',
                'duration': 120,
                'synopsis': 'Movie 4 synopsis',
                'language': 'English',
                'genres': [Categories.get_or_create_normalized(name='Action')[0].pk],
                'actors': ['Actor1 Surname1', 'Actor2 Surname2', 'Actor3 Surname3']}
        response = self.client.post(url, data)
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

        # Invalid create with wrong actor
        data = {'title': 'Movie 4',
                'director': Directors.get_or_create_normalized(name='Director4', surname='SurnameD4')[0].pk,
                'release_date': '2021-01-01',
                'duration': 120,
                'synopsis': 'Movie 4 synopsis',
                'language': 'English',
                'genres': [Categories.get_or_create_normalized(name='Action')[0].pk]}
        response = self.client.post(url, data)
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

        # Valid create
        data = {'title': 'Movie 4',
                'director': Directors.get_or_create_normalized(name='Director4', surname='SurnameD4')[0].pk,
                'release_date': '2021-01-01',
                'duration': 120,
                'synopsis': 'Movie 4 synopsis',
                'language': 'English',
                'genres': [Categories.get_or_create_normalized(name='Action')[0].pk],
                'actors': [Actors.get_or_create_normalized(name='Actor1', surname='Surname1')[0].pk,
                           Actors.get_or_create_normalized(name='Actor2', surname='Surname2')[0].pk]}
        response = self.client.post(url, data)
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)


class RatingsViewsTestCase(TestCase):
    def setUp(self):
        # Create two normal users and an admin
        self.user1 = PlatformUsers.objects.create(first_name='testUserName',
                                                 last_name="testUserSurname",
                                                 email='test@example.com')
        self.user1.set_password('Contraseña0')
        self.user1.save()
        self.user2 = PlatformUsers.objects.create(first_name='testUserNameTwo',
                                                 last_name="testUserSurnameTwo",
                                                 email='test2@example.com')
        self.user2.set_password('Contraseña0')
        self.user2.save()
        self.admin = PlatformUsers.objects.create(first_name='adminName',
                                                  last_name="adminSurname",
                                                  email="admin@email.com",
                                                  is_staff=True)
        self.admin.set_password('Contraseña0')
        self.admin.save()

        # Create a token for the users
        self.token1 = Token.objects.create(user=self.user1)
        self.token2 = Token.objects.create(user=self.user2)
        self.admin_token = Token.objects.create(user=self.admin)

        # Create three movies
        self.movie1 = Movies.objects.create(title='Movie 1',
                                            director=Directors.get_or_create_normalized(name='Director1', surname='SurnameD1')[0],
                                            release_date='2021-01-01',
                                            duration=120,
                                            synopsis='Movie 1 synopsis, boy, car',
                                            language='English')
        self.movie1.genres.add(Categories.get_or_create_normalized(name='Action')[0].pk)
        self.movie1.actors.add(Actors.get_or_create_normalized(name='Actor1', surname='Surname1')[0].pk)
        self.movie1.actors.add(Actors.get_or_create_normalized(name='Actor2', surname='Surname2')[0].pk)
        self.movie2 = Movies.objects.create(title='Movie 2',
                                            director=Directors.get_or_create_normalized(name='director2', surname='SurnameD2')[0],
                                            release_date='2021-01-01',
                                            duration=248,
                                            synopsis='Movie 2 synopsis, woman, food',
                                            language='Spanish')
        self.movie2.genres.add(Categories.get_or_create_normalized(name='Drama')[0].pk)
        self.movie2.actors.add(Actors.get_or_create_normalized(name='Actor2', surname='Surname2')[0].pk)
        self.movie2.actors.add(Actors.get_or_create_normalized(name='Actor3', surname='Surname3')[0].pk)

        self.movie3 = Movies.objects.create(title='Movie 3',
                                            director=Directors.get_or_create_normalized(name='Director2', surname='SurnameD2')[0],
                                            release_date='2021-01-01',
                                            duration=180,
                                            synopsis='Movie 3 synopsis, woman, dog',
                                            language='English')
        self.movie3.genres.add(Categories.get_or_create_normalized(name='Drama')[0].pk)
        self.movie3.genres.add(Categories.get_or_create_normalized(name='action')[0].pk)
        self.movie3.actors.add(Actors.get_or_create_normalized(name='actor2', surname='Surname2')[0].pk)
        self.movie3.actors.add(Actors.get_or_create_normalized(name='Actor3', surname='Surname3')[0].pk)
        self.movie3.actors.add(Actors.get_or_create_normalized(name='Actor4', surname='Surname4')[0].pk)

        # Create ratings for the movies
        # The first movie has two ratings, the second one has one and the third one has none
        Rating.objects.create(user=self.user1, movie=self.movie1, rating=8, comment='Good movie')
        Rating.objects.create(user=self.user1, movie=self.movie2, rating=3, comment='Bad movie')
        Rating.objects.create(user=self.user2, movie=self.movie1, rating=5, comment='Average movie')

        # Create a client
        self.client = Client()

    def test_rating_create_invalid(self):
        """Tests to check the rating endpoint."""
        url = reverse('rating-create', kwargs={'pk': 197516347})
        
        # Invalid create (not logged in)
        response = self.client.post(url)
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

        # We log in as a user
        self.client.cookies['session'] = self.token2.key

        # Invalid create (movie does not exist)
        response = self.client.post(url)
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)

        # Invalid create (rating missing)
        url = reverse('rating-create', kwargs={'pk': self.movie2.id})
        response = self.client.post(url)
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

        # Invalid create (rating missing but comment provided)
        data = {'comment': 'Good movie'}
        response = self.client.post(url)
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

        # Invalid create with wrong rating (greater than 10)
        data = {'rating': 11}
        response = self.client.post(url, data)
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

        # Invalid create with wrong rating (negative rating)
        data = {'rating': -1}
        response = self.client.post(url, data)
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

        # Invalid create with wrong rating (rating is 0)
        data = {'rating': 0}
        response = self.client.post(url, data)
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

        # Invalid create with wrong rating (rating is not a number)
        data = {'rating': 'a'}
        response = self.client.post(url, data)
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

        # Invalid create (rating already exists)
        url = reverse('rating-create', kwargs={'pk': self.movie1.id})
        data = {'rating': 5}
        response = self.client.post(url, data)
        self.assertEqual(response.status_code, status.HTTP_409_CONFLICT)

    def test_rating_create_valid(self):
        """Tests to check the rating endpoint."""
        url = reverse('rating-create', kwargs={'pk': self.movie2.id})
        self.client.cookies['session'] = self.token2.key

        # Rating without comment
        data = {'rating': 9}
        response = self.client.post(url, data)
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)

        # Rating with comment
        url = reverse('rating-create', kwargs={'pk': self.movie3.id})
        data = {'rating': 8, 'comment': 'Good movie'}
        response = self.client.post(url, data)
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)

    def test_get_rating_user_movie(self):
        """Tests to check the rating endpoint."""
        url = reverse('rating-user-movie', kwargs={'pk': 197516347})

        # Invalid get (not logged in)
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

        # We log in as a user
        self.client.cookies['session'] = self.token2.key

        # Invalid get (movie does not exist)
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)

        # Valid get
        url = reverse('rating-user-movie', kwargs={'pk': self.movie1.id})
        response = self.client.get(url)

    def test_put_rating_user_movie(self):
        """Tests to check the rating endpoint."""
        url = reverse('rating-user-movie', kwargs={'pk': 197516347})

        # Invalid put (not logged in)
        response = self.client.put(url)
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

        # We log in as a user
        self.client.cookies['session'] = self.token1.key

        # Invalid put (movie does not exist)
        response = self.client.put(url)
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)

        url = reverse('rating-user-movie', kwargs={'pk': self.movie1.id})

        # Invalid put (rating > 10)
        data = {'rating': 11}
        response = self.client.put(url, data, content_type='application/json')
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

        # Invalid put (rating < 0)
        data = {'rating': -1}
        response = self.client.put(url, data, content_type='application/json')
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

        # Invalid put (rating = 0)
        data = {'rating': 0}
        response = self.client.put(url, data, content_type='application/json')
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

        # Valid put
        data = {'rating': 9}
        response = self.client.put(url, data, content_type='application/json')
        self.assertEqual(response.status_code, status.HTTP_200_OK)

    def test_delete_rating_user_movie(self):
        """Tests to check the rating endpoint."""
        url = reverse('rating-user-movie', kwargs={'pk': 197516347})

        # Invalid delete (not logged in)
        response = self.client.delete(url)
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

        # We log in as a user
        self.client.cookies['session'] = self.token1.key

        # Invalid delete (movie does not exist)
        response = self.client.delete(url)
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)

        url = reverse('rating-user-movie', kwargs={'pk': self.movie1.id})

        # Valid delete
        response = self.client.delete(url)
        self.assertEqual(response.status_code, status.HTTP_204_NO_CONTENT)
