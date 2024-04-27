from channels.generic.websocket import AsyncWebsocketConsumer
import json
from asgiref.sync import sync_to_async
from django.core.serializers import serialize
from django.db.models import F
import random
from channels.db import database_sync_to_async
from channels.layers import get_channel_layer

class CallbreakConsumer(AsyncWebsocketConsumer):
    async def connect(self):
        self.room_number = self.scope['url_route']['kwargs'].get('room_number')
        self.user_name = self.scope['url_route']['kwargs'].get('user_name')

        print(self.channel_name)

        # Join room group
        await self.channel_layer.group_add(
            f'callbreak_rooms_{self.room_number}',
            self.channel_name
        )
        await self.update_player_channel_name(self.channel_name)
        # Accept the connection
        await self.accept()


        # Retrieve player information for the room
        player_data = await sync_to_async(self.get_players_in_room_data)(self.room_number)

        # Send player information to the newly connected user
        await self.send(text_data=json.dumps({
            'connected_users': player_data
        }))

        await self.send(text_data=json.dumps({
            "channel_name":self.channel_name
        }))

        # Send player information to the group
        await self.channel_layer.group_send(
            f'callbreak_rooms_{self.room_number}',
            {
                'type': 'handle.players.update',  # Consistent message type
                'data': player_data,
                'connected_user': self.user_name,
            }
        )
        print("connected")

    async def disconnect(self, close_code):
            await self.handle_disconnect()
    


    async def handle_disconnect(self):
        # Remove the player from the room
        await sync_to_async(self.remove_player_from_room)(self.room_number, self.user_name)

        # Leave room group
        await self.channel_layer.group_discard(
            f'callbreak_rooms_{self.room_number}',
            self.channel_name
        )
         # Retrieve player information for the room
        player_data = await sync_to_async(self.get_players_in_room_data)(self.room_number)
        # Send message to room group about user leaving
        await self.channel_layer.group_send(
            f'callbreak_rooms_{self.room_number}',
            {
                'type': 'handle.players.update',  # Consistent message type
                'data': player_data,
                'connected_user': self.user_name,
            }
        )

    def remove_player_from_room(self, room_number, user_name):
        from callbreak.models import RoomPlayer, Room
        try:
            # Remove the player from the room
            disconnectedPlayer=RoomPlayer.objects.filter(room__room_number=room_number, player__user__username=user_name)
            # Delete the player from the RoomPlayer model
            disconnectedPlayer.delete()
            # Decrement the current players count in the Room model
            room=Room.objects.get(room_number=room_number)
            room.current_players=room.current_players-1
            room.save()

            connectedRoomPlayers=RoomPlayer.objects.filter(room__room_number=room_number)
            if connectedRoomPlayers.count()==0:
                room.delete()
            for roomplayer in connectedRoomPlayers:
                print(roomplayer.channel_name,roomplayer.player.user.username)

        except Exception as e:
            print(f"Error removing player from room: {e}")



    async def user_joined(self, event):
        user_name = event['user_name']
        message = event['message']

        # Send message to WebSocket
        await self.send(text_data=json.dumps({
            'user_joined': user_name,
            'message': message
        }))

    async def user_left(self, event):
        user_name = event['user_name']
        message = event['message']

        # Send message to WebSocket
        await self.send(text_data=json.dumps({
            'user_left': user_name,
            'message': message
        }))

    async def handle_players_update(self, event):
        # Send the player data to all users in the room
        await self.send(text_data=json.dumps({
            'players_update': event['data']
        }))

    async def receive(self, text_data):
    # Parse the received JSON message
        text_data_json = json.loads(text_data)
        action = text_data_json.get('action')

        # Check if the action is for changing the page
        if action == 'change_page':
            # Broadcast the message to the entire group
            await self.channel_layer.group_send(
                f'callbreak_rooms_{self.room_number}',
                {
                    'type': 'change_page',
                }
            )
        elif action == 'distribute_cards':
            await self.distribute_cards(self.room_number)
            print("Distribute cards Request sent from client")
        elif action=="card_thrown":
            card_info = text_data_json['card']
            await self.channel_layer.group_send(
                 f'callbreak_rooms_{self.room_number}',
                {
                    'type': 'send_card_info',
                    'card_info': card_info,
                    'user_info': self.channel_name,
                }
            )
        elif action=="bid_count":
            bid_count=text_data_json['bid_count']
            await self.channel_layer.group_send(
                    f'callbreak_rooms_{self.room_number}',
                    {
                        'type': 'send_bid_count',
                        'bid_count': bid_count,
                        'user_info': self.channel_name,
                    }
            )
        elif action == 'players_order_list':
            self.players_order_list=text_data_json['order_list']
        elif action == 'make_me_active':
            player=text_data_json['player']
            print("make Me active : ",player)
            await self.channel_layer.group_send(
                    f'callbreak_rooms_{self.room_number}',
                    {
                        'type': 'active_player',
                        'player': player,
                    }
            )
        elif action=='send_cards_for_evaluation':
            cards=text_data_json['all_thrown_cards']
            from callbreak.cardmanager import winner_card_index
            cardsOnly=[]
            for card in cards:
                cardsOnly.append(card['card'])
            winner=cards[winner_card_index(cardsOnly)]
            winner_user=winner['user']
            await self.channel_layer.group_send(
                    f'callbreak_rooms_{self.room_number}',
                    {
                        'type': 'winner_player',
                        'player': winner_user,
                    }
            )
            await self.channel_layer.group_send(
                    f'callbreak_rooms_{self.room_number}',
                    {
                        'type': 'reset_thrownCards',
                    }
            )
        elif(action=="update_win_count"):
            win_count=text_data_json['win_count']
            await self.channel_layer.group_send(
                    f'callbreak_rooms_{self.room_number}',
                    {
                        'type': 'update_win_count',
                        "win_count":win_count,
                        'player': self.channel_name,
                    }
            )
        else:
            # Handle other actions as needed
            pass
    

    async def update_win_count(self,event):
        win_count=event['win_count']
        player=event['player']
        await self.send(text_data=json.dumps({
            'action': 'update_win_count',
            'win_count': win_count,
            'player': player,
        }))

    async def reset_thrownCards(self,event):
        await self.send(text_data=json.dumps({
            'action': 'reset_thrownCards',
        }))

    
    async def winner_player(self,event):
        player=event['player']
        print(player)
        await self.send(text_data=json.dumps({
            'action': 'winner_player',
            'winner_player': player,
        }))


    async def active_player(self,event):
        player=event['player']
        await self.send(text_data=json.dumps({
            'action': 'active_player',
            'active_player': player,
        }))


    async def send_bid_count(self,event):
        bid_count=event['bid_count']
        user_info=event['user_info']
        await self.send(text_data=json.dumps({
            'action': 'bid_count',
            'bid_count': bid_count,
            'user_info': user_info,
        }))
    async def send_card_info(self,event):
        # extract the information from event
        card_info = event['card_info']
        user_info = event['user_info']
        # Send the card and user information to the WebSocket
        await self.send(text_data=json.dumps({
            'action': 'card_thrown',
            'card': card_info,
            'user': user_info,
        }))


    async def change_page(self, event):
        # Redirect the user to another page
        await self.send(text_data=json.dumps({
            'redirect': 'initiateGame',
            'room_number': self.room_number,
        }))


    def get_players_in_room_data(self, room_number):
        from callbreak.models import RoomPlayer
        try:
            room_players = RoomPlayer.objects.filter(room__room_number=room_number).select_related('player__user__profile')
        except RoomPlayer.DoesNotExist:
            print(f"No players found in room {room_number}")
            return []
        player_data = []
        for room_player in room_players:
            profile = room_player.player.user.profile
            player_data.append({
                'username': room_player.player.user.username,
                'profile_image': profile.profile_picture.url if profile.profile_picture else None,
                'is_online': room_player.player.is_online,
                'channel_name':room_player.channel_name,                
            })
        return player_data
    

    def create_room_player(self, room_number, user_name):
        from callbreak.models import Room, RoomPlayer
        from user.models import Player
        from games.models import Game
        # Add the user to the room
        try:
            player = Player.objects.get(user__username=user_name)
            game,game_created=Game.objects.get_or_create(name="callbreak")
            room,room_created = Room.objects.get_or_create(room_number=room_number,creator=player,game=game[0],)
            room.current_players=room.current_players+1
            room.save()

            channel_name=self.channel_name
            RoomPlayer.objects.create(room=room, player=player,channel_name=channel_name)
        except Exception as e:
            print(f"Error adding user to room: {e}")


    async def distribute_cards(self, room_number):
        from callbreak.cardmanager import generate_deck, shuffle_deck
        from callbreak.models import RoomPlayer

        
        print("Distributing cards")
        # get all the players in the room
        players_channels=await sync_to_async(self.get_channel_names_for_room)(self.room_number)
        
        player_data = await sync_to_async(self.get_players_in_room_data)(self.room_number)

        cards = shuffle_deck(generate_deck())  
        cards_per_player = 13

        # Broadcast the distributed cards to all users in the room
        for i, player_channel in enumerate(players_channels):
            player_cards = cards[i * cards_per_player: (i + 1) * cards_per_player]
            
            # extract the channel name of the player
            room_player_channel_name=player_channel['channel_name']
            print(room_player_channel_name)
            # Send the distributed cards to the specific player
            await self.channel_layer.send(
                room_player_channel_name,  # Use player's channel name to send cards to them individually
                {   'type': 'cards_distributed_to_client',
                    'cards': player_cards,
                    'players_info':player_data,
                }
            )

        print("Card Distribution Finished.")

    async def cards_distributed_to_client(self, event):

        players_channels=await sync_to_async(self.get_channel_names_for_room)(self.room_number)

        print("Internal Card Distribution Started")
        cards = event['cards']
        players_info=event['players_info']
        # Send the distributed cards to all users in the room
        await self.send(text_data=json.dumps({
            'distributed_cards_to_client': cards,
            'players_info':players_info,
        }))
        print("Internal Card Distribution Ented")


    @database_sync_to_async
    def update_player_channel_name(self, channel_name):
        from django.contrib.auth.models import User
        from user.models import Player
        from callbreak.models import Room, RoomPlayer
        from games.models import Game
        
        try:
            user_instance = (User.objects.get)(username=self.user_name)
            player_instance = (Player.objects.get)(user=user_instance)

            game,game_created=Game.objects.get_or_create(name="callbreak")

            
            room_instance,room_created = (Room.objects.get_or_create)(room_number=self.room_number)
            if(room_created):
                room_instance.creator=player_instance
                room_instance.game=game

            # if room player donot exitst 
            room_player_instance, room_player_created = RoomPlayer.objects.get_or_create(room=room_instance, player=player_instance)

            if(room_player_created):
                room_instance.current_players=room_instance.current_players+1
                room_instance.save()

            room_player_instance.channel_name = channel_name
            room_player_instance.save()
            # Update RoomPlayer instance
            print("Channel_Name Changed")
        except Exception as e:
            print(f"Error updating channel name of Room user: {e}")
 
    
    def get_channel_names_for_room(self,room_number):
        from callbreak.models import RoomPlayer
        try:
            room_players = RoomPlayer.objects.filter(room__room_number=room_number)
        except RoomPlayer.DoesNotExist:
            print(f"No players found in room {room_number}")
            return []
        channel_names = []
        for room_player in room_players:
            channel_names.append({
                'channel_name':room_player.channel_name
            })
        
        return channel_names
    
    
    





    



    
        




       

    