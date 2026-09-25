import pygame


class SpriteSheet:
    """Loads a sprite sheet and crops frames from it."""

    def __init__(self, filename):
        """Load the image with transparency."""
        self.sheet = pygame.image.load(filename).convert_alpha()

    def frame(self, rect):
        """Return the part of the sheet defined by rect."""
        return self.sheet.subsurface(rect)


def load_frames(path, frame_rects, size=None, scale=None, flip=False):
    """Load a sprite sheet and scale its frames to a size or scale factor."""
    sheet = SpriteSheet(path)
    frames = []
    for x, y, w, h in frame_rects:
        frame = sheet.frame((x, y, w, h))
        if size is not None:
            frame = pygame.transform.scale(frame, size)
        elif scale is not None:
            frame = pygame.transform.scale(frame, (w * scale, h * scale))
        if flip:
            frame = pygame.transform.flip(frame, True, False)
        frames.append(frame)
    return frames