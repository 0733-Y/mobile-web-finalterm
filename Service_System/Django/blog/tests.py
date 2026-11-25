import io
import tempfile
from datetime import timedelta

from django.contrib.auth.models import Permission, User
from django.core.files.uploadedfile import SimpleUploadedFile
from django.test import override_settings
from django.utils import timezone
from PIL import Image
from rest_framework.test import APITestCase

from .models import Post, Space


def make_image(name='t.jpg'):
    buf = io.BytesIO()
    Image.new('RGB', (10, 10), 'red').save(buf, 'JPEG')
    return SimpleUploadedFile(name, buf.getvalue(), content_type='image/jpeg')


class ApiTests(APITestCase):
    def setUp(self):
        tmp = tempfile.TemporaryDirectory()
        self.addCleanup(tmp.cleanup)
        override = override_settings(MEDIA_ROOT=tmp.name)
        override.enable()
        self.addCleanup(override.disable)
        self.user = User.objects.create_user('edge', password='pw12345!')
        self.user.user_permissions.add(Permission.objects.get(codename='add_post', content_type__app_label='blog'))
        self.viewer = User.objects.create_user('viewer', password='pw12345!')
        self.space = Space.objects.create(name='열람실 A', capacity=100)

    def login(self, username='edge'):
        r = self.client.post('/api-token-auth/', {'username': username, 'password': 'pw12345!'})
        self.assertEqual(r.status_code, 200)
        self.client.credentials(HTTP_AUTHORIZATION='Token ' + r.data['token'])

    def test_token_wrong_password(self):
        r = self.client.post('/api-token-auth/', {'username': 'edge', 'password': 'bad'})
        self.assertEqual(r.status_code, 400)

    def test_requires_auth(self):
        self.assertEqual(self.client.get('/api_root/Post/').status_code, 401)
        self.assertEqual(self.client.post('/api_root/Post/', {}).status_code, 401)

    def test_post_upload_and_get(self):
        self.login()
        r = self.client.post('/api_root/Post/', {
            'title': 't', 'text': 'x', 'image': make_image(),
            'space': self.space.id, 'person_count': 85, 'level': '혼잡',
        }, format='multipart')
        self.assertEqual(r.status_code, 201, r.data)
        pid = r.data['id']
        self.assertIsNotNone(Post.objects.get(pk=pid).published_date)
        d = self.client.get(f'/api_root/Post/{pid}/')
        self.assertEqual(d.status_code, 200)
        self.assertEqual(d.data['person_count'], 85)

    def test_list_latest_first_and_filter(self):
        self.login()
        other = Space.objects.create(name='B', capacity=10)
        for i, sp in enumerate([self.space, other, self.space]):
            self.client.post('/api_root/Post/', {'title': f'p{i}', 'space': sp.id,
                                                 'person_count': i}, format='multipart')
        r = self.client.get('/api_root/Post/')
        self.assertEqual([p['title'] for p in r.data['results']], ['p2', 'p1', 'p0'])
        r = self.client.get(f'/api_root/Post/?space={self.space.id}')
        self.assertEqual(r.data['count'], 2)

    def test_space_latest(self):
        self.login()
        r = self.client.get('/api_root/Space/')
        self.assertIsNone(r.data['results'][0]['latest'])
        self.client.post('/api_root/Post/', {'title': 'a', 'space': self.space.id,
                                             'person_count': 7, 'level': '여유'},
                         format='multipart')
        r = self.client.get('/api_root/Space/')
        self.assertEqual(r.data['results'][0]['latest']['person_count'], 7)

    def test_viewer_read_only(self):
        self.login('viewer')
        self.assertEqual(self.client.get('/api_root/Post/').status_code, 200)
        self.assertEqual(self.client.get('/api_root/Space/').status_code, 200)
        r = self.client.post('/api_root/Post/', {'title': 'x', 'space': self.space.id}, format='multipart')
        self.assertEqual(r.status_code, 403)
        self.assertEqual(Post.objects.count(), 0)

    def test_viewer_cannot_delete(self):
        self.login()
        pid = self.client.post('/api_root/Post/', {'title': 'e'}, format='multipart').data['id']
        self.client.credentials()
        self.login('viewer')
        self.assertEqual(self.client.delete(f'/api_root/Post/{pid}/').status_code, 403)
        self.assertTrue(Post.objects.filter(pk=pid).exists())

    def test_future_client_time_still_listed(self):
        """Edge 시계가 서버보다 1시간 빨라도 업로드 직후 홈 화면에 보여야 한다."""
        self.login()
        future = (timezone.now() + timedelta(hours=1)).isoformat()
        r = self.client.post('/api_root/Post/', {'title': '5960 | clock', 'published_date': future},
                             format='multipart')
        self.assertEqual(r.status_code, 201)
        self.assertLessEqual(Post.objects.get(pk=r.data['id']).published_date, timezone.now())
        self.assertContains(self.client.get('/'), '5960 | clock')
