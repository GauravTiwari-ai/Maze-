"""Helpers for collecting comparable pathfinding measurements."""

from algorithms import bfs, dfs, dijkstra
from algorithms.common import Cell, Grid, SearchResult

SEARCHES = {"DFS": dfs, "BFS": bfs, "Dijkstra": dijkstra}


def compare_algorithms(grid: Grid, start: Cell, goal: Cell) -> list[SearchResult]:
    """Run each search against the same grid and return results in UI order."""
    return [SEARCHES[name](grid, start, goal) for name in ("DFS", "BFS", "Dijkstra")]