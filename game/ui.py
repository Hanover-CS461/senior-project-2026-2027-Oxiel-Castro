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


def draw_bar(screen, font, x, y, width, height, value, max_value, color, label):
    """Draw a labeled progress bar showing value out of max_value."""
    pygame.draw.rect(screen, COLOR_BLACK, (x, y, width, height))
    fill = int(width * value / max_value)
    pygame.draw.rect(screen, color, (x, y, fill, height))
    text = font.render(label, True, COLOR_WHITE)
    screen.blit(text, (x, y - 26))