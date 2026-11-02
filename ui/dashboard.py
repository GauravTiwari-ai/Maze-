"""Algorithm visualizer, animated playback, and manual maze gameplay."""

import pygame

from algorithms import bfs, dfs, dijkstra, generate_maze
from algorithms.common import Cell, Grid, SearchResult
from algorithms.maze_generator import maze_generation_steps
from ui.buttons import Button, draw_text
from ui.maze_renderer import draw_maze
from utils.constants import ALGORITHMS, COLORS, DIFFICULTIES, HEIGHT, WIDTH

SEARCHES = {"DFS": dfs, "BFS": bfs, "Dijkstra": dijkstra}
MIN_ANIMATION_SPEED = 15.0
MAX_ANIMATION_SPEED = 300.0
ANIMATION_SPEED_RANGE = MAX_ANIMATION_SPEED - MIN_ANIMATION_SPEED


class Dashboard:
    def __init__(self) -> None:
        self.difficulty = "Medium"
        self.algorithm = "BFS"
        self.iterative_generation = True
        self.grid = generate_maze(*DIFFICULTIES[self.difficulty], iterative=self.iterative_generation)
        self.start: Cell = (1, 1)
        self.goal: Cell = (len(self.grid) - 2, len(self.grid[0]) - 2)
        self.player = self.start
        self.manual = False
        self.speed = 60.0
        self._animation_progress = 0.0
        self.result: SearchResult | None = None
        self.visible_count = 0
        self.solving = False
        self.generating = False
        self.generation_steps = None
        self._pending_generation_cells: list[Cell] = []
        self.paused = False
        self.status = "Ready to explore"
        self.move_count = 0
        self.grid_rect = pygame.Rect(266, 192, 822, 546)
        self.layout: dict[str, pygame.Rect] = {}
        self.speed_slider_rect = pygame.Rect(44, 380, 170, 22)
        self.buttons = {
            "generate": Button(pygame.Rect(0, 0, 1, 1), "Generate Maze", COLORS["accent"]),
            "generator": Button(pygame.Rect(0, 0, 1, 1), "Generator: Stack", COLORS["cyan"]),
            "easy": Button(pygame.Rect(0, 0, 1, 1), "Easy"),
            "medium": Button(pygame.Rect(0, 0, 1, 1), "Medium"),
            "hard": Button(pygame.Rect(0, 0, 1, 1), "Hard"),
            "manual": Button(pygame.Rect(0, 0, 1, 1), "Manual play", COLORS["yellow"]),
            "start": Button(pygame.Rect(0, 0, 1, 1), "Start", COLORS["accent"]),
            "pause": Button(pygame.Rect(0, 0, 1, 1), "Pause", COLORS["cyan"]),
            "reset": Button(pygame.Rect(0, 0, 1, 1), "Reset", COLORS["path"]),
            "compare": Button(pygame.Rect(0, 0, 1, 1), "Compare", COLORS["yellow"]),
            "editor": Button(pygame.Rect(0, 0, 1, 1), "Edit Maze", COLORS["accent"]),
        }
        self.algorithm_buttons = {
            name: Button(pygame.Rect(0, 0, 1, 1), name, COLORS["accent"])
            for name in ALGORITHMS
        }
        self._set_layout(WIDTH, HEIGHT)

    def _set_layout(self, width: int, height: int) -> None:
        margin = max(12, int(width * 0.018))
        gap = max(10, int(width * 0.012))
        left_width = int(width * 0.225)
        right_width = int(width * 0.255)
        content_top = max(92, int(height * 0.135))
        footer_top = height - max(74, int(height * 0.091))
        content_bottom = footer_top - 14
        content_height = max(1, content_bottom - content_top)
        center_width = width - 2 * margin - 2 * gap - left_width - right_width
        left = pygame.Rect(margin, content_top, left_width, content_height)
        center = pygame.Rect(left.right + gap, content_top, center_width, content_height)
        right = pygame.Rect(center.right + gap, content_top, right_width, content_height)

        algorithm_height = int(content_height * 0.46)
        algorithm_panel = pygame.Rect(left.x, left.y, left.width, algorithm_height)
        settings_panel = pygame.Rect(
            left.x,
            algorithm_panel.bottom + gap,
            left.width,
            content_bottom - algorithm_panel.bottom - gap,
        )

        stats_height = int(content_height * 0.36)
        info_height = int(content_height * 0.32)
        stats_panel = pygame.Rect(right.x, right.y, right.width, stats_height)
        info_panel = pygame.Rect(right.x, stats_panel.bottom + gap, right.width, info_height)
        legend_panel = pygame.Rect(
            right.x,
            info_panel.bottom + gap,
            right.width,
            content_bottom - info_panel.bottom - gap,
        )

        self.layout = {
            "algorithm": algorithm_panel,
            "settings": settings_panel,
            "maze": center,
            "stats": stats_panel,
            "info": info_panel,
            "legend": legend_panel,
        }
        inner_x = left.x + 14
        inner_width = left.width - 28
        algorithm_top = algorithm_panel.y + 48
        algorithm_button_height = max(42, (algorithm_panel.height - 60) // 3)
        for index, name in enumerate(ALGORITHMS):
            self.algorithm_buttons[name].rect = pygame.Rect(
                inner_x,
                algorithm_top + index * (algorithm_button_height + 4),
                inner_width,
                algorithm_button_height,
            )

        settings_top = settings_panel.y
        difficulty_y = settings_top + 62
        small_gap = 6
        difficulty_width = (inner_width - 2 * small_gap) // 3
        for index, name in enumerate(("easy", "medium", "hard")):
            self.buttons[name].rect = pygame.Rect(
                inner_x + index * (difficulty_width + small_gap),
                difficulty_y,
                difficulty_width,
                34,
            )
        self.buttons["generator"].rect = pygame.Rect(
            inner_x, difficulty_y + 46, inner_width, 32
        )
        self.speed_slider_rect = pygame.Rect(
            inner_x,
            difficulty_y + 106,
            inner_width,
            22,
        )
        self.buttons["manual"].rect = pygame.Rect(
            inner_x,
            settings_panel.bottom - 90,
            inner_width,
            34,
        )
        self.buttons["generate"].rect = pygame.Rect(
            inner_x,
            settings_panel.bottom - 46,
            inner_width,
            36,
        )

        action_names = ("start", "pause", "reset", "compare", "editor")
        action_gap = max(8, int(width * 0.012))
        action_width = (width - 2 * margin - action_gap * 4) // len(action_names)
        action_y = footer_top + max(8, (height - footer_top - 58) // 2)
        for index, name in enumerate(action_names):
            self.buttons[name].rect = pygame.Rect(
                margin + index * (action_width + action_gap),
                action_y,
                action_width,
                min(58, height - action_y - 8),
            )

        maze_bounds = pygame.Rect(
            center.x + 18,
            center.y + 48,
            center.width - 36,
            center.height - 90,
        )
        self.grid_rect = maze_bounds

    def set_maze(self, grid: Grid, start: Cell, goal: Cell) -> None:
        self.grid = [row[:] for row in grid]
        self.start, self.goal = start, goal
        self.player = start
        self.clear_search()
        self.status = "Editor maze loaded"

    def clear_search(self) -> None:
        self.result = None
        self.visible_count = 0
        self._animation_progress = 0.0
        self.solving = False
        self.generating = False
        self.generation_steps = None
        self._pending_generation_cells.clear()
        self.paused = False
        self.buttons["pause"].label = "Pause"
        self.move_count = 0
        self.player = self.start

    def generate(self) -> None:
        self.clear_search()
        rows, columns = DIFFICULTIES[self.difficulty]
        self.grid = [[1 for _ in range(columns)] for _ in range(rows)]
        self.start = (1, 1)
        self.goal = (rows - 2, columns - 2)
        self.grid[self.start[0]][self.start[1]] = 0
        self.player = self.start
        self.generation_steps = maze_generation_steps(
            rows, columns, iterative=self.iterative_generation
        )
        self._pending_generation_cells.clear()
        self._animation_progress = 0.0
        self.generating = True
        self.status = "Carving maze..."

    def solve(self) -> None:
        if self.generating:
            self.status = "Wait for maze generation to finish"
            return
        self.clear_search()
        self.result = SEARCHES[self.algorithm](self.grid, self.start, self.goal)
        self.solving = True
        self.status = f"Searching with {self.algorithm}..."

    def update(self, delta_seconds: float) -> None:
        if self.paused or not (self.generating or self.solving):
            return
        self._animation_progress += self.speed * max(0.0, delta_seconds)
        cells_to_animate = int(self._animation_progress)
        self._animation_progress -= cells_to_animate
        if cells_to_animate == 0:
            return
        if self.generating and self.generation_steps is not None:
            for _ in range(cells_to_animate):
                if not self._pending_generation_cells:
                    try:
                        wall, destination = next(self.generation_steps)
                    except StopIteration:
                        self.generating = False
                        self.generation_steps = None
                        self.status = "Maze generated"
                        break
                    self._pending_generation_cells.extend((destination, wall))
                row, column = self._pending_generation_cells.pop()
                self.grid[row][column] = 0
            return
        if not self.solving or self.result is None:
            return
        self.visible_count = min(
            len(self.result.visited),
            self.visible_count + cells_to_animate,
        )
        if self.visible_count >= len(self.result.visited):
            self.solving = False
            self.status = "Maze solved!" if self.result.found else "No route to the exit"

    def handle_event(self, event: pygame.event.Event) -> str | None:
        if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
            self._set_speed_from_mouse(event.pos)
        elif event.type == pygame.MOUSEMOTION and getattr(event, "buttons", (False,))[0]:
            self._set_speed_from_mouse(event.pos)

        if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
            selected_algorithm = next(
                (
                    name
                    for name, button in self.algorithm_buttons.items()
                    if button.clicked(event)
                ),
                None,
            )
            if selected_algorithm is not None:
                self.algorithm = selected_algorithm
            elif self.buttons["generate"].clicked(event):
                self.generate()
            elif self.buttons["generator"].clicked(event):
                self.iterative_generation = not self.iterative_generation
                self.buttons["generator"].label = "Generator: Stack" if self.iterative_generation else "Generator: Recursive"
                self.generate()
            elif self.buttons["easy"].clicked(event):
                self.set_difficulty("Easy")
            elif self.buttons["medium"].clicked(event):
                self.set_difficulty("Medium")
            elif self.buttons["hard"].clicked(event):
                self.set_difficulty("Hard")
            elif self.buttons["manual"].clicked(event):
                self.manual = not self.manual
                self.clear_search()
                self.status = "Manual movement enabled" if self.manual else "Manual movement disabled"
            elif self.buttons["start"].clicked(event):
                self.manual = False
                self.solve()
            elif self.buttons["pause"].clicked(event):
                if self.generating or (self.result is not None and (self.solving or self.paused)):
                    self.paused = not self.paused
                    self.solving = self.result is not None and not self.paused
                    self.buttons["pause"].label = "Resume" if self.paused else "Pause"
                    if self.paused:
                        self.status = "Paused"
                    elif self.generating:
                        self.status = "Carving maze..."
                    else:
                        self.status = f"Searching with {self.algorithm}..."
            elif self.buttons["reset"].clicked(event):
                self.generate()
            elif self.buttons["compare"].clicked(event):
                return "compare"
            elif self.buttons["editor"].clicked(event):
                return "editor"
            elif self.manual and self.grid_rect.collidepoint(event.pos):
                self._move_player_to_click(event.pos)

        if event.type == pygame.KEYDOWN and self.manual:
            movement = {
                pygame.K_UP: (-1, 0), pygame.K_w: (-1, 0),
                pygame.K_RIGHT: (0, 1), pygame.K_d: (0, 1),
                pygame.K_DOWN: (1, 0), pygame.K_s: (1, 0),
                pygame.K_LEFT: (0, -1), pygame.K_a: (0, -1),
            }
            if event.key in movement:
                self._move_player(movement[event.key])
        return None

    def set_difficulty(self, name: str) -> None:
        if name != self.difficulty:
            self.difficulty = name
            self.generate()

    def _set_speed_from_mouse(self, position: tuple[int, int]) -> None:
        if self.speed_slider_rect.collidepoint(position):
            speed_fraction = (position[0] - self.speed_slider_rect.x) / self.speed_slider_rect.width
            self.speed = max(
                MIN_ANIMATION_SPEED,
                min(
                    MAX_ANIMATION_SPEED,
                    MIN_ANIMATION_SPEED + speed_fraction * ANIMATION_SPEED_RANGE,
                ),
            )

    def _move_player_to_click(self, position: tuple[int, int]) -> None:
        cell_size = min(self.grid_rect.width // len(self.grid[0]), self.grid_rect.height // len(self.grid))
        actual = pygame.Rect(0, 0, cell_size * len(self.grid[0]), cell_size * len(self.grid))
        actual.center = self.grid_rect.center
        if not actual.collidepoint(position):
            return
        column = (position[0] - actual.x) // cell_size
        row = (position[1] - actual.y) // cell_size
        self._move_player((row - self.player[0], column - self.player[1]))

    def _move_player(self, delta: tuple[int, int]) -> None:
        row = self.player[0] + max(-1, min(1, delta[0]))
        column = self.player[1] + max(-1, min(1, delta[1]))
        if abs(row - self.player[0]) + abs(column - self.player[1]) != 1:
            return
        if 0 <= row < len(self.grid) and 0 <= column < len(self.grid[0]) and self.grid[row][column] != 1:
            self.player = (row, column)
            self.move_count += 1
            self.status = "Maze solved!" if self.player == self.goal else "Keep moving to the exit"

    def draw(self, surface: pygame.Surface) -> None:
        self._set_layout(*surface.get_size())
        surface.fill(COLORS["background"])
        pygame.draw.rect(surface, COLORS["panel"], (0, 0, surface.get_width(), 82))
        pygame.draw.line(surface, COLORS["accent"], (0, 81), (surface.get_width(), 81), 2)
        draw_text(surface, "THE MAZE PROJECT", (30, 19), size=24, color=COLORS["accent"], bold=True)
        draw_text(surface, "MAZE SOLVER  /  PATHFINDING VISUALIZER", (32, 49), size=10, color=COLORS["muted"])

        self._draw_left_sidebar(surface)
        self._draw_center(surface)
        self._draw_right_sidebar(surface)
        for name in ("start", "pause", "reset", "compare", "editor"):
            self.buttons[name].draw(surface, active=True)

    def _draw_panel(self, surface: pygame.Surface, rect: pygame.Rect, accent: tuple[int, int, int]) -> None:
        pygame.draw.rect(surface, COLORS["panel"], rect, border_radius=12)
        pygame.draw.rect(surface, accent, rect, 2, border_radius=12)
        header = pygame.Rect(rect.x + 2, rect.y + 2, rect.width - 4, 42)
        pygame.draw.rect(surface, COLORS["panel_light"], header, border_radius=10)
        pygame.draw.rect(
            surface,
            accent,
            (rect.x + 2, rect.y + 40, rect.width - 4, 2),
        )

    def _draw_left_sidebar(self, surface: pygame.Surface) -> None:
        algorithm_panel = self.layout["algorithm"]
        settings_panel = self.layout["settings"]
        self._draw_panel(surface, algorithm_panel, COLORS["path"])
        self._draw_panel(surface, settings_panel, COLORS["cyan"])
        draw_text(surface, "ALGORITHM SELECTION", (algorithm_panel.x + 16, algorithm_panel.y + 13), size=14, color=COLORS["text"], bold=True)
        descriptions = {
            "DFS": "Depth-first search",
            "BFS": "Shortest by steps",
            "Dijkstra": "Lowest total cost",
        }
        for name, button in self.algorithm_buttons.items():
            active = self.algorithm == name
            pygame.draw.rect(
                surface,
                COLORS["panel_light"] if active else COLORS["panel"],
                button.rect,
                border_radius=8,
            )
            pygame.draw.rect(
                surface,
                COLORS["accent"] if active else COLORS["border"],
                button.rect,
                2 if active else 1,
                border_radius=8,
            )
            draw_text(surface, name, (button.rect.x + 12, button.rect.y + 6), size=14, color=COLORS["accent"] if active else COLORS["text"], bold=True)
            draw_text(surface, descriptions[name], (button.rect.x + 12, button.rect.y + 25), size=11, color=COLORS["muted"])

        draw_text(surface, "MAZE SETTINGS", (settings_panel.x + 16, settings_panel.y + 13), size=14, color=COLORS["text"], bold=True)
        draw_text(surface, f"DIFFICULTY  /  {self.difficulty.upper()}", (settings_panel.x + 16, settings_panel.y + 48), size=10, color=COLORS["muted"], bold=True)
        for name in ("easy", "medium", "hard"):
            self.buttons[name].draw(surface, active=self.difficulty.lower() == name)
        self.buttons["generator"].draw(surface)
        draw_text(surface, "ANIMATION SPEED", (self.speed_slider_rect.x, self.speed_slider_rect.y - 22), size=10, color=COLORS["muted"], bold=True)
        slider = pygame.Rect(
            self.speed_slider_rect.x,
            self.speed_slider_rect.centery - 2,
            self.speed_slider_rect.width,
            4,
        )
        pygame.draw.rect(surface, COLORS["border"], slider, border_radius=3)
        knob_x = slider.x + int(
            (self.speed - MIN_ANIMATION_SPEED) / ANIMATION_SPEED_RANGE * slider.width
        )
        pygame.draw.line(surface, COLORS["accent"], slider.topleft, (knob_x, slider.centery), 4)
        pygame.draw.circle(surface, COLORS["accent"], (knob_x, slider.centery), 8)
        draw_text(surface, f"{int(self.speed)} cells / sec", (slider.x, slider.bottom + 5), size=10, color=COLORS["muted"])
        self.buttons["manual"].draw(surface, active=self.manual)
        self.buttons["generate"].draw(surface)

    def _draw_center(self, surface: pygame.Surface) -> None:
        center = self.layout["maze"]
        self._draw_panel(surface, center, COLORS["cyan"])
        draw_text(surface, "THE SEARCH FLOOR", (center.x + 18, center.y + 13), size=14, color=COLORS["text"], bold=True)
        grid_label = f"{len(self.grid)} x {len(self.grid[0])} GRID"
        draw_text(surface, grid_label, (center.right - 60, center.y + 20), size=10, color=COLORS["muted"], center=True)
        visited_cells = set(self.result.visited[:self.visible_count]) if self.result else set()
        final_path = set(self.result.path) if self.result and not self.solving else set()
        maze_bounds = pygame.Rect(center.x + 18, center.y + 48, center.width - 36, center.height - 90)
        self.grid_rect, _ = draw_maze(
            surface, self.grid, maze_bounds, self.start, self.goal,
            player=self.player if self.manual else None,
            visited=visited_cells, path=final_path,
        )
        footer_y = center.bottom - 26
        draw_text(surface, "S  START", (center.x + 18, footer_y), size=10, color=COLORS["accent"], bold=True)
        draw_text(surface, "E  DESTINATION", (center.x + 102, footer_y), size=10, color=COLORS["coral"], bold=True)
        draw_text(surface, f"{self.algorithm}  /  {self.difficulty}", (center.right - 60, footer_y + 5), size=10, color=COLORS["muted"], center=True)

    def _draw_right_sidebar(self, surface: pygame.Surface) -> None:
        stats = self.layout["stats"]
        info = self.layout["info"]
        legend_panel = self.layout["legend"]
        self._draw_panel(surface, stats, COLORS["cyan"])
        self._draw_panel(surface, info, COLORS["path"])
        self._draw_panel(surface, legend_panel, COLORS["cyan"])
        draw_text(surface, "EXECUTION STATISTICS", (stats.x + 16, stats.y + 13), size=13, color=COLORS["text"], bold=True)
        result = self.result
        visible = self.visible_count if result else 0
        metrics = [
            ("Time taken", f"{result.elapsed_ms:.2f} ms" if result else "--"),
            ("Visited nodes", str(visible if self.solving else len(result.visited) if result else 0)),
            ("Path length", str(max(0, len(result.path) - 1) if result else "--")),
            ("Total cost", str(result.total_cost if result else "--")),
            ("Player moves", str(self.move_count)),
        ]
        row_height = max(30, (stats.height - 54) // len(metrics))
        for index, (label, value) in enumerate(metrics):
            y = stats.y + 50 + index * row_height
            draw_text(surface, label, (stats.x + 16, y + 3), size=11, color=COLORS["muted"])
            draw_text(surface, value, (stats.right - 52, y + 9), size=12, color=COLORS["text"], center=True)
            if index < len(metrics) - 1:
                pygame.draw.line(surface, COLORS["border"], (stats.x + 14, y + row_height - 1), (stats.right - 14, y + row_height - 1), 1)

        draw_text(surface, "ALGORITHM INFO", (info.x + 16, info.y + 13), size=13, color=COLORS["text"], bold=True)
        details = {
            "DFS": ("Depth-first search", "Explores one branch deeply, then backtracks.", "O(V + E)", "Shortest path: No"),
            "BFS": ("Breadth-first search", "Explores neighbors one distance layer at a time.", "O(V + E)", "Shortest path: Yes"),
            "Dijkstra": ("Dijkstra's algorithm", "Expands the lowest-cost frontier first.", "O((V + E) log V)", "Lowest cost: Yes"),
        }[self.algorithm]
        title, description, complexity, guarantee = details
        draw_text(surface, title, (info.x + 16, info.y + 50), size=13, color=COLORS["accent"], bold=True)
        draw_text(surface, description, (info.x + 16, info.y + 72), size=10, color=COLORS["text"])
        draw_text(surface, f"Time: {complexity}", (info.x + 16, info.y + 96), size=10, color=COLORS["muted"])
        draw_text(surface, guarantee, (info.x + 16, info.y + 116), size=10, color=COLORS["muted"])
        status_color = COLORS["accent"] if "solved" in self.status.lower() else COLORS["yellow"]
        status_rect = pygame.Rect(info.x + 12, info.bottom - 36, info.width - 24, 25)
        pygame.draw.rect(surface, COLORS["panel_light"], status_rect, border_radius=6)
        draw_text(surface, self.status[:28], (status_rect.x + 8, status_rect.y + 5), size=10, color=status_color, bold=True)

        draw_text(surface, "LEGEND", (legend_panel.x + 16, legend_panel.y + 13), size=13, color=COLORS["text"], bold=True)
        legend = [
            (COLORS["start"], "Start"),
            (COLORS["coral"], "Exit"),
            (COLORS["wall"], "Wall"),
            (COLORS["floor"], "Floor"),
            (COLORS["visited"], "Visited"),
            (COLORS["path"], "Final path"),
            (COLORS["yellow"], "Weighted"),
        ]
        columns = 2 if legend_panel.width < 330 else 3
        column_width = (legend_panel.width - 28) // columns
        for index, (color, label) in enumerate(legend):
            column, row = index % columns, index // columns
            x = legend_panel.x + 14 + column * column_width
            y = legend_panel.y + 52 + row * 28
            pygame.draw.rect(surface, color, (x, y, 13, 13), border_radius=3)
            draw_text(surface, label, (x + 19, y - 1), size=9, color=COLORS["text"])