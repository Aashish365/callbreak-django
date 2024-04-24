from django.db import models
from games.models import Game
from user.models import Player

# Create your models here.

import uuid

class Room(models.Model):
    id = models.AutoField(primary_key=True)
    game = models.ForeignKey(Game, on_delete=models.CASCADE)
    is_expired = models.BooleanField(default=False)
    max_players = models.PositiveIntegerField(default=4)
    current_players = models.PositiveIntegerField(default=0)
    creator = models.ForeignKey(Player, on_delete=models.CASCADE)
    room_number = models.UUIDField(default=uuid.uuid4, unique=True)

    def __str__(self):
        return f"{self.room_number} ({self.game})"
    




# class RoomPlayer(models.Model):
#     id = models.AutoField(primary_key=True)
#     room = models.ForeignKey(Room, on_delete=models.CASCADE)
#     player = models.ForeignKey(Player, on_delete=models.CASCADE)
#     score = models.IntegerField(default=0)

#     def __str__(self):
#         return f"{self.player} in {self.room}"
    
class RoomPlayer(models.Model):
    id = models.AutoField(primary_key=True)
    room = models.ForeignKey(Room, on_delete=models.CASCADE)
    player = models.ForeignKey(Player, on_delete=models.CASCADE)
    score = models.IntegerField(default=0)
    channel_name = models.CharField(max_length=255, blank=True, null=True)

    def __str__(self):
        return f"{self.player} in {self.room}"
    



class Invitation(models.Model):
    sender = models.ForeignKey(Player, on_delete=models.CASCADE, related_name='sent_invitations')
    receiver = models.ForeignKey(Player, on_delete=models.CASCADE, related_name='received_invitations')
    room = models.ForeignKey(Room, on_delete=models.CASCADE)
    timestamp = models.DateTimeField(auto_now_add=True)
    is_read = models.BooleanField(default=False)  # New field to track read status

    def __str__(self):
        return f"{self.sender} invited {self.receiver} to {self.room}"