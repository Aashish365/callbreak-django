from django.contrib import admin
from .models import Room,RoomPlayer,Invitation
# Register your models here.

admin.site.register(Room)
admin.site.register(RoomPlayer)
admin.site.register(Invitation)