from rest_api.models import DockerfileBuild


def update_status_by_imageId(image_id, status):
    try:
        # Update status in the database
        db_instance = DockerfileBuild.objects.get(image_id=image_id)
        db_instance.status = status
        db_instance.save()
    except DockerfileBuild.DoesNotExist:
        print(f"DockerfileBuild with image_id '{image_id}' not found in the database.")
    except Exception as e:
        print(f"Error updating status in the database: {str(e)}")

def update_status_imageId_by_build_id(id, image_id,status):
    try:
        # Update status in the database
        db_instance = DockerfileBuild.objects.get(id=id)
        db_instance.status = status
        db_instance.image_id = image_id
        db_instance.save()
    except DockerfileBuild.DoesNotExist:
        print(f"DockerfileBuild with id '{id}' not found in the database.")
    except Exception as e:
        print(f"Error updating status in the database: {str(e)}")