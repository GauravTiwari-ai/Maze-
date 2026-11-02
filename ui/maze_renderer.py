"""Render maze cells and search overlays into a Pygame surface."""

import pygame

from algorithms.common import Cell, Grid
from utils.constants import COLORS


def draw_maze(
    surface: pygame.Surface,
    grid: Grid,
    bounds: pygame.Rect,
    start: Cell,
    goal: Cell,
    *,
    player: Cell | None = None,
    visited: set[Cell] | None = None,
    path: set[Cell] | None = None,
) -> tuple[pygame.Rect, int]:
    rows, columns = len(grid), len(grid[0])
    cell_size = max(4, min(bounds.width // columns, bounds.height // rows))
    grid_rect = pygame.Rect(0, 0, cell_size * columns, cell_size * rows)
    grid_rect.center = bounds.center
    visited = visited or set()
    path = path or set()

    pygame.draw.rect(surface, COLORS["background"], grid_rect.inflate(10, 10), border_radius=6)
    for row in range(rows):
        for column in range(columns):
            cell = (row, column)
            cell_rect = pygame.Rect(
                grid_rect.x + column * cell_size + 1,
                grid_rect.y + row * cell_size + 1,
                max(1, cell_size - 2),
                max(1, cell_size - 2),
            )
            color = COLORS["wall"] if grid[row][column] == 1 else COLORS["floor"]
            if grid[row][column] > 1:
                color = COLORS["yellow"]
            if cell in visited and cell not in (start, goal):
                color = COLORS["visited"]
            if cell in path and cell not in (start, goal):
                color = COLORS["path"]
            pygame.draw.rect(surface, color, cell_rect, border_radius=2)
            if grid[row][column] > 1 and cell_size >= 18:
                font = pygame.font.SysFont("bahnschrift", max(10, cell_size // 2), bold=True)
                label = font.render(str(grid[row][column]), True, COLORS["background"])
                surface.blit(label, label.get_rect(center=cell_rect.center))

    for cell, label, color in (
        (start, "S", COLORS["start"]),
        (goal, "E", COLORS["coral"]),
    ):
        rect = pygame.Rect(
            grid_rect.x + cell[1] * cell_size + 1,
            grid_rect.y + cell[0] * cell_size + 1,
            cell_size - 2,
            cell_size - 2,
        )
        pygame.draw.rect(surface, color, rect, border_radius=3)
        if cell_size >= 17:
            font = pygame.font.SysFont("bahnschrift", max(10, cell_size // 2), bold=True)
            marker = font.render(label, True, COLORS["background"])
            surface.blit(marker, marker.get_rect(center=rect.center))

    if player is not None and player not in (start, goal):
        center = (
            grid_rect.x + player[1] * cell_size + cell_size // 2,
            grid_rect.y + player[0] * cell_size + cell_size // 2,
        )
        pygame.draw.circle(surface, COLORS["text"], center, max(4, cell_size // 3))
        pygame.draw.circle(surface, COLORS["cyan"], center, max(2, cell_size // 6))
    return grid_rect, cell_size