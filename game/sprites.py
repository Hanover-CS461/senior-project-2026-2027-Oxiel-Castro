import pygame

_image_cache = {}


def load_image(path, size=None):
    """Load an image, optionally scaled, caching it by path and size."""
    key = (path, size)
    cached = _image_cache.get(key)
    if cached is not None:
        return cached
    image = pygame.image.load(path).convert()
    if size is not None:
        image = pygame.transform.scale(image, size)
    _image_cache[key] = image
    return image


class SpriteSheet:
    """Loads a sprite sheet and crops frames from it."""

    def __init__(self, filename):
        """Load the image with transparency."""
        self.sheet = pygame.image.load(filename).convert_alpha()

    def frame(self, rect):
        """Return the part of the sheet defined by rect."""
        return self.sheet.subsurface(rect)


def _frame_size(w, h, size, scale):
    """Return the drawn (width, height) for a frame given size/scale options."""
    if size is not None:
        return size
    if scale is not None:
        return int(w * scale), int(h * scale)
    return w, h


def load_frames(path, frame_rects, size=None, scale=None, flip=False, normalize=False):
    """Load a sprite sheet and scale its frames to a size or scale factor."""
    sheet = SpriteSheet(path)
    frames = []
    max_w = max_h = 0
    if normalize:
        for x, y, w, h in frame_rects:
            fw, fh = _frame_size(w, h, size, scale)
            max_w, max_h = max(max_w, fw), max(max_h, fh)
    for x, y, w, h in frame_rects:
        frame = sheet.frame((x, y, w, h))
        drawn_size = _frame_size(w, h, size, scale)
        if drawn_size != frame.get_size():
            frame = pygame.transform.scale(frame, drawn_size)
        if flip:
            frame = pygame.transform.flip(frame, True, False)
        if normalize:
            canvas = pygame.Surface((max_w, max_h), pygame.SRCALPHA)
            canvas.blit(
                frame,
                ((max_w - frame.get_width()) // 2, (max_h - frame.get_height()) // 2),
            )
            frame = canvas
        frames.append(frame)
    return frames