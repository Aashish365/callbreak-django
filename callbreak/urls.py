from django.urls import path,include
from . import views

urlpatterns = [
    path("",views.callbreak_home,name="callbreak_home"),
    path("create-room/",views.create_room,name="create_room"),
    path("callbreak-creator-room/<str:room_number>",views.callbreak_creator_room,name="callbreak_creator_room"),
    path("callbreak-joinee-room/<str:room_number>",views.callbreak_joinee_room,name="callbreak_joinee_room"),
    path('join-room/<str:room_number>', views.join_room, name='join_room'),
    path("decline-room/<str:room_number>",views.declineRequest,name="decline_room"),
    path('send-invitation/<str:room_number>/<str:receiver_name>', views.send_invitation, name='send_invitation'),
    path("get_unread_invitations_count",views.get_unread_invitations_count,name="get_unread_invitations_count"),
    path("get_unread_invitations",views.get_unread_invitations,name="get_unread_invitations"),

]