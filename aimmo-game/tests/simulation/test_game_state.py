from __future__ import absolute_import
from .maps import InfiniteMap, AvatarMap, EmptyMap
from .dummy_avatar import DummyAvatarRunner, EmptyAvatarManager
from simulation.game_state import GameState
from unittest import TestCase


class FogToEmpty(object):
    def apply_fog_of_war(self, world_map, wrapper):
        return EmptyMap()


class TestGameState(TestCase):
    def game_state_with_two_avatars(self, world_map=None, avatar_manager=None):
        if world_map is None:
            world_map = EmptyMap()
        if avatar_manager is None:
            avatar_manager = EmptyAvatarManager()

        avatar = DummyAvatarRunner((0, 0), 1)
        other_avatar = DummyAvatarRunner((0, 0), 2)
        other_avatar.marked = True
        avatar_manager.avatarsById[1] = avatar
        avatar_manager.avatarsById[2] = other_avatar
        game_state = GameState(world_map, avatar_manager)
        return (game_state, avatar, world_map, avatar_manager)

    def test_remove_non_existant_avatar(self):
        state = GameState(None, EmptyAvatarManager())
        state.remove_avatar(10)

    def test_remove_avatar(self):
        (state, _, world_map, manager) = self.game_state_with_two_avatars()
        state.remove_avatar(1)

        self.assertTrue(manager.avatarsById[2].marked)
        self.assertNotIn(1, manager.avatarsById)
        self.assertEqual(world_map.get_cell((0, 0)).avatar, None)

    def test_add_avatar(self):
        state = GameState(AvatarMap(None), EmptyAvatarManager())
        state.add_avatar(7, 'test')
        self.assertIn(7, state.avatar_manager.avatarsById)
        avatar = state.avatar_manager.avatarsById[7]
        self.assertEqual(avatar.location.x, 10)
        self.assertEqual(avatar.location.y, 10)

    def test_fog_of_war(self):
        state = GameState(InfiniteMap(), EmptyAvatarManager())
        view = state.get_state_for(DummyAvatarRunner(None, None), FogToEmpty())
        self.assertEqual(len(view['world_map']['cells']), 0)
        self.assertEqual(view['avatar_state'], 'Dummy')

    def test_no_main_avatar_by_default(self):
        state = GameState(EmptyMap(), EmptyAvatarManager())
        with self.assertRaises(KeyError):
            state.get_main_avatar()

    def test_get_main_avatar(self):
        (game_state, avatar, _, _) = self.game_state_with_two_avatars()
        game_state.main_avatar_id = avatar.player_id
        self.assertEqual(game_state.get_main_avatar(), avatar)

    def test_is_complete_calls_lambda(self):
        class LambdaTest(object):
            def __init__(self, return_value):
                self.return_value = return_value

            def __call__(self, game_state):
                self.game_state = game_state
                return self.return_value

        test = LambdaTest(True)
        game_state = GameState(EmptyMap(), EmptyAvatarManager(), test)
        self.assertTrue(game_state.is_complete())
        test.return_value = False
        self.assertFalse(game_state.is_complete())
