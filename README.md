# The Maze Project

An offline Python and Pygame mini project for exploring maze generation, graph search, and basic data structures. It includes a playable maze, animated DFS/BFS/Dijkstra searches, a weighted-cell editor, and a side-by-side performance view.

## Requirements

- Windows 10/11
- Python 3.10 or newer
- Pygame-compatible `pygame-ce` 2.5.5 or newer (`import pygame` API)

## Run in Visual Studio Code

1. Open this project folder in VS Code.
2. Open **Terminal > New Terminal** and create a virtual environment:

   ```powershell
   py -m venv .venv
   .venv\Scripts\Activate.ps1
   ```

   If PowerShell blocks activation, use the VS Code terminal command prompt profile or run `.venv\Scripts\python.exe` directly.

3. Install the one runtime dependency (internet is needed only for this initial install):

   ```powershell
   python -m pip install -r requirements.txt
   ```

4. Select `.venv` with **Python: Select Interpreter**, then launch:

   ```powershell
   python main.py
   ```

After installation, the application runs locally without a database, web service, or network access.

## Using the application

- **Solver:** Pick DFS, BFS, or Dijkstra from the top control; choose a size/difficulty and animation speed; use Start, Pause/Resume, or Reset.
- **Generator:** Generate, difficulty, and generator-mode controls animate recursive or iterative stack-based backtracking at the selected speed.
- **Start Game / manual play:** Start Game animates a new maze and enables play; use arrow keys or WASD to move. Walls block movement and the move count updates as you reach the exit. From the visualizer, use Manual play to toggle movement.
- **Editor:** Choose Wall, Erase, Set start, Set exit, or Weighted, then click cells. Clear, Random maze, and Restore are available; Use in visualizer transfers the edited grid.
- **Compare:** Runs all three solvers on the same grid and reports execution time, explored nodes, path length, cost, and shortest-path guarantee.
- **Navigation:** Use the top navigation or Esc to return home.

## Algorithms and data structures

| Component | Data structure | Time | Space | Notes |
| --- | --- | --- | --- | --- |
| Iterative DFS | Stack | O(V + E) | O(V) | Finds a route, not necessarily a shortest one |
| BFS | FIFO queue | O(V + E) | O(V) | Shortest path by number of steps for equal-cost cells |
| Dijkstra | `heapq` priority queue | O((V + E) log V) | O(V) | Minimum-cost path for positive cell-entry costs |
| Recursive backtracking | Call stack | O(RC) | O(RC) | Produces a perfect maze; very large dimensions can hit Python's recursion limit |
| Iterative backtracking | Explicit list stack | O(RC) | O(RC) | Avoids recursion-depth limits |

`V` is the number of walkable cells and `E` the number of adjacent walkable-cell pairs. A grid value of `1` means wall, `0` means ordinary floor, and values greater than `1` represent weighted terrain. Dijkstra charges the cost of entering each cell; the start cell has cost zero.

## Tests

The algorithm tests run without Pygame or a display:

```powershell
py -m unittest discover -v
```

The tests cover deterministic generation, connectivity for both generation modes, BFS shortest steps, weighted Dijkstra routing, unreachable destinations, and invalid dimensions.

## Suggested viva questions

1. **Why does BFS find the shortest path in an unweighted maze?** It visits cells in increasing distance from the start, so the first discovery of the goal uses the fewest moves.
2. **Why can DFS return a longer route?** Its stack follows a deep branch before comparing alternatives, rather than considering all routes by distance.
3. **Why does Dijkstra use a priority queue?** It selects the unsettled cell with the smallest known route cost efficiently.
4. **How does Dijkstra support terrain weights?** The relaxation step adds the destination cell's positive entry cost.
5. **What is a parent map used for?** It remembers each discovered cell's predecessor so the final path can be reconstructed backward.
6. **Why use an explicit stack for iterative generation?** It models recursive backtracking without consuming Python call-stack depth.
7. **What does `perf_counter()` measure here?** High-resolution elapsed wall-clock time for each synchronous search; tiny measurements vary between runs and machines.
8. **What is the difference between path length and total cost?** Path length counts moves; total cost sums the costs of entered cells.

## Project layout

```text
main.py
requirements.txt
algorithms/    maze generation, DFS, BFS, Dijkstra, shared search types
ui/            screens, controls, maze rendering, animated dashboard
utils/         palette, window settings, performance comparison
tests/         headless algorithm tests
docs/          algorithm notes
```