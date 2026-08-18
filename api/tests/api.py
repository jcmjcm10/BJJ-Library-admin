from django.test import TestCase

from rest_framework.authtoken.models import Token
from rest_framework.test import APIClient

from api.models import Tag, Video, VideoTag
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


class VideoTagPermissionTests(TestCase):
    """Los tags de un video solo los gestiona el propietario del video (o un is_staff)."""

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
            title='Privado del propietario', url='https://youtu.be/abc123',
            youtubeID='abc123', owner=self.owner, visibility='private',
        )
        self.tag = Tag.objects.create(name='guardia')
        self.videoTag = VideoTag.objects.create(video=self.video, tag=self.tag)

    def _client_for(self, user):
        client = APIClient()
        token = Token.objects.create(user=user)
        client.credentials(HTTP_AUTHORIZATION='Token ' + token.key)
        return client

    def test_intruso_no_puede_borrar_el_tag_de_un_video_ajeno(self):
        response = self._client_for(self.other).delete(
            '/videoTag/{}/'.format(self.videoTag.id),
        )

        self.assertEqual(response.status_code, 403)
        self.assertTrue(VideoTag.objects.filter(id=self.videoTag.id).exists())

    def test_intruso_no_puede_etiquetar_un_video_ajeno(self):
        response = self._client_for(self.other).post(
            '/videoTag/', {'videoId': self.video.id, 'tagId': self.tag.id}, format='json',
        )

        self.assertEqual(response.status_code, 403)
        self.assertEqual(VideoTag.objects.filter(video=self.video).count(), 1)

    def test_intruso_no_ve_los_tags_de_videos_privados_ajenos(self):
        response = self._client_for(self.other).get('/videoTag/')

        self.assertEqual(response.status_code, 200)
        ids = [item['id'] for item in response.data['results']]
        self.assertNotIn(self.videoTag.id, ids)

    def test_intruso_no_puede_mover_un_tag_a_un_video_ajeno(self):
        propio = Video.objects.create(
            title='Video del intruso', url='https://youtu.be/xyz789',
            youtubeID='xyz789', owner=self.other, visibility='private',
        )
        videoTagPropio = VideoTag.objects.create(video=propio, tag=self.tag)

        response = self._client_for(self.other).put(
            '/videoTag/{}/'.format(videoTagPropio.id),
            {'video': self.video.id, 'tag': self.tag.id}, format='json',
        )

        self.assertEqual(response.status_code, 403)
        videoTagPropio.refresh_from_db()
        self.assertEqual(videoTagPropio.video_id, propio.id)

    def test_el_propietario_si_puede_borrar_el_tag(self):
        response = self._client_for(self.owner).delete(
            '/videoTag/{}/'.format(self.videoTag.id),
        )

        self.assertEqual(response.status_code, 200)
        self.assertFalse(VideoTag.objects.filter(id=self.videoTag.id).exists())

    def test_el_propietario_si_puede_etiquetar_su_video(self):
        otroTag = Tag.objects.create(name='pasaje')
        response = self._client_for(self.owner).post(
            '/videoTag/', {'videoId': self.video.id, 'tagId': otroTag.id}, format='json',
        )

        self.assertEqual(response.status_code, 201)
        self.assertTrue(VideoTag.objects.filter(video=self.video, tag=otroTag).exists())

    def test_peticion_sin_videoId_devuelve_400(self):
        response = self._client_for(self.owner).post(
            '/videoTag/', {'tagId': self.tag.id}, format='json',
        )

        self.assertEqual(response.status_code, 400)
