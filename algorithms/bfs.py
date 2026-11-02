"""Breadth-first search using a FIFO queue."""

from collections import deque
from time import perf_counter

from .common import Cell, Grid, SearchResult, neighbors, reconstruct_path


def bfs(grid: Grid, start: Cell, goal: Cell) -> SearchResult:
    """Find a shortest route by number of steps in an unweighted grid."""
    started = perf_counter()
    queue = deque([start])
    discovered = {start}
    parent: dict[Cell, Cell] = {}
    visited: list[Cell] = []

    while queue:
        current = queue.popleft()
        visited.append(current)
        if current == goal:
            break
        for neighbor in neighbors(grid, current):
            if neighbor not in discovered:
                discovered.add(neighbor)
                parent[neighbor] = current
                queue.append(neighbor)

    path = reconstruct_path(parent, start, goal) if goal in discovered else []
    elapsed_ms = (perf_counter() - started) * 1000
    total_cost = sum(max(1, grid[row][column]) for row, column in path[1:])
    cost_is_uniform = all(value <= 1 for row in grid for value in row)
    return SearchResult("BFS", visited, path, elapsed_ms, total_cost, cost_is_uniform)