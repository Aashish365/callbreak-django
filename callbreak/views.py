from django.contrib.auth import authenticate, login,logout
from django.shortcuts import render, redirect,reverse
from django.contrib.auth.models import User
from django.contrib.auth.decorators import login_required
from user.models import Profile
from .models import Room, RoomPlayer,Invitation
from games.models import Game
from user.models import Player
from django.http import JsonResponse
import uuid




@login_required(login_url='login')
def callbreak_home(request):
    gameInfo={
            'name': 'Call Break',
            'description': 'A trick-taking card game popular in South Asia.',
            'image_url': 'images/callbreak.png',
            'id':"callbreak"
        }
    user_profile, created = Profile.objects.get_or_create(user=request.user)
    return render(request, 'callbreak_home.html',{ 'title':"Call Break",'game':gameInfo,'user_profile': user_profile})



@login_required(login_url='login')
def callbreak_creator_room(request, room_number):
    gameInfo = {
        'name': 'Call Break',
        'description': 'A trick-taking card game popular in South Asia.',
        'image_url': 'images/callbreak.png',
        'id': "callbreak"
    }
    user_profile, created = Profile.objects.get_or_create(user=request.user)
    return render(request, 'callbreak_creator_room.html', { 'title': "Call Break Room", 'game': gameInfo, 'user_profile': user_profile, 'room_number': room_number })    

@login_required(login_url='login')
def callbreak_joinee_room(request, room_number):
    gameInfo = {
        'name': 'Call Break',
        'description': 'A trick-taking card game popular in South Asia.',
        'image_url': 'images/callbreak.png',
        'id': "callbreak"
    }
    user_profile, created = Profile.objects.get_or_create(user=request.user)
    return render(request, 'callbreak_joinee_room.html', { 'title': "Call Break Room", 'game': gameInfo, 'user_profile': user_profile, 'room_number': room_number })    


    
@login_required(login_url='login')
def create_room(request):
    if request.method == 'POST':
        if request.user.is_authenticated:
            # Retrieve the Player instance corresponding to the logged-in user
            player = request.user.player
            
            try:
                # Attempt to get the Game instance
                game = Game.objects.get(name="callbreak")
            except Game.DoesNotExist:
                # If the Game instance does not exist, create a new one
                game = Game.objects.create(name="callbreak", is_active=True)

            # Create a new room
            room = Room.objects.create(
                game=game,
                creator=player,
            )

            # Create a RoomPlayer instance for the creator
            RoomPlayer.objects.create(
                room=room,
                player=player,
            )

            # Update current players count in the room
            room.current_players = RoomPlayer.objects.filter(room=room).count()
            room.save()

            # Redirect to the newly created room
            response=JsonResponse({'room_number': room.room_number})
            return response
        else:
            return JsonResponse({'error': 'User is not authenticated.'}, status=401)
    else:
        return JsonResponse({'error': 'Only POST requests are allowed.'}, status=400)


       

@login_required(login_url='login')
def join_room(request, room_number):
    if request.method == 'POST':
        # Assuming the user is logged in
        if request.user.is_authenticated:
            # Retrieve the Player instance corresponding to the logged-in user
            player = request.user.player
            
            # if player already joined the room
            if RoomPlayer.objects.filter(room__room_number=room_number,player=player).exists():
                return JsonResponse({'error': 'Player has already joined the room.'}, status=400)
            else:
                try:
                    # Get the room
                    room = Room.objects.get(room_number=room_number)

                    # Validate if the room is expired or at max capacity
                    if room.is_expired:
                        return JsonResponse({'error': 'Room is expired.'}, status=400)
                    if room.current_players >= room.max_players:
                        return JsonResponse({'error': 'Room is at max capacity.'}, status=400)

                    # Create a RoomPlayer instance for the player
                    RoomPlayer.objects.create(
                        room=room,
                        player=player,
                    )

                    # Update current players count in the room
                    room.current_players = RoomPlayer.objects.filter(room=room).count()
                    room.save()

                    # Generate a response
                    response_data = {
                        'room_number': room.room_number,
                    }

                    invitation = Invitation.objects.filter(room__room_number=room_number, receiver=player).first()
                    # If an invitation exists, delete it
                    if invitation:
                        invitation.delete()
                    return JsonResponse(response_data)
                except Room.DoesNotExist:
                    return JsonResponse({'error': 'Room does not exist.'}, status=404)
        else:
            return JsonResponse({'error': 'User is not authenticated.'}, status=401)
    else:
        return JsonResponse({'error': 'Only POST requests are allowed.'}, status=400)
    


