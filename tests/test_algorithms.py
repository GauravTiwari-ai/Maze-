"""Headless tests for maze generation and pathfinding."""

import unittest

from algorithms import bfs, dfs, dijkstra, generate_maze
from algorithms.maze_generator import maze_generation_steps


class MazeAlgorithmTests(unittest.TestCase):
    def test_seeded_generation_is_reproducible_and_connected(self) -> None:
        rows, columns = 9, 13
        grid = generate_maze(rows, columns, seed=7)
        self.assertEqual(grid, generate_maze(rows, columns, seed=7))
        result = bfs(grid, (1, 1), (rows - 2, columns - 2))
        self.assertTrue(result.found)

    def test_bfs_returns_shortest_path(self) -> None:
        grid = [[0] * 5 for _ in range(5)]
        grid[1][2] = 1
        result = bfs(grid, (0, 0), (0, 4))
        self.assertEqual(len(result.path) - 1, 4)
        self.assertTrue(result.shortest_path_guarantee)

    def test_bfs_does_not_guarantee_lowest_cost_on_weighted_grid(self) -> None:
        grid = [[0] * 5 for _ in range(3)]
        grid[1][1:4] = [8, 8, 8]

        result = bfs(grid, (1, 0), (1, 4))

        self.assertEqual(len(result.path) - 1, 4)
        self.assertEqual(result.total_cost, 25)
        self.assertFalse(result.shortest_path_guarantee)

    def test_dijkstra_prefers_cheaper_weighted_route(self) -> None:
        grid = [[0] * 5 for _ in range(3)]
        grid[1][1:4] = [8, 8, 8]
        result = dijkstra(grid, (1, 0), (1, 4))
        self.assertEqual(result.total_cost, 6)
        self.assertNotIn((1, 2), result.path)

    def test_dfs_cost_includes_weighted_cells(self) -> None:
        grid = [[0, 4, 0]]
        result = dfs(grid, (0, 0), (0, 2))
        self.assertEqual(result.total_cost, 5)

    def test_unreachable_goal_has_empty_path(self) -> None:
        grid = [[0, 1, 0]]
        for search in (bfs, dfs, dijkstra):
            self.assertFalse(search(grid, (0, 0), (0, 2)).found)

    def test_recursive_and_iterative_generators_match_connectivity(self) -> None:
        for iterative in (True, False):
            grid = generate_maze(11, 15, seed=11, iterative=iterative)
            result = bfs(grid, (1, 1), (9, 13))
            self.assertTrue(result.found)

    def test_generation_steps_reconstruct_the_generated_grid(self) -> None:
        for iterative in (True, False):
            grid = [[1] * 15 for _ in range(11)]
            grid[1][1] = 0
            for wall, destination in maze_generation_steps(11, 15, seed=19, iterative=iterative):
                grid[wall[0]][wall[1]] = 0
                grid[destination[0]][destination[1]] = 0
            self.assertEqual(grid, generate_maze(11, 15, seed=19, iterative=iterative))

    def test_generator_rejects_even_dimensions(self) -> None:
        with self.assertRaises(ValueError):
            generate_maze(10, 15)


if __name__ == "__main__":
    unittest.main()