"""Depth-first search using an explicit stack."""

from time import perf_counter

from .common import Cell, Grid, SearchResult, cell_cost, neighbors, reconstruct_path


def dfs(grid: Grid, start: Cell, goal: Cell) -> SearchResult:
    """Explore deeply first; the returned route is not necessarily shortest."""
    started = perf_counter()
    stack = [start]
    discovered = {start}
    parent: dict[Cell, Cell] = {}
    visited: list[Cell] = []

    while stack:
        current = stack.pop()
        visited.append(current)
        if current == goal:
            break
        for neighbor in reversed(neighbors(grid, current)):
            if neighbor not in discovered:
                discovered.add(neighbor)
                parent[neighbor] = current
                stack.append(neighbor)

    path = reconstruct_path(parent, start, goal) if goal in discovered else []
    elapsed_ms = (perf_counter() - started) * 1000
    total_cost = sum(cell_cost(grid, cell) for cell in path[1:])
    return SearchResult("DFS", visited, path, elapsed_ms, total_cost, False)