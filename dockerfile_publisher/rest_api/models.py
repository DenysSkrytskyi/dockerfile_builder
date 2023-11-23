from django.db import models

# Create your models here.

class DockerfileBuild(models.Model):

    username = models.CharField(max_length=128, blank=False)
    file = models.FileField(upload_to='dockerfiles/', default=None)               # location where to store the Dockerfile
    image_id = models.CharField(max_length=128, null=True)
    status = models.CharField(max_length=50, null=True)
    created_at = models.DateTimeField(auto_now_add=True)
