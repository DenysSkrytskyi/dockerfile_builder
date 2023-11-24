import datetime
import os
from .models import DockerfileBuild
from rest_framework import serializers

class DockerfileBuildSerializer(serializers.ModelSerializer):
    class Meta:
        model = DockerfileBuild
        fields =['id', 'docker_username', 'docker_repo', 'file','image_id','status', 'created_at']


    def create(self,validated_data):
    
        # Create file name
        current_time = datetime.datetime.now().strftime("%Y%m%d%H%M%S")
        dockerfile_new_name = (
            validated_data['file'].name +
            '_' +
            validated_data['docker_username'] +
            '_' +
            current_time
        )

        # Create path to store Dockerfile (without actually saving the file)
        dockerfile_path = os.path.join('dockerfiles', dockerfile_new_name)

        # Save the path to the database
        validated_data['file'].name = dockerfile_path

        return super().create(validated_data)

 