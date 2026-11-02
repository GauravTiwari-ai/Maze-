"""Entry point for The Maze Project Pygame application."""

import sys

import pygame

from ui.screens import ScreenManager
from utils.constants import FPS, HEIGHT, TITLE, WIDTH


def main() -> int:
    pygame.init()
    try:
        screen = pygame.display.set_mode((WIDTH, HEIGHT))
    except pygame.error as error:
        pygame.quit()
        print(f"Unable to open the Pygame display: {error}", file=sys.stderr)
        return 1

    pygame.display.set_caption(TITLE)
    clock = pygame.time.Clock()
    screens = ScreenManager()
    fullscreen = False
    running = True

    while running:
        delta_seconds = min(clock.tick(FPS) / 1000, 0.1)
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
                continue

            action = screens.handle_event(event)
            if action == "quit":
                running = False
            elif action == "minimize":
                pygame.display.iconify()
            elif action == "toggle_fullscreen":
                next_fullscreen = not fullscreen
                flags = pygame.SCALED | pygame.FULLSCREEN if next_fullscreen else 0
                try:
                    screen = pygame.display.set_mode((WIDTH, HEIGHT), flags)
                except pygame.error as error:
                    print(f"Unable to change display mode: {error}", file=sys.stderr)
                else:
                    fullscreen = next_fullscreen
                    screens.fullscreen = fullscreen

        screens.update(delta_seconds)
        screens.draw(screen)
        pygame.display.flip()

    pygame.quit()
    return 0


if __name__ == "__main__":
    raise SystemExit(main())