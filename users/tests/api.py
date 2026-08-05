from django.test import TestCase

from rest_framework.test import APIClient

from users.models import User


class UserRegistrationTests(TestCase):
    """POST /user/ es público: no debe permitir asignar privilegios."""

    def test_registro_no_permite_escalar_privilegios(self):
        client = APIClient()
        response = client.post('/user/', {
            'username': 'atacante',
            'email': 'atacante@example.com',
            'name': 'Ata',
            'last_name': 'Cante',
            'password': 'una-clave-segura-123',
            'is_superuser': True,
            'is_staff': True,
        }, format='json')

        self.assertEqual(response.status_code, 201)

        user = User.objects.get(username='atacante')
        self.assertFalse(user.is_superuser)
        self.assertFalse(user.is_staff)
