from django.contrib import admin
from django.urls import path,include
from django.conf.urls import handler404
from . import views
from django.conf import settings
from django.conf.urls.static import static

handler404 = views.handler404

urlpatterns = [
    path('admin/', admin.site.urls),
    path("",views.Home,name="home"),
    path("",include("user.urls")),
    path("games/",include("games.urls")),
]

urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)