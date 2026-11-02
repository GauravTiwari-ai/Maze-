"""Dijkstra's shortest-path algorithm using heapq as a priority queue."""

import heapq
from time import perf_counter

from .common import Cell, Grid, SearchResult, cell_cost, neighbors, reconstruct_path


def dijkstra(grid: Grid, start: Cell, goal: Cell) -> SearchResult:
    """Find a minimum-cost route; cells valued above 1 are weighted terrain."""
    started = perf_counter()
    distances = {start: 0}
    parent: dict[Cell, Cell] = {}
    frontier = [(0, start)]
    settled: set[Cell] = set()
    visited: list[Cell] = []

    while frontier:
        distance, current = heapq.heappop(frontier)
        if current in settled or distance != distances.get(current):
            continue
        settled.add(current)
        visited.append(current)
        if current == goal:
            break
        for neighbor in neighbors(grid, current):
            candidate = distance + cell_cost(grid, neighbor)
            if candidate < distances.get(neighbor, float("inf")):
                distances[neighbor] = candidate
                parent[neighbor] = current
                heapq.heappush(frontier, (candidate, neighbor))

    path = reconstruct_path(parent, start, goal) if goal in settled else []
    elapsed_ms = (perf_counter() - started) * 1000
    return SearchResult("Dijkstra", visited, path, elapsed_ms, distances.get(goal, 0), True)