from django.shortcuts import render
from user.models import Profile

# Create your views here.


def Home(request):
    games = [
        {
            'name': 'Call Break',
            'description': 'A trick-taking card game popular in South Asia.',
            'image_url': 'images/callbreak.png',
            'id':"callbreak"
        },
        {
            'name': 'Ludo',
            'description': 'A classic board game for 2-4 players.',
            'image_url': 'images/ludo.png',
            'id':'ludo',
        },
        {
            'name': 'Puzzle Solver',
            'description': 'Test your problem-solving skills with various puzzles.',
            'image_url': 'images/puzzle.png',
            'id':"puzzlesolver"
        },
    ]
    if request.user.is_authenticated:
        user_profile, created = Profile.objects.get_or_create(user=request.user)
        return render(request, 'home.html', {'games': games,'title':"Home",'user_profile': user_profile,})
    else:
         return render(request, 'home.html', {'games': games,'title':"Home",})




def handler404(request, exception):
    return render(request, 'notfound.html', status=404)