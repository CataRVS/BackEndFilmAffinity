from django.test import SimpleTestCase, TestCase
import Filmaffinity.serializers as serializers
from rest_framework.exceptions import ValidationError

# Create your tests here.
class TestUsuarioSerializer(SimpleTestCase):
    def test_validate_password(self):
        serializer = serializers.UsuarioSerializer()
        # Test valid password
        self.assertEqual(serializer.validate_password('Contraseña0'), 'Contraseña0')
        # Test invalid password (no number)
        with self.assertRaises(ValidationError):
            serializer.validate_password('Contraseña')
        # Test invalid password (no Uppercase)
        with self.assertRaises(ValidationError):
            serializer.validate_password('contraseña0')
        # Test invalid password (no Lowercase)
        with self.assertRaises(ValidationError):
            serializer.validate_password('CONTRASEÑA0')
        # Test invalid password (less than 8 characters)
        with self.assertRaises(ValidationError):
            serializer.validate_password('Pass0')


class TestRegistroView(TestCase):
    def test_registro_view(self):
        response = self.client.post('filmaffinity/users/info/',
                                    {'first_name': 'Tomas',
                                     'last_name': 'Garcia',
                                     'email': 'tom@gmail.com',
                                     'password': 'Contraseña0'})
        self.assertNotIn('password', response.json().keys())
        self.assertEqual(response.status_code, 201)

    def test_registro_view_invalid(self):
        response = self.client.post('filmaffinity/users/info/',
                                    {'first_name': 'Andres',
                                     'last_name': 'Jimenez',
                                     'email': 'andres@gmail.com',
                                     'password': 'Contr'})
        with self.assertRaises(ValidationError):
            self.assertEqual(response.status_code, 400)

    def test_registro_view_invalid_email(self):
        response = self.client.post('filmaffinity/users/info/',
                                    {'first_name': 'Andrés_8',
                                     'last_name': 'Jimenez',
                                     'email': 'andresgmail.com',
                                     'password': 'Contraseña0'})
        with self.assertRaises(ValidationError):
            self.assertEqual(response.status_code, 400)

    def test_registro_view_invalid_duplicate_email(self):
        response = self.client.post('filmaffinity/users/info/',
                                    {'first_name': 'Tomas',
                                     'last_name': 'Garcia',
                                     'email': 'tom@gmail.com',
                                     'password': 'Contraseña0'})
        self.assertEqual(response.status_code, 201)

        response = self.client.post('filmaffinity/users/info/',
                                    {'first_name': 'Tomas',
                                     'last_name': 'Garcia',
                                     'email': 'tomas3@gmail.com',
                                     'password': 'Contraseña0'})
        self.assertEqual(response.status_code, 201)

class TestLoginView(TestCase):
    def test_login_view(self):
        response = self.client.post('filmaffinity/users/login/',
                                    {'email': 'tomas3@gmail.com',
                                     'password': 'Contraseña0'})
        self.assertEqual(response.status_code, 201)
        self.assertIn('session', response.COOKIES.get('session'))

