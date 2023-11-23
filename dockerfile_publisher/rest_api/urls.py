from django.urls import path
from .views import dockerfile_builds

urlpatterns = [
    path("dockerfile-build/", dockerfile_builds, name='dockerfile-build'),
]
