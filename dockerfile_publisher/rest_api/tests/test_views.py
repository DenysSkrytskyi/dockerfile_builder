from time import sleep
from django.test import Client, TestCase
from django.urls import reverse
from rest_api.serializer import DockerfileBuildSerializer
from django.core.files.base import ContentFile


from rest_api.models import DockerfileBuild

class TestViews(TestCase):

    # will run before each test
    def setUp(self):

        self.client = Client()
        self.dockerfile_build_url =reverse('dockerfile-build')


    def test_GET_list_dockerfile_builds(self):

        response = self.client.get(self.dockerfile_build_url)
        self.assertEqual(response.status_code, 200)

    def test_GET_dockerfile_builds_by_id(self):  

        # create test data in test database
        DockerfileBuild.objects.create(username="usertest999", file="/dockerfiles/Dockerfile_denys677_20231123011442")

        response = self.client.get(f"{self.dockerfile_build_url}?dockerfile_build_id=1")
        self.assertEqual(response.status_code, 200)

    def test_GET_dockerfile_builds_by_id_not_found(self):
            
        response = self.client.get(f"{self.dockerfile_build_url}?dockerfile_build_id=2")
        self.assertEqual(response.status_code, 404)

    def test_POST_upload_build_publish_dockerfile(self):

        dockerfile_path = 'rest_api/tests/files/Dockerfile'

        # Read the contents of the file
        with open(dockerfile_path, 'rb') as file:
            file_content = file.read()

        # Create a ContentFile from the file content
        content_file = ContentFile(file_content, name='Dockerfile')

        # Include the file in the POST request
        response = self.client.post(self.dockerfile_build_url, {'username':'testuser123','file': content_file}, format='multipart')

        # Check the response status code
        self.assertEqual(response.status_code, 202)

        # Check if the instance is created in the database
        self.assertTrue(DockerfileBuild.objects.filter(username='testuser123').exists())

    def test_POST_400_dockerfile_validation(self):
        # Path to test pdf file
        dockerfile_path = 'rest_api/tests/files/Dockerfile.pdf'

        # Read the contents of the file
        with open(dockerfile_path, 'rb') as file:
            file_content = file.read()

        # Create a ContentFile from the file content
        content_file = ContentFile(file_content, name='Dockerfile.pdf')

        # Include the file in the POST request
        response = self.client.post(self.dockerfile_build_url, {'username':'usertest','file': content_file}, format='multipart')

        # Check the response status code
        self.assertEqual(response.status_code, 400)  # Adjust the expected status code
        self.assertEqual(response.json()['message'], 'File is not valid')

    def test_POST_400_content_type_validation(self):

        response = self.client.post(self.dockerfile_build_url, {'username':'usertest','file': 'Dockerfile'}, content_type='application/json')

        # Check the response status code
        self.assertEqual(response.status_code, 400)  
        self.assertEqual(response.json()['message'], 'Content-Type is not valid. Expected binary data, actual header is application/json')
    