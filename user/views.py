from django.contrib.auth import authenticate, login,logout
from django.shortcuts import render, redirect
from django.contrib.auth.models import User
from django.contrib.auth.decorators import login_required
from .models import Profile
from django.http import JsonResponse
from .models import Player


# Create your views here.

def Login(request):
    if request.user.is_authenticated: 
        return redirect('home')
    
    if request.method == 'POST':
        username = request.POST.get('username')
        password = request.POST.get('password')
        user = authenticate(request, username=username, password=password)
        if user is not None:
            login(request, user)
            player, created = Player.objects.get_or_create(user=user)
            player.is_online = True
            player.save()
            request.session['user_email'] = user.email
            request.session['user_full_name'] = user.get_full_name()
            return redirect('home')
        else:
            return render(request, 'login.html', {'error_message': 'Invalid username or password.','title':"Login"})
    else:
        return render(request, 'login.html',{ 'title':"Login"})
    


def Register(request):
    if request.user.is_authenticated: 
        return redirect('home')
    
    if request.method == 'POST':
        username = request.POST.get('username')
        password = request.POST.get('password')
        email = request.POST.get('email')

        if User.objects.filter(username=username).exists():
            return render(request, 'register.html', {'error_message': 'Username is already taken.','title':"Register"})
        if User.objects.filter(email=email).exists():
            return render(request, 'register.html', {'error_message': 'Email is already taken.','title':"Register"})
        
        user = User.objects.create_user(username=username, password=password, email=email)
        user.save()
        return redirect('login')
    else:
        return render(request, 'register.html',{ 'title':"Register"})


@login_required(login_url='login')
def PublicProfile(request):
    user_profile, created = Profile.objects.get_or_create(user=request.user)
    return render(request, 'privateProfile.html', {'user_profile': user_profile, 'title': "Profile"})


@login_required(login_url='login')
def Logout(request):
    player = request.user.player
    player.is_online = False
    player.save()

    if 'user_email' in request.session:
        del request.session['user_email']
    if 'user_full_name' in request.session:
        del request.session['user_full_name']
    logout(request)
    return redirect('login')





@login_required(login_url='login')
def update_profile(request):
  if request.method == 'POST':
    profile = request.user.profile
    # Update profile fields only if data has changed
    for field in ['bio', 'full_name', 'location', 'interests', 'social_media_links',
                  'preferred_language','date_of_birth', 'occupation', 'education']:
      new_value = request.POST.get(field, '')  # Get the posted value
      if new_value != getattr(profile, field):  # Compare with current value
        setattr(profile, field, new_value)  # Update if different

    # Handle profile picture separately (if uploaded)
    if 'profile_picture' in request.FILES:
      profile.profile_picture = request.FILES['profile_picture']
    

    # Save the updated profile
    profile.save()
    # Redirect to a success page (or handle success message)
    return redirect('profile')  # Assuming 'profile' is your success URL pattern name
  else:
    # Handle GET request (likely pre-populating the form)
    context = {'user_profile': request.user.profile}
    return render(request, 'update_profile.html', context)  # Assuming 'update_profile.html' is your template name





    
@login_required(login_url='login')
def search_users(request):
    if request.headers.get('x-requested-with') == 'XMLHttpRequest':
        search_query = request.GET.get('search_query', '')

        current_user = request.user
        # Perform case-insensitive search for usernames starting with the query
        players = Player.objects.filter(user__username__istartswith=search_query).exclude(user=current_user)

        # Prepare data to return
        users_data = []
        for player in players:
            profile = Profile.objects.filter(user=player.user).first()
            if profile:
                user_data = {
                    'username': player.user.username,
                    'profile_picture': profile.profile_picture.url if profile.profile_picture else '',
                    'is_online': player.is_online,
                    # You can add more fields from the profile or player model if needed
                }
                users_data.append(user_data)
            else:
                # Handle case where Profile object doesn't exist for the user
                user_data = {
                    'username': player.user.username,
                    'profile_picture': '',  # No profile picture available
                    'is_online': player.is_online,
                    # You can add more fields from the player model if needed
                }
                users_data.append(user_data)

        if not users_data:
            users_data = [{"username": "No matching result", "profile_picture": "", "is_online": False}]

        return JsonResponse({'users': users_data})
    else:
        return JsonResponse({'error': 'Not a valid AJAX request'})
