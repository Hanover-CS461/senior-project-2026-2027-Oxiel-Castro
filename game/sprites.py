import pygame


class SpriteSheet:
    """Loads a sprite sheet and crops frames from it."""

    def __init__(self, filename):
        """Load the image with transparency."""
        self.sheet = pygame.image.load(filename).convert_alpha()

    def frame(self, rect):
        """Return the part of the sheet defined by rect."""
        return self.sheet.subsurface(rect)


def load_frames(path, frame_rects, size=None, scale=None, flip=False, normalize=False):
    """Load a sprite sheet and scale its frames to a size or scale factor."""
    sheet = SpriteSheet(path)
    frames = []
    max_w = max_h = 0
    if normalize:
        for x, y, w, h in frame_rects:
            fw = w if size is None else size[0]
            fh = h if size is None else size[1]
            if scale is not None:
                fw, fh = int(w * scale), int(h * scale)
            max_w, max_h = max(max_w, fw), max(max_h, fh)
    for x, y, w, h in frame_rects:
        frame = sheet.frame((x, y, w, h))
        if size is not None:
            frame = pygame.transform.scale(frame, size)
        elif scale is not None:
            frame = pygame.transform.scale(frame, (int(w * scale), int(h * scale)))
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