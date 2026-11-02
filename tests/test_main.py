"""Tests for application-level window control handling."""

import unittest
from unittest.mock import MagicMock, call, patch

import pygame

import main


class MainWindowControlTests(unittest.TestCase):
    def test_minimize_and_fullscreen_actions_reach_display(self) -> None:
        actions = ["minimize", "toggle_fullscreen", "toggle_fullscreen", "quit"]
        event_batches = [
            [pygame.event.Event(pygame.USEREVENT)]
            for _ in actions
        ]
        screen_manager = MagicMock()
        screen_manager.handle_event.side_effect = actions
        clock = MagicMock()
        clock.tick.return_value = 16

        with (
            patch("main.pygame.init"),
            patch("main.pygame.quit"),
            patch("main.pygame.display.set_mode", side_effect=[object(), object(), object()]) as set_mode,
            patch("main.pygame.display.set_caption"),
            patch("main.pygame.display.iconify") as iconify,
            patch("main.pygame.display.flip"),
            patch("main.pygame.event.get", side_effect=event_batches),
            patch("main.pygame.time.Clock", return_value=clock),
            patch("main.ScreenManager", return_value=screen_manager),
        ):
            result = main.main()

        self.assertEqual(result, 0)
        iconify.assert_called_once_with()
        self.assertEqual(
            set_mode.call_args_list,
            [
                call((main.WIDTH, main.HEIGHT)),
                call((main.WIDTH, main.HEIGHT), pygame.SCALED | pygame.FULLSCREEN),
                call((main.WIDTH, main.HEIGHT), 0),
            ],
        )
        self.assertFalse(screen_manager.fullscreen)


if __name__ == "__main__":
    unittest.main()
