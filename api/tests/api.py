from django.test import TestCase

from rest_framework.authtoken.models import Token
from rest_framework.test import APIClient

from api.models import Video
from users.models import User


class VideoUpdatePermissionTests(TestCase):
    """PUT /video/<id>/ solo lo puede hacer el propietario (o un is_staff)."""

    def setUp(self):
        self.owner = User.objects.create_user(
            username='propietario', email='propietario@example.com',
            name='Pro', last_name='Pietario', password='clave-propietario-123',
        )
        self.other = User.objects.create_user(
            username='intruso', email='intruso@example.com',
            name='In', last_name='Truso', password='clave-intruso-123',
        )
        self.video = Video.objects.create(
            title='Original', url='https://youtu.be/abc123',
            youtubeID='abc123', owner=self.owner,
        )
        self.payload = {
            'title': 'Editado por el intruso',
            'url': 'https://youtu.be/hackeado',
            'youtubeID': 'hackeado',
        }

    def _client_for(self, user):
        client = APIClient()
        token = Token.objects.create(user=user)
        client.credentials(HTTP_AUTHORIZATION='Token ' + token.key)
        return client

    def test_usuario_no_propietario_no_puede_editar(self):
        response = self._client_for(self.other).put(
            '/video/{}/'.format(self.video.id), self.payload, format='json',
        )

        self.assertEqual(response.status_code, 403)
        self.video.refresh_from_db()
        self.assertEqual(self.video.title, 'Original')

    def test_el_propietario_si_puede_editar(self):
        response = self._client_for(self.owner).put(
            '/video/{}/'.format(self.video.id), self.payload, format='json',
        )

        self.assertEqual(response.status_code, 200)
        self.video.refresh_from_db()
        self.assertEqual(self.video.title, 'Editado por el intruso')
