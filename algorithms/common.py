"""Shared types and helpers for grid-search algorithms."""

from dataclasses import dataclass
from typing import TypeAlias

Cell: TypeAlias = tuple[int, int]
Grid: TypeAlias = list[list[int]]


@dataclass
class SearchResult:
    algorithm: str
    visited: list[Cell]
    path: list[Cell]
    elapsed_ms: float
    total_cost: int
    shortest_path_guarantee: bool

    @property
    def found(self) -> bool:
        return bool(self.path)


def neighbors(grid: Grid, cell: Cell) -> list[Cell]:
    rows, columns = len(grid), len(grid[0])
    row, column = cell
    return [
        (next_row, next_column)
        for next_row, next_column in (
            (row - 1, column),
            (row, column + 1),
            (row + 1, column),
            (row, column - 1),
        )
        if 0 <= next_row < rows
        and 0 <= next_column < columns
        and grid[next_row][next_column] != 1
    ]


def cell_cost(grid: Grid, cell: Cell) -> int:
    return max(1, grid[cell[0]][cell[1]])


def reconstruct_path(parent: dict[Cell, Cell], start: Cell, goal: Cell) -> list[Cell]:
    if goal != start and goal not in parent:
        return []
    path = [goal]
    while path[-1] != start:
        path.append(parent[path[-1]])
    path.reverse()
    return path