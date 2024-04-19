from django.urls import path
from . import views

urlpatterns = [
    path("login", views.Login,name='login'),
    path('register', views.Register,name='register'),
    path('logout', views.Logout, name='logout'),
    path('profile', views.PublicProfile, name='profile'),
    path('update-profile/', views.update_profile, name='update_profile'),
    path('search_users/', views.search_users, name='search_users')
]