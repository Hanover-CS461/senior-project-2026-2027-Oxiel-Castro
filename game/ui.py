import pygame

from config import (
    COLOR_BLACK,
    COLOR_BUTTON,
    COLOR_BUTTON_HOVER,
    COLOR_DISABLED,
    COLOR_DISABLED_TEXT,
    COLOR_WHITE,
)


class Button:
    """A clickable button with a hover effect."""

    def __init__(self, x, y, width, height, text, action):
        """Store the button's rect, label, and action id."""
        self.rect = pygame.Rect(x, y, width, height)
        self.text = text
        self.action = action
        self.color = COLOR_BUTTON
        self.hover_color = COLOR_BUTTON_HOVER

    def draw(self, screen, font):
        """Draw the button with a hover highlight and centered text."""
        mouse_pos = pygame.mouse.get_pos()
        color = self.hover_color if self.rect.collidepoint(mouse_pos) else self.color
        pygame.draw.rect(screen, color, self.rect, border_radius=5)
        pygame.draw.rect(screen, COLOR_BLACK, self.rect, width=3, border_radius=5)
        text_surface = font.render(self.text, True, COLOR_WHITE)
        text_rect = text_surface.get_rect(center=self.rect.center)
        screen.blit(text_surface, text_rect)


def draw_disabled_button(screen, button, font):
    """Draw a button in a disabled grey style."""
    pygame.draw.rect(screen, COLOR_DISABLED, button.rect, border_radius=5)
    pygame.draw.rect(screen, COLOR_BLACK, button.rect, width=3, border_radius=5)
    text_surface = font.render(button.text, True, COLOR_DISABLED_TEXT)
    text_rect = text_surface.get_rect(center=button.rect.center)
    screen.blit(text_surface, text_rect)


def draw_bar(screen, font, x, y, width, height, value, max_value, color, label=None):
    """Draw a progress bar showing value out of max_value."""
    pygame.draw.rect(screen, COLOR_BLACK, (x, y, width, height))
    fill = int(width * value / max_value)
    pygame.draw.rect(screen, color, (x, y, fill, height))
    if label is not None:
        draw_outlined_text(screen, font, label, (x, y - 26))


def draw_outlined_text(screen, font, text, pos, color=COLOR_WHITE, outline=COLOR_BLACK):
    """Draw text with a translucent black backing and outline for readability."""
    text_w, text_h = font.size(text)
    pad_x, pad_y = 8, 4
    box = pygame.Surface((text_w + pad_x * 2, text_h + pad_y * 2), pygame.SRCALPHA)
    box.fill((0, 0, 0, 110))
    base = font.render(text, True, color)
    mask = font.render(text, True, outline)
    x, y = pad_x, pad_y
    for dx, dy in ((-1, -1), (0, -1), (1, -1), (-1, 0), (1, 0), (-1, 1), (0, 1), (1, 1)):
        box.blit(mask, (x + dx, y + dy))
    box.blit(base, (x, y))
    screen.blit(box, pos)