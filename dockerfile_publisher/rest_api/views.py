import os

from rest_framework.response import Response
from rest_framework.decorators import api_view

from celery import chain

import docker
from docker.errors import ImageNotFound

from .tasks import build_docker_image, publish_docker_image
from .serializer import DockerfileBuildSerializer
from .models import DockerfileBuild


@api_view(["POST","GET","DELETE"])
def dockerfile_builds(request):

    if request.method == "POST":

        if request.headers["Content-Type"].split(';')[0] == "multipart/form-data":

            # Map payload to Serializer
            instance = DockerfileBuildSerializer(data=request.data)

            if instance.is_valid():

                # Save initial data to Database with file and username from payload
                saved_instance=instance.save()
                
                # Update status in database
                saved_instance.status = "Build is starting"
                saved_instance.save() 

                # Chain the tasks: 1st building docker image, 2nd publishing docker image
                task_chain = chain(build_docker_image.s(saved_instance.file.path, saved_instance.id) | publish_docker_image.s())

                # Execute the chained tasks asynchronously
                result = task_chain.delay()

                return Response({"data": DockerfileBuildSerializer(saved_instance).data },status=202)

            else:
                return Response({"message": "File is not valid", "errors": instance.errors}, status=400)


        else:
            return Response({"message": f'Content-Type is not valid. Expected binary data, actual header is {request.headers["Content-Type"]}'}, status=400)


    elif request.method == "GET":
    
        dockerfile_build_id = request.query_params.get("dockerfile_build_id")

        # GET list of all builds details
        if dockerfile_build_id is None:

            data = DockerfileBuild.objects.all()
            serializer = DockerfileBuildSerializer(data, many=True)


            return Response({"data": serializer.data}, status=200)
        
        #GET dockerfile build process details by 'id'
        else:
            try:
                data = DockerfileBuild.objects.get(id=dockerfile_build_id)
            except DockerfileBuild.DoesNotExist:
                return Response({"message": f"Dockerfile build process with 'id = {dockerfile_build_id}' is not found."}, status=404)

            serializer = DockerfileBuildSerializer(data)


            return Response({"data": serializer.data}, status=200)
        
    elif request.method == "DELETE":

        dockerfile_build_id = request.query_params.get("dockerfile_build_id")

        if dockerfile_build_id:

            # Try to retrieve the DockerImage with the specified image_id from Database
            try:
                dockerfile_build_db = DockerfileBuild.objects.get(id=dockerfile_build_id)
            except:
                return Response({"message": f"Missing 'dockerfile_build' in the Database with id = {dockerfile_build_id}."}, status=400)
            
            # Try to retrieve the DockerImage from local Docker
            try:    
                image_id = dockerfile_build_db.image_id
            except ImageNotFound:
                return Response({"message": "Docker Image is not found"},status = 404) 
            
            # Get dockerfile path
            file_path = dockerfile_build_db.file

            # Try to delete file from local storage
            try:
                os.remove(file_path.path)
            except Exception as e:
                return Response({"message": str(e)}, status=400)

            # Delete from Database
            dockerfile_build_db.delete()

            # Create Docker client to delete Image
            client = docker.from_env()

            # Attempt to remove the Docker image
            try:
                client.images.remove(image=image_id, force=True)    
            except Exception as e:
                return Response({"message": e},status=400)

            return Response({"message": f"Dockerfile, Docker Image and Database record was deleted successfully for 'dockerfile_build_id' = {dockerfile_build_id}."}, status=200)
                
        return Response({"message":"Missing query parameter 'dockerfile_build_id' in the DELETE request"}, status=400)
 