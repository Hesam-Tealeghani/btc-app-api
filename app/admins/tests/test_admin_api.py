import tempfile
import os
from PIL import Image
from django.test import TestCase
from django.contrib.auth import get_user_model
from django.urls import reverse
from rest_framework.test import APIClient
from rest_framework import status

from admins.serializers import AdminSerializer, ProfileSerializer

ADMIN_LIST_URL = reverse('admins:list')
CREATE_ADMIN_URL = reverse('admins:create')
MY_PROFILE_URL = reverse('admins:me')
TOKEN_URL = reverse('admins:token')

def image_upload_url(admin_id):
    """return url for the admin image upload"""
    return reverse('admins:admin-upload-image', args=[admin_id])

def create_admin(**params):
    return get_user_model().objects.create_user(**params)

def create_super_user(**params):
    return get_user_model().objects.create_superuser(**params)


class PrivateAdminApiTest(TestCase):
    """Test for the admins api (private - only superusers can create admins)"""

    def login_super_user(self):
        """To Create and log in as a superuser"""
        superuser = create_super_user(
            username='superuser',
            email='email@super.user',
            password='12345687super'
        )
        self.client.force_authenticate(user=superuser)

    def setUp(self):
        self.client = APIClient()
    
    def super_user_required(self):
        """Test that it is required to be a superuser to create a new user"""
        payload = {
            'username': 'testuser',
            'name': 'test user',
            'email': 'test@user.com',
            'password': 'test1234password'
        }
        response = self.client.post(CREATE_ADMIN_URL, payload)
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)
        admin = create_admin(username='testuser',
                             name='test',
                             email='test@admin.com',
                             password='1234password'
                            )
        self.client.force_authenticate(user=admin)
        response = self.client.post(CREATE_ADMIN_URL, payload)
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

    def test_create_valid_admin(self):
        """Test creating a admins with valid payloads (json) is successful"""
        self.login_super_user()
        payload = {
            'username': 'testuser',
            'name': 'test user',
            'email': 'test@user.com',
            'password': 'test1234password'
        }
        response = self.client.post(CREATE_ADMIN_URL, payload)
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        admin = get_user_model().objects.get(id=response.data['id'])
        self.assertTrue(admin.check_password(payload['password']))
        self.assertNotIn('password', response.data)
    
    def test_admin_already_exist(self):
        """Testing Can not create an admin that exists."""
        payload = {
            'username': 'testuser',
            'name': 'test user',
            'email': 'test@user.com',
            'password': 'test1234password'
        }
        create_admin(**payload)
        self.login_super_user()
        response = self.client.post(CREATE_ADMIN_URL, payload)
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
    
    def test_short_password(self):
        """Testing that the admin should use a password with at least 6 characters"""
        payload = {
            'username': 'testuser',
            'name': 'test user',
            'email': 'test@user.com',
            'password': '12345'
        }
        self.login_super_user()
        response = self.client.post(CREATE_ADMIN_URL, payload)
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        admincreated = get_user_model().objects.filter(
            username=payload['username']
        ).exists()
        self.assertFalse(admincreated)
    
    def test_create_token_for_admin(self):
        """Test to get a token when the admin login"""
        payload = {
            'username': 'test',
            'email': 'test@test.com',
            'password': 'a1234test'
        }
        create_admin(**payload)
        response = self.client.post(TOKEN_URL, payload)
        self.assertIn('token', response.data)
        self.assertEqual(response.status_code, status.HTTP_200_OK)

    def test_create_token_for_invalid(self):
        """Test that the token is not created for invalid credentials (wrong password and username)"""
        create_admin(username='testusername', email='test@test.com', password='test124pas')
        payload = {
            'username': 'testusername',
            'email': 'test@test.com',
            'password': 'test1234pas'
        }
        response = self.client.post(TOKEN_URL, payload)
        self.assertNotIn('token', response.data)
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

        payload = {
            'username': 'wrongtest',
            'password': 'doesnotmatter',
            'email': 'doesnt@matter.either'
        }
        response = self.client.post(TOKEN_URL, payload)
        self.assertNotIn('token', response.data)
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
    
    def test_authentication_needed_for_profile(self):
        """Test that authentication is needed to see and update profile"""
        response = self.client.get(MY_PROFILE_URL)
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)
    
    def test_login_required_for_promoting(self):
        """Test that a normal admin or unauthorized can not promote or demote"""
        admin = create_admin(
            username='testadmin',
            name='test admin',
            email='test@admin.com',
            password='admin1234admin',
            phone='12345678',
            postal_code='123321',
            birth_date='2000-01-01',
            address='world, world',
            title='tester'
        )
        testuser = create_admin(
            username='testuser',
            name='test user',
            email='test@user.com',
            password='user1234',
            phone='12345678',
            postal_code='123321',
            birth_date='2000-01-01',
            address='world, world',
            title='tester'
        )
        response = self.client.post(reverse('admins:deactive', args=[testuser.id]))
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)
        
        self.client.force_authenticate(user=admin)
        response = self.client.post(reverse('admins:deactive', args=[testuser.pk]))
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)
    
    def test_superuser_required_for_admin_list(self):
        """Test that only superusers can see the admins list"""
        admin = create_admin(
            username='testadmin',
            name='test admin',
            email='test@admin.com',
            password='admin1234admin',
            phone='12345678',
            postal_code='123321',
            birth_date='2000-01-01',
            address='world, world',
            title='tester'
        )
        testuser = create_admin(
            username='testuser',
            name='test user',
            email='test@user.com',
            password='user1234',
            phone='12345678',
            postal_code='123321',
            birth_date='2000-01-01',
            address='world, world',
            title='tester'
        )
        response = self.client.get(ADMIN_LIST_URL)
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

        self.client.force_authenticate(user=admin)
        response = self.client.get(ADMIN_LIST_URL)
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

        self.login_super_user()
        response = self.client.get(ADMIN_LIST_URL)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        admins = get_user_model().objects.all().order_by('name')
        adminserialized = ProfileSerializer(admins, many=True)
        self.assertEqual(response.data, adminserialized.data)
        

