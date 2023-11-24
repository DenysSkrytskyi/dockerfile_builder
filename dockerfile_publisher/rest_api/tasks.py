import datetime
import os
from celery import shared_task
import docker

from .services.build_status_update import update_status_by_imageId, update_status_imageId_by_build_id
from .config import DOCKER_HUB_REPO

from .models import DockerfileBuild

@shared_task
def build_docker_image(dockerfile_path, dockerfile_build_id, docker_username, docker_pass, docker_repo):

    print("========Task: build_docker_image========")
    print(f'File that is used for a build {dockerfile_path}')

    # Create Docker client
    client = docker.from_env()
    
    try:
        client.login(username=docker_username, password=docker_pass)
    except docker.errors.APIError as e:
        print(f"Error logging in to Docker registry: {e}")


    # Create tag
    current_time = datetime.datetime.now().strftime("%Y%m%d%H%M%S")
    tag = f"{docker_repo}:{current_time}" 

    # Build the Image
    try:
        image, build_log = client.images.build(
            path = os.path.dirname(dockerfile_path),
            dockerfile=os.path.basename(dockerfile_path),
            tag=tag,
            nocache = True,                             # Don’t use the cache
            forcerm = True,                             # Remove intermediate containers.    
        )

        #Update status in database
        update_status_imageId_by_build_id(id=dockerfile_build_id, image_id=image.id,status="Image successfully built. To be published.")

        return image.id         #this return is passed to chained function
    
    except docker.errors.BuildError as e :
        update_status_imageId_by_build_id(id = dockerfile_build_id, image_id="0000", status=e)
        print(f"Error building Docker image: {e}") 
    except Exception as e:
        update_status_imageId_by_build_id(id=dockerfile_build_id, image_id="0000", status=e)
        print(f"An error occurred: {e}")
    return None

@shared_task
def publish_docker_image(image_id):

    print("========Task: publish_docker_image========")

    # Create Docker client
    client = docker.from_env()

    try:
        # Find image
        image_details = client.images.get(name = image_id)

        registry_image_tag = image_details.attrs['RepoTags'][0]

        # Logs of pushing to the Docker Hub 
        for line in client.images.push(registry_image_tag, stream=True, decode=True):
            print(line)  # Print push progress

        #Update status in database
        update_status_by_imageId(image_id=image_id, status="Docker Image is successfully pushed to Docker Hub.")
    except Exception as e:
        # Update status to indicate error
        update_status_by_imageId(image_id=image_id, status=f"Error: {str(e)}")
        return str(e)
    return None