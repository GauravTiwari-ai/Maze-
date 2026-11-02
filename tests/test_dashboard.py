"""Headless tests for dashboard animation and the home-screen game flow."""

import unittest
from unittest.mock import patch

import pygame

from ui.dashboard import Dashboard, MIN_ANIMATION_SPEED
from ui.screens import ScreenManager


class DashboardAnimationTests(unittest.TestCase):
    def test_window_controls_return_their_requested_actions(self) -> None:
        screens = ScreenManager()
        controls = (
            ("minimize", "minimize"),
            ("fullscreen", "toggle_fullscreen"),
            ("close", "quit"),
        )

        for name, expected_action in controls:
            button = screens.window_buttons[name]
            event = pygame.event.Event(
                pygame.MOUSEBUTTONDOWN,
                {"button": 1, "pos": button.rect.center},
            )
            self.assertEqual(screens.handle_event(event), expected_action)

    def test_header_controls_fit_and_do_not_overlap_navigation(self) -> None:
        screens = ScreenManager()

        for width in (1365, 1440):
            screens._layout_header(width)
            nav_buttons = list(screens.nav.values())
            control_buttons = list(screens.window_buttons.values())
            self.assertLessEqual(nav_buttons[-1].rect.right, control_buttons[0].rect.left)
            self.assertLessEqual(control_buttons[-1].rect.right, width)

    def test_secondary_screens_fit_reference_window(self) -> None:
        pygame.font.init()
        screens = ScreenManager()

        for size in ((1440, 900), (1365, 768)):
            surface = pygame.Surface(size)
            for name in ("compare", "editor", "about"):
                screens.current = name
                with patch("pygame.mouse.get_pos", return_value=(0, 0)):
                    screens.draw(surface)

                if name == "compare":
                    self.assertLessEqual(screens.compare_chart_rect.right, size[0])
                    self.assertLessEqual(screens.compare_buttons["back"].rect.right, size[0])
                    self.assertLessEqual(screens.compare_buttons["back"].rect.bottom, size[1])
                elif name == "editor":
                    self.assertLessEqual(screens.editor_panel_rect.right, size[0])
                    self.assertLessEqual(screens.editor_panel_rect.bottom, size[1])
                    self.assertLessEqual(screens.editor_grid_rect.bottom, screens.editor_label_y)
                else:
                    self.assertLessEqual(screens.about_footer_rect.right, size[0])
                    self.assertLessEqual(screens.about_footer_rect.bottom, size[1])

    def test_start_game_plays_generation_animation_and_enables_manual_mode(self) -> None:
        screens = ScreenManager()
        start_button = screens.home_buttons["start"]
        event = pygame.event.Event(
            pygame.MOUSEBUTTONDOWN,
            {"button": 1, "pos": start_button.rect.center},
        )

        screens.handle_event(event)

        self.assertEqual(screens.current, "dashboard")
        self.assertTrue(screens.dashboard.manual)
        self.assertTrue(screens.dashboard.generating)
        self.assertEqual(screens.dashboard.status, "Carving maze...")

        screens.dashboard.update(1 / screens.dashboard.speed)
        self.assertTrue(screens.dashboard.generating)
        self.assertEqual(
            sum(cell == 0 for row in screens.dashboard.grid for cell in row),
            2,
        )

    def test_solver_animation_respects_fractional_cell_progress(self) -> None:
        dashboard = Dashboard()
        dashboard.grid = [[0] * 9 for _ in range(9)]
        dashboard.start = (0, 0)
        dashboard.goal = (8, 8)
        dashboard.speed = 20.0
        dashboard.solve()

        dashboard.update(0.025)
        self.assertEqual(dashboard.visible_count, 0)
        dashboard.update(0.025)
        self.assertEqual(dashboard.visible_count, 1)
        self.assertTrue(dashboard.solving)

    def test_animation_speed_slider_updates_from_mouse_event(self) -> None:
        dashboard = Dashboard()
        with patch("pygame.mouse.get_pos", return_value=(0, 0)):
            dashboard.draw(pygame.Surface((1440, 900)))
        event = pygame.event.Event(
            pygame.MOUSEBUTTONDOWN,
            {"button": 1, "pos": dashboard.speed_slider_rect.topleft},
        )
        dashboard.handle_event(event)

        self.assertEqual(dashboard.speed, MIN_ANIMATION_SPEED)

    def test_dashboard_panels_fit_reference_and_window_sizes(self) -> None:
        pygame.font.init()
        dashboard = Dashboard()

        for size in ((1440, 900), (1365, 768)):
            with patch("pygame.mouse.get_pos", return_value=(0, 0)):
                dashboard.draw(pygame.Surface(size))
            self.assertLessEqual(dashboard.layout["algorithm"].bottom, dashboard.layout["settings"].top)
            self.assertLessEqual(dashboard.layout["stats"].bottom, dashboard.layout["info"].top)
            self.assertLessEqual(dashboard.layout["info"].bottom, dashboard.layout["legend"].top)
            self.assertLessEqual(dashboard.layout["legend"].right, size[0])
            self.assertTrue(all(button.rect.bottom <= size[1] for button in dashboard.buttons.values()))

    def test_algorithm_options_select_the_requested_search(self) -> None:
        dashboard = Dashboard()
        pygame.font.init()
        with patch("pygame.mouse.get_pos", return_value=(0, 0)):
            dashboard.draw(pygame.Surface((1365, 768)))
        button = dashboard.algorithm_buttons["DFS"]
        event = pygame.event.Event(
            pygame.MOUSEBUTTONDOWN,
            {"button": 1, "pos": button.rect.center},
        )

        dashboard.handle_event(event)

        self.assertEqual(dashboard.algorithm, "DFS")


if __name__ == "__main__":
    unittest.main()
