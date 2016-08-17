from django.conf import settings
import subprocess
import errno


def get_url(game):
    try:
        output = subprocess.check_output(['./test-bin/minikube', 'service', 'game-%s' % game, '--url'])
    except subprocess.CalledProcessError:
        pass
    except OSError as e:
        if errno.ERONT != e.errno:
            raise
    else:

        return (output.strip(), '/game/%s/socket.io' % game)
    return ('http://localhost:%d' % (6001 + int(id) * 1000), '/socket.io')

#: URL function for locating the game server, takes one parameter `game`
GAME_SERVER_LOCATION_FUNCTION = getattr(
    settings,
    'AIMMO_GAME_SERVER_LOCATION_FUNCTION',
    get_url
)

CREATOR_AUTH_TOKEN = getattr(settings, 'CREATOR_AUTH_TOKEN', 'insecure-creator-auth-token')

MAX_LEVEL = 1