class PrivateAdminProfileApi(TestCase):
    """Test the profile for authorized admin"""

    def setUp(self):
        self.admin = create_admin(
            username='testadmin',
            name='test admin',
            email='test@admin.com',
            password='admin1234admin',
            phone='12345678',
            postal_code='123321',
            birth_date='2000-01-01',
            address='world, world',
            title='tester'
        )
        self.client = APIClient()
        self.client.force_authenticate(user=self.admin)
    
    def test_retrieve_profile_success(self):
        """Test retrieving profile for logged in admin"""
        response = self.client.get(MY_PROFILE_URL)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data, AdminSerializer(self.admin).data)

    def test_post_profile_not_allowed(self):
        """Test that post method is not allowed on this url"""
        response = self.client.post(MY_PROFILE_URL)
        self.assertEqual(response.status_code, status.HTTP_405_METHOD_NOT_ALLOWED)

    def test_updating_admin_profile(self):
        """Test updating admin profile for logged in admins"""
        payload = {
            'name':'new name test',
            'email':'changed@test.com',
            'password':'newadminpassword'
        }
        response = self.client.patch(MY_PROFILE_URL, payload)
        self.admin.refresh_from_db()
        self.assertEqual(self.admin.name, payload['name'])
        self.assertTrue(self.admin.check_password(payload['password']))
        self.assertEqual(response.status_code, status.HTTP_200_OK)


class PrivateSuperUserUpdates(TestCase):
    """The Test for superuser options"""
    def setUp(self):
        """To create and authenticate as a superuser."""
        self.admin = create_super_user(
            username='testsuper',
            name='test super',
            email='super@admin.com',
            password='adminsuper1234admin',
            phone='12345678',
            postal_code='123321',
            birth_date='2000-01-01',
            address='world, world',
            title='tester'
        )
        self.client = APIClient()
        self.client.force_authenticate(user=self.admin)

    def test_changing_admin(self):
        """ Test that a 
        1. superuser can promote an admin or
        2. demote a superuser that is created by himself
        3. deavtivate an admin
        4. activate an admin """
        sample_admin = create_admin(
            username='sampleuper',
            name='test user',
            email='user@admin.com',
            password='admin1234admin',
            phone='12345678',
            postal_code='123321',
            birth_date='2000-01-01',
            address='world, world',
            title='tested'
        )
        response = self.client.post(reverse('admins:promote', kwargs={'pk': sample_admin.id}))
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        sample_admin.refresh_from_db()
        self.assertEqual(sample_admin.is_staff, True)

        response = self.client.post(reverse('admins:promote', kwargs={'pk': sample_admin.id}))
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        sample_admin.refresh_from_db()
        self.assertEqual(sample_admin.is_staff, False)

        response = self.client.post(reverse('admins:deactive', kwargs={'pk': sample_admin.id}))
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        sample_admin.refresh_from_db()
        self.assertEqual(sample_admin.is_active, False)

        response = self.client.post(reverse('admins:deactive', kwargs={'pk': sample_admin.id}))
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        sample_admin.refresh_from_db()
        self.assertEqual(sample_admin.is_active, True)


class AdminImageUploadTest(TestCase):
    """Test for uploadin images"""

    def setUp(self):
        self.client = APIClient()
        self.admin = create_super_user(
            username='testsuper',
            name='test super',
            email='super@admin.com',
            password='adminsuper1234admin',
            phone='12345678',
            postal_code='123321',
            birth_date='2000-01-01',
            address='world, world',
            title='tester'
        )
        self.client.force_authenticate(self.admin)

    def tearDown(self):
        self.admin.image.delete()
    
    # def test_upload_image(self):
    #     """Test Uploading an image to profile of admin"""
    #     url = image_upload_url(self.admin.id)
    #     with tempfile.NamedTemporaryFile(suffix='.jpg') as ntf:
    #         img = Image.new('R GB', (10, 10))
    #         img.save(ntf, format='JPEG')
    #         ntf.seek(0)
    #         response = self.client.post(url, {'image': ntf}, format='multipart')
    #         self.admin.refresh_from_db()
    #         self.assertEqual(response.status_code, status.HTTP_200_OK)
    #         self.assertIn('image', response.data)
    #         self.assertTrue(os.path.exists(self.admin.image.path))
