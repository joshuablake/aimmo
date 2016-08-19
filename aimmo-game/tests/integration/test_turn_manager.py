from __future__ import absolute_import

from collections import defaultdict
from simulation.game_state import GameState
from simulation.turn_manager import ConcurrentTurnManager
from httmock import HTTMock
import json
from requests.exceptions import ConnectionError
from unittest import TestCase, main


MOVE_LEFT_JSON = json.dumps({'action': 'MoveAction', 'direction': {'x': 1, 'y': 0}})
WAIT_JSON = json.dumps({'action': 'WaitAction'})
ATTACK_UP_JSON = json.dumps({'action': 'AttackAction', 'direction': {'x': 0, 'y': 1}})
NOT_REAL_ACTION_JSON = json.dumps({'action': 'NonexistantAction'})
NO_ACTION_JSON = json.dumps({'MoveAction': {'x': 1, 'y': 0}})


class MockTurnProvider(object):
    def __init__(self, auth_token, avatar_actions=None):
        if avatar_actions is None:
            avatar_actions = {}
        self.avatar_actions = avatar_actions
        self.state_given = defaultdict(list)

    def __call__(self, url, request):
        try:
            avatar_id = int(url.netloc)
        except ValueError:
            raise ConnectionError('Invalid host %s', url.netloc)
        if avatar_id not in self.avatar_actions:
            raise ConnectionError('No worker for Avatar')
        if url.path == '/':
            return 'HEATLHY'
        if url.path.startswith('/turn'):
            return json.dumps(self.do_turn(avatar_id, json.loads(request.body)))
        return {'status_code': 404, 'content': 'unknown url'}

    def do_turn(self, avatar_id, state):
        self.state_given[avatar_id].append(state)
        return self.avatar_actions[avatar_id]


class IntegrationTestConcurrentTurnManager(TestCase):
    INITIAL_TURNS = {
        1: MOVE_LEFT_JSON,
        2: WAIT_JSON,
        3: 'Not JSON',
        4: NOT_REAL_ACTION_JSON,
        5: NO_ACTION_JSON,
        6: ATTACK_UP_JSON,
    }

    def build_map(self)

    def test_run(self):
        world = self.build_map()
        avatar_manager = self.build_avatar_manager()
        game_state = GameState(world, avatar_manager)
        turn_manager = ConcurrentTurnManager(game_state, lambda: None)
        turn_mocks = MockTurnProvider('auth', self.INTIAL_TURNS)
        with HTTMock(turn_mocks):
            turn_manager.run_turn()
            import requests
            requests.post('http://1/turn/?auth=1', json={'a': 'b'})
            self.assertEqual(turn_mocks.state_given[1].pop(), {'a': 'b'})


if __name__ == '__main__':
    main()
