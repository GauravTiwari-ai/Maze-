"""Window, palette, and difficulty settings for the Pygame interface."""

WIDTH = 1440
HEIGHT = 900
FPS = 60
TITLE = "THE MAZE PROJECT"

COLORS = {
    "background": (8, 12, 31),
    "panel": (14, 20, 48),
    "panel_light": (28, 34, 75),
    "border": (57, 65, 135),
    "text": (237, 241, 255),
    "muted": (173, 184, 218),
    "accent": (26, 220, 255),
    "cyan": (65, 168, 255),
    "start": (35, 221, 110),
    "coral": (255, 65, 79),
    "yellow": (255, 196, 50),
    "wall": (49, 52, 68),
    "floor": (222, 226, 241),
    "visited": (81, 183, 255),
    "path": (191, 76, 255),
}

DIFFICULTIES = {
    "Easy": (11, 17),
    "Medium": (17, 25),
    "Hard": (23, 35),
}

ALGORITHMS = ("DFS", "BFS", "Dijkstra")