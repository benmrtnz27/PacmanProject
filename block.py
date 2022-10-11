from pygame.sprite import Sprite
from pygame import Rect


class Block(Sprite):
    """Represents a generic block in the maze"""
    def __init__(self, x, y, width, height, image):
        super().__init__()
        self.rect = Rect(x, y, width, height)
        self.image = image