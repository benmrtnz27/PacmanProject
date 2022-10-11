from block import Block
from random import choice
from image_manager import ImageManager


class Fruit(Block):
    """Inherits from maze.Block to represent a fruit available for pickup in the maze"""
    def __init__(self, x, y, width, height):
        images = ['apple.png', 'cherry.png', 'peach.png', 'strawberry.png']
        fruit_image, _ = ImageManager(img=choice(images), resize=(width // 2, height // 2)).get_image()
        super(Fruit, self).__init__(x, y, width, height, fruit_image)