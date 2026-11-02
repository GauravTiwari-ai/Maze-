# Algorithm Notes

## Grid model

The maze is a rectangular list of lists. A cell is addressed by `(row, column)`. The value `1` blocks movement, `0` is ordinary floor, and a value above `1` is the cost of entering weighted terrain. Movement is limited to the four cardinal neighbors.

## Search state

Each search tracks discovered or settled cells, records visit order for animation, and stores predecessor links in a parent dictionary. Reconstructing the path follows these links from the destination to the start, then reverses the sequence. A missing destination produces an empty path.

## Algorithm selection guide

| Algorithm | Frontier structure | How it chooses the next cell | Best fit |
| --- | --- | --- | --- |
| DFS | LIFO stack | Most recently discovered cell | Finding a route when shortest length is not required |
| BFS | FIFO queue | Earliest discovered cell | Minimum number of moves when all moves cost the same |
| Dijkstra | Min-priority queue | Cell with the smallest known route cost | Minimum-cost paths with weighted terrain |

### Depth-first search

DFS uses a Python list as a LIFO stack. It explores one branch deeply, backtracks at dead ends, and returns the first route it discovers. Its time and space complexity are O(V + E) and O(V); it does not guarantee a shortest route. For consistency with other algorithms, the dashboard reports route cost using unit steps on ordinary maze cells.

### Breadth-first search

BFS uses `collections.deque` as a FIFO queue. Cells are expanded in layers of increasing move count, making the first discovered route to the destination shortest by steps. A parent map records the predecessor of each discovered cell so the route can be reconstructed. BFS guarantees minimum total cost only when cell-entry costs are uniform; use Dijkstra for weighted terrain. Its time and space complexity are O(V + E) and O(V).

### Dijkstra's algorithm

Dijkstra uses `heapq` as a min-priority queue. A relaxation step updates a neighbor only when the new route cost is smaller. It is correct for non-negative edge costs and guarantees a minimum-cost route for the positive cell-entry costs used here. Its binary-heap complexity is O((V + E) log V), with O(V) auxiliary storage.

## Maze generation

Recursive backtracking begins at an odd grid coordinate and randomly carves through unvisited cells two positions away, opening the wall between them. The iterative version uses an explicit stack and the same rule. With an odd-sized, initially walled grid, this creates connected passages without loops (a perfect maze). The iterative version is preferred for larger mazes because it does not depend on Python's recursion limit.

## Measurement and visualization

`time.perf_counter()` brackets each synchronous search. The displayed value is a single-run duration, not a benchmark average; small mazes may complete in less than the clock's practical resolution for comparisons. The visualizer computes a search result, then reveals its recorded visitation order over multiple frames. Pause changes playback only; it does not pause or resume the underlying search computation.

## Suggested checks

- Open grid: BFS and Dijkstra should return the same minimum number of steps when all cells have equal cost.
- Weighted detour: Dijkstra should prefer a longer route when its total entry cost is lower.
- Blocked corridor: all algorithms should return an empty path when the destination is unreachable.
- Generator seeds: equal dimensions and seed should reproduce the same maze.
- Generator modes: both backtracking modes should leave the designated start and destination connected.