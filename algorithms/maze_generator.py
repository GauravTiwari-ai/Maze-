"""Perfect-maze generation using recursive or explicit-stack backtracking."""

import random
from collections.abc import Iterator

from .common import Cell, Grid


def generate_maze(
    rows: int = 17,
    columns: int = 25,
    *,
    seed: int | None = None,
    iterative: bool = True,
) -> Grid:
    """Return an odd-sized maze where 1 is a wall and 0 is open floor."""
    if rows < 5 or columns < 5 or rows % 2 == 0 or columns % 2 == 0:
        raise ValueError("Maze dimensions must be odd integers of at least 5.")

    grid = [[1 for _ in range(columns)] for _ in range(rows)]
    grid[1][1] = 0
    for wall, destination in maze_generation_steps(
        rows, columns, seed=seed, iterative=iterative
    ):
        grid[wall[0]][wall[1]] = 0
        grid[destination[0]][destination[1]] = 0
    grid[rows - 2][columns - 2] = 0
    return grid


def maze_generation_steps(
    rows: int = 17,
    columns: int = 25,
    *,
    seed: int | None = None,
    iterative: bool = True,
) -> Iterator[tuple[Cell, Cell]]:
    """Yield each carved wall and destination cell in backtracking order."""
    if rows < 5 or columns < 5 or rows % 2 == 0 or columns % 2 == 0:
        raise ValueError("Maze dimensions must be odd integers of at least 5.")

    rng = random.Random(seed)
    start = (1, 1)
    directions = [(0, 2), (2, 0), (0, -2), (-2, 0)]
    visited = {start}

    if iterative:
        stack = [start]
        while stack:
            row, column = stack[-1]
            choices = [
                (row + row_step, column + column_step, row_step, column_step)
                for row_step, column_step in directions
                if 1 <= row + row_step < rows - 1
                and 1 <= column + column_step < columns - 1
                and (row + row_step, column + column_step) not in visited
            ]
            if not choices:
                stack.pop()
                continue
            next_row, next_column, row_step, column_step = rng.choice(choices)
            visited.add((next_row, next_column))
            yield (row + row_step // 2, column + column_step // 2), (next_row, next_column)
            stack.append((next_row, next_column))
        return

    def carve_from(row: int, column: int) -> Iterator[tuple[Cell, Cell]]:
        shuffled_directions = directions[:]
        rng.shuffle(shuffled_directions)
        for row_step, column_step in shuffled_directions:
            next_cell = (row + row_step, column + column_step)
            next_row, next_column = next_cell
            if (
                1 <= next_row < rows - 1
                and 1 <= next_column < columns - 1
                and next_cell not in visited
            ):
                visited.add(next_cell)
                yield (row + row_step // 2, column + column_step // 2), next_cell
                yield from carve_from(next_row, next_column)

    yield from carve_from(*start)