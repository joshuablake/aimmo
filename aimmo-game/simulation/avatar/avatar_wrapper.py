import logging
import requests

from simulation.action import ACTIONS, MoveAction

LOGGER = logging.getLogger(__name__)


class AvatarWrapper(object):
    """
    The application's view of a character, not to be confused with "Avatar",
    the player-supplied code.
    """

    def __init__(self, player_id, initial_location, worker_url, avatar_appearance):
        self.player_id = player_id
        self.location = initial_location
        self.health = 5
        self.score = 0
        self.events = []
        self.avatar_appearance = avatar_appearance
        self.worker_url = worker_url
        self.fog_of_war_modifier = 0
        self._action = None

    @property
    def action(self):
        return self._action

    @property
    def is_moving(self):
        return isinstance(self.action, MoveAction)

    def decide_action(self, state_view):
        try:
            data = requests.post(self.worker_url, json=state_view).json()
        except ValueError as err:
            LOGGER.info('Failed to get turn result: %s', err)
            return False
        else:
            try:
                action_data = data['action']
                action_type = action_data['action_type']
                action_args = action_data.get('options', {})
                action_args['avatar'] = self
                action = ACTIONS[action_type](**action_args)
            except (KeyError, ValueError) as err:
                LOGGER.info('Bad action data supplied: %s', err)
                return False
            else:
                self._action = action
                return True

    def clear_action(self):
        self._action = None

    def die(self, respawn_location):
        # TODO: extract settings for health and score loss on death
        self.health = 5
        self.score = max(0, self.score - 2)
        self.location = respawn_location

    def add_event(self, event):
        self.events.append(event)

    def serialise(self):
        return {
            'events': [
                #    {
                #        'event_name': event.__class__.__name__.lower(),
                #        'event_options': event.__dict__,
                #    } for event in self.events
            ],
            'health': self.health,
            'location': self.location.serialise(),
            'score': self.score,
        }

    def __repr__(self):
        return 'Avatar(id={}, location={}, health={}, score={})'.format(self.player_id, self.location, self.health, self.score)
