from django.urls import path,include
from . import views

urlpatterns = [
    path("callbreak/",include("callbreak.urls")),
]