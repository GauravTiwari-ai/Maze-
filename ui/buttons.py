"""Small reusable button and text-drawing helpers."""

from dataclasses import dataclass

import pygame

from utils.constants import COLORS


def draw_text(
    surface: pygame.Surface,
    text: str,
    position: tuple[int, int],
    *,
    size: int = 18,
    color: tuple[int, int, int] | None = None,
    center: bool = False,
    bold: bool = False,
) -> pygame.Rect:
    font = pygame.font.SysFont("bahnschrift", size, bold=bold)
    rendered = font.render(text, True, color or COLORS["text"])
    rect = rendered.get_rect()
    if center:
        rect.center = position
    else:
        rect.topleft = position
    surface.blit(rendered, rect)
    return rect


@dataclass
class Button:
    rect: pygame.Rect
    label: str
    accent: tuple[int, int, int] = COLORS["accent"]
    fill: tuple[int, int, int] = COLORS["panel_light"]

    def draw(self, surface: pygame.Surface, *, active: bool = False) -> None:
        hovered = self.rect.collidepoint(pygame.mouse.get_pos())
        fill = self.accent if active else self.fill
        foreground = COLORS["background"] if active else COLORS["text"]
        if hovered and not active:
            fill = (37, 52, 61)
        pygame.draw.rect(surface, fill, self.rect, border_radius=8)
        pygame.draw.rect(surface, self.accent if active or hovered else COLORS["border"], self.rect, 1, border_radius=8)
        draw_text(surface, self.label, self.rect.center, size=15, color=foreground, center=True, bold=active)

    def clicked(self, event: pygame.event.Event) -> bool:
        return (
            event.type == pygame.MOUSEBUTTONDOWN
            and event.button == 1
            and self.rect.collidepoint(event.pos)
        )