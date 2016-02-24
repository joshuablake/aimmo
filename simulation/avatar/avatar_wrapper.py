from StringIO import StringIO
import traceback
import sys

import docker
from io import BytesIO

from simulation.action import WaitAction


# This class will be implemented by the player
Avatar = None


class UserCodeException(Exception):
    def __init__(self, *args, **kwargs):
        super(Exception, self).__init__(*args, **kwargs)
        self.exc_type, self.exc_value, self.exc_traceback = sys.exc_info()

    def to_user_string(self):
        lines = traceback.format_exception(self.exc_type, self.exc_value, self.exc_traceback)
        return '<br/>'.join(lines)


class AvatarWrapper(object):
    """
    The application's view of a character, not to be confused with "Avatar", the player-supplied code.
    """

    def __init__(self, initial_location, initial_code, player_id, avatar_appearance):
        self.location = initial_location
        self.health = 5
        self.score = 0
        self.events = []
        self.player_id = player_id
        self.avatar_appearance = avatar_appearance
        self.avatar = None

        self.set_code(initial_code)

    def handle_turn(self, state):
        try:
            next_action = self.avatar.handle_turn(state, self.events)
        except Exception as e:
            # TODO: tell user their program threw an exception during execution somehow...
            print('avatar threw exception during handle_turn:', e)
            traceback.print_exc()
            next_action = WaitAction()
        # Reset event log
        self.events = []

        return next_action

    def die(self, respawn_location):
        # TODO: extract settings for health and score loss on death
        self.health = 5
        self.score = max(0, self.score - 2)
        self.location = respawn_location

    def add_event(self, event):
        self.events.append(event)

    def set_code(self, code):
        self.code = code
        try:
            exec(code)
            self.avatar = Avatar()
        except Exception as ex:
            raise UserCodeException("Exception in user code", ex)

    def set_code_2(self, code):
        self.code = code

        import tarfile

        def add_string_to_tar(string, name, tar):
            tar_info = tarfile.TarInfo(name=name)
            tar_info.size = len(string)
            tar.addfile(tar_info, fileobj=StringIO(string))

        docker_file = '''
FROM python:2.7

RUN mkdir -p /usr/src/app
WORKDIR /usr/src/app
ADD avatar.py avatar.py
CMD ["python", "avatar.py"]'''

        tar_buffer = BytesIO()
        tar = tarfile.open(fileobj=tar_buffer, mode='w')

        add_string_to_tar(docker_file, 'dockerfile', tar)
        add_string_to_tar(code, 'avatar.py', tar)

        tar.close()
        tar_buffer.seek(0)

        tls_config = docker.tls.TLSConfig(client_cert=('''C:\Users\c.brett\.docker\machine\certs\cert.pem''', '''C:\Users\c.brett\.docker\machine\certs\key.pem'''), verify=False)
        client = docker.Client('https://192.168.99.100:2376', tls=tls_config)
        client.pull('python:2.7')
        USER_CODE_IMAGE = 'aimmo-avatar-code'
        client.build(fileobj=tar_buffer, custom_context=True, tag=USER_CODE_IMAGE)
        container = client.create_container(image=USER_CODE_IMAGE)
        client.start(container.get('Id'))
        import time
        time.sleep(5)
        print 'logs', repr(client.logs(container=container.get('Id')))

    def __repr__(self):
        return 'Avatar(id={}, location={}, health={}, score={})'.format(self.player_id, self.location,
                                                                        self.health, self.score)

if __name__ == '__main__':
    from simulation.location import Location
    a = AvatarWrapper(Location(2, 2), 'class Avatar:pass', None, 1)
    a.set_code_2('print("code!!!")')
