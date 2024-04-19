from django.db import models
from django.contrib.auth.models import User
from django.db.models.signals import post_save
from django.dispatch import receiver


class Profile(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    profile_picture = models.ImageField(upload_to='profile_pics/', blank=True, null=True)
    full_name = models.CharField(max_length=100, blank=True)
    bio = models.TextField(blank=True)
    location = models.CharField(max_length=100, blank=True)
    interests = models.CharField(max_length=255, blank=True)
    social_media_links = models.URLField(max_length=200, blank=True)
    preferred_language = models.CharField(max_length=50, blank=True)
    date_of_birth = models.DateField(blank=True, null=True)
    occupation = models.CharField(max_length=100, blank=True)
    education = models.CharField(max_length=100, blank=True)

    def __str__(self):
        return self.user.username
    


class Player(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    is_online = models.BooleanField(default=False)
    def __str__(self):
        return self.user.username
    



@receiver(post_save, sender=User)
def create_player(sender, instance, created, **kwargs):
    if created:
        Player.objects.create(user=instance)