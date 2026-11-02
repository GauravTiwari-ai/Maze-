"""Navigation and secondary screens for The Maze Project."""

import pygame

from algorithms import generate_maze
from algorithms.common import Cell, Grid, SearchResult
from ui.buttons import Button, draw_text
from ui.dashboard import Dashboard
from ui.maze_renderer import draw_maze
from utils.constants import COLORS, HEIGHT, WIDTH
from utils.performance import compare_algorithms


class ScreenManager:
    def __init__(self) -> None:
        self.dashboard = Dashboard()
        self.current = "home"
        self.nav = {
            "solver": Button(pygame.Rect(850, 24, 84, 38), "SOLVER"),
            "editor": Button(pygame.Rect(942, 24, 84, 38), "EDITOR"),
            "compare": Button(pygame.Rect(1034, 24, 92, 38), "COMPARE"),
            "about": Button(pygame.Rect(1134, 24, 78, 38), "ABOUT"),
            "home": Button(pygame.Rect(1220, 24, 86, 38), "HOME", COLORS["coral"]),
        }
        self.window_buttons = {
            "minimize": Button(pygame.Rect(0, 0, 32, 32), "", COLORS["cyan"]),
            "fullscreen": Button(pygame.Rect(0, 0, 32, 32), "", COLORS["accent"]),
            "close": Button(pygame.Rect(0, 0, 32, 32), "", COLORS["coral"]),
        }
        self.fullscreen = False
        self.home_buttons = {
            "start": Button(pygame.Rect(72, 388, 310, 52), "Start game", COLORS["accent"]),
            "solver": Button(pygame.Rect(72, 452, 310, 52), "Algorithm visualizer", COLORS["cyan"]),
            "compare": Button(pygame.Rect(72, 516, 310, 52), "Performance comparison", COLORS["yellow"]),
            "about": Button(pygame.Rect(72, 580, 310, 52), "About / help", COLORS["coral"]),
            "exit": Button(pygame.Rect(72, 644, 310, 52), "Exit", COLORS["muted"]),
        }
        self.compare_buttons = {
            "run": Button(pygame.Rect(1068, 782, 156, 44), "Run again", COLORS["accent"]),
            "back": Button(pygame.Rect(1238, 782, 136, 44), "Back", COLORS["cyan"]),
        }
        self.editor_actions = {
            "wall": Button(pygame.Rect(76, 158, 116, 36), "Wall"),
            "erase": Button(pygame.Rect(200, 158, 116, 36), "Erase", COLORS["muted"]),
            "start": Button(pygame.Rect(324, 158, 116, 36), "Set start", COLORS["accent"]),
            "goal": Button(pygame.Rect(448, 158, 116, 36), "Set exit", COLORS["coral"]),
            "weight": Button(pygame.Rect(572, 158, 148, 36), "Weighted", COLORS["yellow"]),
            "clear": Button(pygame.Rect(732, 158, 108, 36), "Clear"),
            "random": Button(pygame.Rect(852, 158, 142, 36), "Random maze", COLORS["cyan"]),
            "restore": Button(pygame.Rect(1006, 158, 132, 36), "Restore", COLORS["muted"]),
            "use": Button(pygame.Rect(1150, 158, 214, 36), "Use in visualizer", COLORS["accent"]),
        }
        self.editor_tool = "wall"
        self.editor_grid: Grid = []
        self.editor_default: Grid = []
        self.editor_start: Cell = (1, 1)
        self.editor_goal: Cell = (1, 1)
        self.editor_grid_rect = pygame.Rect(78, 220, 1000, 600)
        self.editor_panel_rect = pygame.Rect(58, 210, 1324, 622)
        self.editor_label_y = 804
        self.editor_cell_size = 1
        self.compare_chart_rect = pygame.Rect(980, 202, 394, 242)
        self.about_footer_rect = pygame.Rect(64, 732, 1310, 80)
        self.comparison: list[SearchResult] = []
        self._load_editor()
        self._run_comparison()
        self._layout_header(WIDTH)
        self._layout_secondary(WIDTH, HEIGHT)

    def _load_editor(self) -> None:
        self.editor_grid = [row[:] for row in self.dashboard.grid]
        self.editor_default = [row[:] for row in self.editor_grid]
        self.editor_start = self.dashboard.start
        self.editor_goal = self.dashboard.goal

    def _run_comparison(self) -> None:
        self.comparison = compare_algorithms(
            self.dashboard.grid, self.dashboard.start, self.dashboard.goal
        )

    def set_screen(self, screen: str) -> None:
        if screen == "editor":
            self._load_editor()
        elif screen == "compare":
            self._run_comparison()
        self.current = screen

    def handle_event(self, event: pygame.event.Event) -> str | None:
        if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
            for name, button in self.window_buttons.items():
                if button.clicked(event):
                    return {
                        "minimize": "minimize",
                        "fullscreen": "toggle_fullscreen",
                        "close": "quit",
                    }[name]

        if event.type == pygame.KEYDOWN and event.key == pygame.K_ESCAPE:
            self.set_screen("home")
            return None

        if self.current != "home" and event.type == pygame.MOUSEBUTTONDOWN:
            for name, button in self.nav.items():
                if button.clicked(event):
                    self.set_screen("dashboard" if name == "solver" else name)
                    return None

        if self.current == "home":
            for name, button in self.home_buttons.items():
                if button.clicked(event):
                    if name == "exit":
                        return "quit"
                    if name == "start":
                        self.dashboard.manual = True
                        self.dashboard.generate()
                        self.set_screen("dashboard")
                    else:
                        self.set_screen("dashboard" if name == "solver" else name)
                    return None
        elif self.current == "dashboard":
            destination = self.dashboard.handle_event(event)
            if destination:
                self.set_screen(destination)
        elif self.current == "compare":
            if self.compare_buttons["run"].clicked(event):
                self._run_comparison()
            elif self.compare_buttons["back"].clicked(event):
                self.set_screen("dashboard")
        elif self.current == "editor":
            self._handle_editor(event)
        return None

    def _handle_editor(self, event: pygame.event.Event) -> None:
        if event.type != pygame.MOUSEBUTTONDOWN or event.button != 1:
            return
        for name, button in self.editor_actions.items():
            if not button.clicked(event):
                continue
            if name in ("wall", "erase", "start", "goal", "weight"):
                self.editor_tool = name
            elif name == "clear":
                self.editor_grid = [[0 for _ in row] for row in self.editor_grid]
            elif name == "random":
                self.editor_grid = generate_maze(len(self.editor_grid), len(self.editor_grid[0]))
                self.editor_start = (1, 1)
                self.editor_goal = (len(self.editor_grid) - 2, len(self.editor_grid[0]) - 2)
            elif name == "restore":
                self.editor_grid = [row[:] for row in self.editor_default]
                self.editor_start = self.dashboard.start
                self.editor_goal = self.dashboard.goal
            elif name == "use":
                self.dashboard.set_maze(self.editor_grid, self.editor_start, self.editor_goal)
                self.set_screen("dashboard")
            return

        if self.editor_grid_rect.collidepoint(event.pos):
            column = (event.pos[0] - self.editor_grid_rect.x) // self.editor_cell_size
            row = (event.pos[1] - self.editor_grid_rect.y) // self.editor_cell_size
            cell = (row, column)
            if not (0 <= row < len(self.editor_grid) and 0 <= column < len(self.editor_grid[0])):
                return
            if self.editor_tool == "start" and cell != self.editor_goal:
                self.editor_start = cell
                self.editor_grid[row][column] = 0
            elif self.editor_tool == "goal" and cell != self.editor_start:
                self.editor_goal = cell
                self.editor_grid[row][column] = 0
            elif cell not in (self.editor_start, self.editor_goal):
                value = self.editor_grid[row][column]
                if self.editor_tool == "wall":
                    self.editor_grid[row][column] = 0 if value == 1 else 1
                elif self.editor_tool == "weight":
                    self.editor_grid[row][column] = 0 if value > 1 else 5
                else:
                    self.editor_grid[row][column] = 0

    def update(self, delta_seconds: float) -> None:
        if self.current == "dashboard":
            self.dashboard.update(delta_seconds)

    def draw(self, surface: pygame.Surface) -> None:
        width, height = surface.get_size()
        self._layout_header(width)
        self._layout_secondary(width, height)
        self._draw_background(surface)
        if self.current == "home":
            self._draw_home(surface)
        elif self.current == "dashboard":
            self.dashboard.draw(surface)
            self._draw_nav(surface)
        elif self.current == "compare":
            self._draw_compare(surface)
            self._draw_nav(surface)
        elif self.current == "editor":
            self._draw_editor(surface)
            self._draw_nav(surface)
        else:
            self._draw_about(surface)
            self._draw_nav(surface)
        self._draw_window_controls(surface)

    def _layout_header(self, width: int) -> None:
        control_size = 32
        control_gap = 5
        control_margin = 18
        controls_width = control_size * len(self.window_buttons) + control_gap * (
            len(self.window_buttons) - 1
        )
        controls_left = width - control_margin - controls_width
        for index, button in enumerate(self.window_buttons.values()):
            button.rect = pygame.Rect(
                controls_left + index * (control_size + control_gap),
                24,
                control_size,
                control_size,
            )

        nav_gap = 8
        nav_width = sum(button.rect.width for button in self.nav.values())
        nav_width += nav_gap * (len(self.nav) - 1)
        nav_right = controls_left - 14
        nav_left = nav_right - nav_width
        for button in self.nav.values():
            button.rect.topleft = (nav_left, 24)
            nav_left += button.rect.width + nav_gap

    def _layout_secondary(self, width: int, height: int) -> None:
        button_gap = 14
        right_margin = max(18, int(width * 0.045))
        back = self.compare_buttons["back"]
        run = self.compare_buttons["run"]
        back.rect.topleft = (width - right_margin - back.rect.width, height - 118)
        run.rect.topleft = (back.rect.left - button_gap - run.rect.width, height - 118)

        chart_width = min(394, max(1, width - 1004))
        self.compare_chart_rect = pygame.Rect(980, 202, chart_width, 242)

        self.editor_panel_rect = pygame.Rect(58, 210, max(1, width - 116), max(1, height - 278))
        self.editor_grid_rect = pygame.Rect(
            80,
            222,
            max(1, width - 160),
            max(1, height - 332),
        )
        self.editor_label_y = height - 96
        self.about_footer_rect = pygame.Rect(64, height - 168, max(1, width - 130), 80)

    def _draw_window_controls(self, surface: pygame.Surface) -> None:
        for name, button in self.window_buttons.items():
            button.draw(surface)
            center_x, center_y = button.rect.center
            color = COLORS["coral"] if name == "close" else COLORS["text"]
            if name == "minimize":
                pygame.draw.line(
                    surface,
                    color,
                    (center_x - 6, center_y + 4),
                    (center_x + 6, center_y + 4),
                    2,
                )
            elif name == "fullscreen" and self.fullscreen:
                pygame.draw.rect(
                    surface,
                    color,
                    (center_x - 5, center_y - 6, 9, 9),
                    2,
                )
                pygame.draw.rect(
                    surface,
                    color,
                    (center_x - 1, center_y - 2, 9, 9),
                    2,
                )
            elif name == "fullscreen":
                pygame.draw.rect(
                    surface,
                    color,
                    (center_x - 6, center_y - 6, 12, 12),
                    2,
                )
            else:
                pygame.draw.line(
                    surface,
                    color,
                    (center_x - 5, center_y - 5),
                    (center_x + 5, center_y + 5),
                    2,
                )
                pygame.draw.line(
                    surface,
                    color,
                    (center_x + 5, center_y - 5),
                    (center_x - 5, center_y + 5),
                    2,
                )

    def _draw_background(self, surface: pygame.Surface) -> None:
        surface.fill(COLORS["background"])
        for x in range(0, WIDTH, 48):
            pygame.draw.line(surface, (18, 26, 32), (x, 0), (x, HEIGHT), 1)
        for y in range(0, HEIGHT, 48):
            pygame.draw.line(surface, (18, 26, 32), (0, y), (WIDTH, y), 1)

    def _draw_nav(self, surface: pygame.Surface) -> None:
        for name, button in self.nav.items():
            button.draw(surface, active=(self.current == ("dashboard" if name == "solver" else name)))

    def _draw_home(self, surface: pygame.Surface) -> None:
        pygame.draw.rect(surface, COLORS["panel"], (0, 0, WIDTH, 88))
        draw_text(surface, "THE MAZE PROJECT", (72, 23), size=26, color=COLORS["accent"], bold=True)
        draw_text(surface, "MAZE SOLVER  /  PATHFINDING VISUALIZER", (74, 54), size=11, color=COLORS["muted"])
        draw_text(surface, "PATHFINDING,", (72, 148), size=17, color=COLORS["cyan"], bold=True)
        draw_text(surface, "MADE VISIBLE.", (72, 177), size=17, color=COLORS["cyan"], bold=True)
        draw_text(surface, "A living lab for", (72, 224), size=44, color=COLORS["text"], bold=True)
        draw_text(surface, "search algorithms.", (72, 270), size=44, color=COLORS["text"], bold=True)
        draw_text(surface, "Build a maze. Choose a strategy. Watch every decision.", (74, 337), size=16, color=COLORS["muted"])
        for button in self.home_buttons.values():
            button.draw(surface)

        preview = pygame.Rect(680, 144, 680, 568)
        pygame.draw.rect(surface, COLORS["panel"], preview, border_radius=10)
        pygame.draw.rect(surface, COLORS["border"], preview, 1, border_radius=10)
        draw_text(surface, "LIVE PREVIEW", (712, 172), size=12, color=COLORS["muted"], bold=True)
        draw_text(surface, "BFS  /  SHORTEST ROUTE", (1084, 172), size=12, color=COLORS["accent"])
        draw_maze(surface, self.dashboard.grid, pygame.Rect(710, 206, 620, 438), self.dashboard.start, self.dashboard.goal)
        draw_text(surface, "STACKS     QUEUES     PRIORITY QUEUES     GRAPHS", (713, 669), size=11, color=COLORS["muted"])
        draw_text(surface, "OFFLINE  /  PYTHON + PYGAME", (72, 750), size=12, color=COLORS["muted"])

    def _draw_compare(self, surface: pygame.Surface) -> None:
        draw_text(surface, "PERFORMANCE / FIELD NOTES", (64, 118), size=26, color=COLORS["text"], bold=True)
        draw_text(surface, "Same maze. Three strategies. Measured locally with perf_counter().", (66, 156), size=14, color=COLORS["muted"])
        colors = (COLORS["coral"], COLORS["cyan"], COLORS["accent"])
        for index, result in enumerate(self.comparison):
            x = 64 + index * 276
            pygame.draw.rect(surface, COLORS["panel"], (x, 202, 252, 112), border_radius=8)
            pygame.draw.rect(surface, colors[index], (x, 202, 4, 112), border_radius=2)
            draw_text(surface, result.algorithm.upper(), (x + 20, 220), size=13, color=COLORS["muted"], bold=True)
            draw_text(surface, f"{result.elapsed_ms:.4f} ms", (x + 20, 247), size=23, color=COLORS["text"], bold=True)
            draw_text(surface, f"{len(result.visited)} nodes  /  {max(0, len(result.path) - 1)} steps", (x + 20, 284), size=12, color=COLORS["muted"])

        chart = self.compare_chart_rect
        pygame.draw.rect(surface, COLORS["panel"], chart, border_radius=8)
        draw_text(surface, "EXECUTION TIME", (1002, 220), size=12, color=COLORS["muted"], bold=True)
        max_time = max((result.elapsed_ms for result in self.comparison), default=0.0) or 1.0
        for index, result in enumerate(self.comparison):
            y = 270 + index * 49
            draw_text(surface, result.algorithm, (1004, y), size=13, color=COLORS["text"])
            bar_width = max(3, int(206 * result.elapsed_ms / max_time))
            pygame.draw.rect(surface, colors[index], (1080, y, bar_width, 16), border_radius=4)
            draw_text(surface, f"{result.elapsed_ms:.3f}", (1300, y - 2), size=12, color=COLORS["muted"])

        table = pygame.Rect(64, 346, 888, 370)
        pygame.draw.rect(surface, COLORS["panel"], table, border_radius=8)
        headings = [(86, "METRIC"), (398, "DFS"), (574, "BFS"), (750, "DIJKSTRA")]
        for x, label in headings:
            draw_text(surface, label, (x, 369), size=12, color=COLORS["muted"], bold=True)
        pygame.draw.line(surface, COLORS["border"], (86, 397), (930, 397), 1)
        metrics = [
            ("Execution time", lambda item: f"{item.elapsed_ms:.4f} ms"),
            ("Nodes visited", lambda item: str(len(item.visited))),
            ("Path length", lambda item: str(max(0, len(item.path) - 1))),
            ("Total cost", lambda item: str(item.total_cost)),
            ("Shortest-path guarantee", lambda item: "Yes" if item.shortest_path_guarantee else "No"),
        ]
        for row, (label, value) in enumerate(metrics):
            y = 421 + row * 50
            draw_text(surface, label, (86, y), size=14, color=COLORS["text"])
            for column, result in enumerate(self.comparison):
                draw_text(surface, value(result), (398 + column * 176, y), size=14, color=COLORS["text"])
            pygame.draw.line(surface, COLORS["border"], (86, y + 31), (930, y + 31), 1)

        draw_text(surface, "Timing is machine- and run-dependent; compare trends, not tiny differences.", (982, 482), size=13, color=COLORS["muted"])
        draw_text(surface, f"MAZE  {len(self.dashboard.grid)} x {len(self.dashboard.grid[0])}", (982, 518), size=12, color=COLORS["cyan"])
        self.compare_buttons["run"].draw(surface)
        self.compare_buttons["back"].draw(surface)

    def _draw_editor(self, surface: pygame.Surface) -> None:
        draw_text(surface, "MAZE EDITOR", (64, 112), size=25, color=COLORS["text"], bold=True)
        draw_text(surface, "Select a tool, then paint cells. Start and exit cannot overlap.", (66, 140), size=13, color=COLORS["muted"])
        for name, button in self.editor_actions.items():
            button.draw(surface, active=(name == self.editor_tool))
        pygame.draw.rect(surface, COLORS["panel"], self.editor_panel_rect, border_radius=8)
        self.editor_grid_rect, self.editor_cell_size = draw_maze(
            surface,
            self.editor_grid,
            self.editor_grid_rect,
            self.editor_start,
            self.editor_goal,
        )
        draw_text(
            surface,
            f"{len(self.editor_grid)} rows  /  {len(self.editor_grid[0])} columns",
            (82, self.editor_label_y),
            size=12,
            color=COLORS["muted"],
        )

    def _draw_about(self, surface: pygame.Surface) -> None:
        draw_text(surface, "ABOUT / FIELD GUIDE", (64, 120), size=28, color=COLORS["text"], bold=True)
        draw_text(surface, "How each algorithm explores, what it guarantees, and which data structure it uses.", (66, 160), size=14, color=COLORS["muted"])
        sections = [
            ("01  /  DEPTH-FIRST SEARCH", "LIFO stack follows one branch deeply, then backtracks.\nReturns the first route found; it may not be the shortest.\nTime O(V + E)  /  Space O(V)"),
            ("02  /  BREADTH-FIRST SEARCH", "FIFO queue explores neighbors one distance layer at a time.\nA parent map rebuilds the route when the exit is reached.\nShortest by steps on equal-cost cells  /  O(V + E)"),
            ("03  /  DIJKSTRA", "Min-heap selects the lowest-cost frontier cell to expand.\nRelaxation updates a route only when its cost improves.\nMinimum-cost route for positive weights  /  O((V + E) log V)"),
            ("04  /  BACKTRACKING", "Carve to an unvisited cell two steps away; open the wall between.\nDead ends trigger backtracking to the previous branch point.\nRecursive calls or an explicit stack  /  O(RC)"),
            ("GRID / CONTROLS / MEASUREMENT", "Grid: 1 = wall, 0 = floor, values above 1 = entry cost.\nArrow keys or WASD move; the editor lets you paint cells.\nLists, parent maps, heapq, and perf_counter()"),
        ]
        for index, (heading, body) in enumerate(sections):
            column, row = index % 2, index // 2
            card_height = min(
                142,
                max(110, (self.about_footer_rect.y - 220 - 48) // 3),
            )
            row_gap = (self.about_footer_rect.y - 220 - 3 * card_height) // 3
            x, y = 64 + column * 650, 220 + row * (card_height + row_gap)
            card = pygame.Rect(x, y, 610, card_height)
            pygame.draw.rect(surface, COLORS["panel"], card, border_radius=8)
            pygame.draw.rect(surface, COLORS["border"], card, 1, border_radius=8)
            draw_text(surface, heading, (x + 22, y + 16), size=12, color=COLORS["accent"], bold=True)
            for line_index, line in enumerate(body.split("\n")):
                draw_text(surface, line, (x + 22, y + 46 + line_index * 23), size=12, color=COLORS["text"])
        pygame.draw.rect(surface, COLORS["panel"], self.about_footer_rect, border_radius=8)
        draw_text(surface, "BUILT FOR OFFLINE USE", (88, self.about_footer_rect.y + 18), size=12, color=COLORS["cyan"], bold=True)
        draw_text(surface, "Python 3  /  Pygame  /  No database, API, or network connection required.", (88, self.about_footer_rect.y + 43), size=13, color=COLORS["text"])