@login_required(login_url='login')
def send_invitation(request, room_number, receiver_name):
    if request.method == 'POST':
        # Assuming the user is logged in
        if request.user.is_authenticated:
            # Retrieve the Player instance corresponding to the logged-in user
            sender = request.user.player
            receiver = Player.objects.get(user__username=receiver_name)
            # if player already joined the room
            if Invitation.objects.filter(room__room_number=room_number, sender=sender, receiver=receiver).exists():
                return JsonResponse({'error': 'Invitation already sent.'}, status=400)
            else:
                try:
                    # Get the room
                    room = Room.objects.get(room_number=room_number)
                    # Create an Invitation instance for the player
                    invitation = Invitation.objects.create(
                        room=room,
                        sender=sender,
                        receiver=receiver,
                    )
                    # Generate a response
                    response_data = {
                        'room_number': room.room_number,
                    }
                    return JsonResponse(response_data)
                except Room.DoesNotExist:
                    return JsonResponse({'error': 'Room does not exist.'}, status=404)
        else:
            return JsonResponse({'error': 'User is not authenticated.'}, status=401)
    else:
        return JsonResponse({'error': 'Only POST requests are allowed.'}, status=400)
    


@login_required(login_url='login')
def get_unread_invitations_count(request):
    if request.method != 'POST':
        return JsonResponse({'error': 'Only POST requests are allowed.'}, status=405)
    # Check if the user is authenticated
    if request.user.is_authenticated:
        # Retrieve the receiver (assuming Player is related to User)
        receiver = request.user.player

        # Count the unread invitations received by the receiver
        unread_count = Invitation.objects.filter(receiver=receiver, is_read=False).count()

        # Return the count as JSON response
        return JsonResponse({'unread_count': unread_count})
    else:
        return JsonResponse({'error': 'User is not authenticated.'}, status=401)
    

@login_required(login_url='login')
def get_unread_invitations(request):
    if request.method != 'POST':
        return JsonResponse({'error': 'Only POST requests are allowed.'}, status=405)
    # Check if the user is authenticated
    if request.user.is_authenticated:
        # Retrieve the receiver (assuming Player is related to User)
        receiver = request.user.player

        # Retrieve the unread invitations received by the receiver
        unread_invitations = Invitation.objects.filter(receiver=receiver, is_read=False)

        # Serialize the unread invitations
        unread_invitations_data = []
        for invitation in unread_invitations:
            print(invitation)
            unread_invitations_data.append({
                'sender': invitation.sender.user.username,
                'room_number': invitation.room.room_number,
                'timestamp': invitation.timestamp,
                'game_name':"Call-Break"
            })

        # Mark the unread invitations as read
        # unread_invitations.update(is_read=True)   update his part when user take action to the invitation.

        # Return the unread invitations as JSON response
        return JsonResponse({'unread_invitations': unread_invitations_data})
    else:
        return JsonResponse({'error': 'User is not authenticated.'}, status=401)
    


@login_required(login_url='login')
def declineRequest(request,room_number):
    if request.method == 'POST':
        # Assuming the user is logged in
        if request.user.is_authenticated:
            # Retrieve the Player instance corresponding to the logged-in user
            player = request.user.player
            # Find the invitation for the player and the room
            invitation = Invitation.objects.filter(room__room_number=room_number, receiver=player).first()
            # If an invitation exists, delete it
            if invitation:
                invitation.delete()
                # Generate a response
                response_data = {
                    'message': 'Successfully declined the room invitation.'
                }
                return JsonResponse(response_data)
            else:
                return JsonResponse({'error': 'No invitation found for this player and room.'}, status=404)
        else:
            return JsonResponse({'error': 'User is not authenticated.'}, status=401)
    else:
        return JsonResponse({'error': 'Only POST requests are allowed.'}, status=400)