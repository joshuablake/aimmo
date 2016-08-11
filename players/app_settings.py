from django.conf import settings

#: URL function for locating the game server, takes one parameter `game`
GAME_SERVER_LOCATION_FUNCTION = getattr(
    settings,
    'AIMMO_GAME_SERVER_LOCATION_FUNCTION',
    lambda id: ('http://localhost:%d' % (6001 + int(id) * 1000), '/socket.io'),
)

CREATOR_AUTH_TOKEN = getattr(settings, 'CREATOR_AUTH_TOKEN', 'insecure-creator-auth-token')

MAX_LEVEL = 1
