from channels.routing import ProtocolTypeRouter, URLRouter
from callbreak import consumers
from django.urls import re_path,path

websocket_urlpatterns = [
  re_path(r'ws/join-room/(?P<room_number>[-\w]+)/(?P<user_name>[-\w]+)/', consumers.CallbreakConsumer.as_asgi()),
]

application = ProtocolTypeRouter({
    "websocket": URLRouter(websocket_urlpatterns),
})
