from types import SimpleNamespace
import unittest
from unittest.mock import Mock

from pico2d import SDL_KEYDOWN, SDL_KEYUP, SDLK_LEFT, SDLK_RIGHT, SDLK_SPACE

from boy import Boy
from settings import RUN_SPEED
from states import Idle, Run, Sleep


def key_down(boy, key):
    boy.handle_event(SimpleNamespace(type=SDL_KEYDOWN, key=key))


def key_up(boy, key):
    boy.handle_event(SimpleNamespace(type=SDL_KEYUP, key=key))


class BoyTests(unittest.TestCase):
    def setUp(self):
        self.boy = Boy(image=Mock())

    def test_initial_state_and_sleep_time_boundary(self):
        self.assertIsInstance(self.boy.state, Idle)
        self.boy.update(4.999)
        self.assertIsInstance(self.boy.state, Idle)
        self.boy.update(0.0011)
        self.assertIsInstance(self.boy.state, Sleep)

    def test_both_directions_use_one_run_class(self):
        for key, direction in ((SDLK_LEFT, -1), (SDLK_RIGHT, 1)):
            with self.subTest(direction=direction):
                boy = Boy(image=Mock())
                key_down(boy, key)
                self.assertIsInstance(boy.state, Run)
                boy.update(0.1)
                self.assertAlmostEqual(boy.x, 400 + direction * RUN_SPEED * 0.1)
                self.assertEqual(boy.face_dir, direction)

    def test_repeat_opposite_keys_and_release(self):
        key_down(self.boy, SDLK_RIGHT)
        key_down(self.boy, SDLK_RIGHT)
        self.boy.update(0.1)
        self.assertAlmostEqual(self.boy.x, 430)
        key_down(self.boy, SDLK_LEFT)
        self.assertIsInstance(self.boy.state, Idle)
        key_up(self.boy, SDLK_RIGHT)
        self.assertIsInstance(self.boy.state, Run)
        self.assertEqual(self.boy.move_dir, -1)
        key_up(self.boy, SDLK_LEFT)
        self.assertIsInstance(self.boy.state, Idle)

    def test_normal_run_stays_inside_screen(self):
        for key, expected_x in ((SDLK_LEFT, 50), (SDLK_RIGHT, 750)):
            with self.subTest(key=key):
                boy = Boy(image=Mock())
                key_down(boy, key)
                boy.update(10.0)
                self.assertEqual(boy.x, expected_x)

    def test_sleep_space_and_both_directions(self):
        for key, state in ((SDLK_SPACE, Idle), (SDLK_LEFT, Run), (SDLK_RIGHT, Run)):
            with self.subTest(key=key):
                boy = Boy(image=Mock())
                boy.update(5.0)
                key_down(boy, key)
                self.assertIsInstance(boy.state, state)

    def test_idle_timer_resets_after_run(self):
        self.boy.update(4.0)
        key_down(self.boy, SDLK_RIGHT)
        self.boy.update(10.0)
        key_up(self.boy, SDLK_RIGHT)
        self.boy.update(4.999)
        self.assertIsInstance(self.boy.state, Idle)
        self.boy.update(0.0011)
        self.assertIsInstance(self.boy.state, Sleep)


if __name__ == '__main__':
    unittest.main()
