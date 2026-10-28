from types import SimpleNamespace
import unittest
from unittest.mock import Mock

from pico2d import SDL_KEYDOWN, SDL_KEYUP, SDLK_LEFT, SDLK_RIGHT, SDLK_SPACE, SDLK_a

from boy import Boy
from settings import AUTO_RUN_SPEED, RUN_SPEED
from states import AutoRun, Idle, Run, Sleep


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


class AutoRunTests(unittest.TestCase):
    def setUp(self):
        self.boy = Boy(image=Mock())

    def start_auto_run(self, direction=1):
        self.boy.face_dir = direction
        key_down(self.boy, SDLK_a)
        self.assertIsInstance(self.boy.state, AutoRun)

    def test_a_starts_only_from_idle(self):
        self.start_auto_run()
        for initial_state in (Run, Sleep):
            with self.subTest(state=initial_state.__name__):
                boy = Boy(image=Mock())
                boy.change_state(initial_state)
                key_down(boy, SDLK_a)
                self.assertIsInstance(boy.state, initial_state)

    def test_release_a_keeps_automatic_movement_and_facing(self):
        for direction in (-1, 1):
            with self.subTest(direction=direction):
                self.boy = Boy(image=Mock())
                self.start_auto_run(direction)
                key_up(self.boy, SDLK_a)
                self.boy.update(0.1)
                self.assertIsInstance(self.boy.state, AutoRun)
                self.assertAlmostEqual(self.boy.x, 400 + direction * AUTO_RUN_SPEED * 0.1)
                self.assertEqual(self.boy.face_dir, direction)

    def test_auto_run_is_twice_as_fast_and_twice_as_large(self):
        key_down(self.boy, SDLK_RIGHT)
        self.boy.update(0.1)
        normal_distance = self.boy.x - 400
        normal_size = self.boy.draw_size
        key_up(self.boy, SDLK_RIGHT)
        self.boy.x = 400
        self.start_auto_run()
        self.boy.update(0.1)
        self.assertAlmostEqual(self.boy.x - 400, normal_distance * 2)
        self.assertEqual(self.boy.draw_size, normal_size * 2)
        self.boy.draw()
        self.assertEqual(self.boy.image.clip_draw.call_args.args[-2:], (200, 200))

    def test_five_second_boundary_and_normal_size_restore(self):
        self.start_auto_run()
        self.boy.update(4.999)
        self.assertIsInstance(self.boy.state, AutoRun)
        self.boy.update(0.001)
        self.assertIsInstance(self.boy.state, Idle)
        self.assertEqual(self.boy.draw_size, 100)
        x = self.boy.x
        self.boy.update(4.999)
        self.assertIsInstance(self.boy.state, Idle)
        self.assertEqual(self.boy.x, x)
        self.boy.update(0.0011)
        self.assertIsInstance(self.boy.state, Sleep)

    def test_each_edge_reflects_overshoot_inside_enlarged_bounds(self):
        for start_x, direction, expected_x in ((690, 1, 650), (110, -1, 150)):
            with self.subTest(direction=direction):
                self.boy = Boy(image=Mock())
                self.boy.x = start_x
                self.start_auto_run(direction)
                self.boy.update(0.1)
                self.assertAlmostEqual(self.boy.x, expected_x)
                self.assertEqual(self.boy.face_dir, -direction)
                self.assertGreaterEqual(self.boy.x, 100)
                self.assertLessEqual(self.boy.x, 700)

    def test_entry_clamps_for_larger_sprite_and_exact_edge_turns(self):
        for start_x, direction, expected_x in ((750, 1, 700), (50, -1, 100)):
            with self.subTest(direction=direction):
                self.boy = Boy(image=Mock())
                self.boy.x = start_x
                self.start_auto_run(direction)
                self.assertEqual(self.boy.x, expected_x)
                self.boy.update(0)
                self.assertEqual(self.boy.face_dir, -direction)

    def test_multiple_reflections_in_one_update(self):
        self.start_auto_run()
        self.boy.update(3.0)
        self.assertAlmostEqual(self.boy.x, 400)
        self.assertEqual(self.boy.face_dir, -1)
        self.assertIsInstance(self.boy.state, AutoRun)

    def test_long_frame_only_moves_for_five_seconds(self):
        self.start_auto_run()
        self.boy.update(100.0)
        self.assertIsInstance(self.boy.state, Idle)
        self.assertAlmostEqual(self.boy.x, 400)
        self.assertEqual(self.boy.face_dir, -1)

    def test_either_arrow_cancels_to_normal_run(self):
        for key, direction in ((SDLK_LEFT, -1), (SDLK_RIGHT, 1)):
            with self.subTest(direction=direction):
                self.boy = Boy(image=Mock())
                self.start_auto_run()
                self.boy.update(0.1)
                key_down(self.boy, key)
                self.assertIsInstance(self.boy.state, Run)
                self.assertEqual(self.boy.draw_size, 100)
                self.assertEqual(self.boy.face_dir, direction)
                x = self.boy.x
                self.boy.update(0.1)
                self.assertAlmostEqual(self.boy.x, x + direction * RUN_SPEED * 0.1)
                self.boy.update(6.0)
                self.assertIsInstance(self.boy.state, Run)
                key_up(self.boy, key)
                self.assertIsInstance(self.boy.state, Idle)

    def test_repeated_a_does_not_extend_or_restart_auto_run(self):
        self.start_auto_run()
        self.boy.update(4.0)
        key_down(self.boy, SDLK_a)
        self.boy.update(1.0)
        self.assertIsInstance(self.boy.state, Idle)
        key_down(self.boy, SDLK_a)
        self.assertIsInstance(self.boy.state, Idle)
        key_up(self.boy, SDLK_a)
        key_down(self.boy, SDLK_a)
        self.assertIsInstance(self.boy.state, AutoRun)

    def test_space_and_unrelated_events_do_not_cancel_auto_run(self):
        self.start_auto_run()
        key_down(self.boy, SDLK_SPACE)
        self.boy.handle_event(SimpleNamespace(type=0))
        self.assertIsInstance(self.boy.state, AutoRun)


if __name__ == '__main__':
    unittest.main()
