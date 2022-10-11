import pygame
from block import Block
from fruit import Fruit
from random import randrange

class Maze:
    BLUE = (25, 25, 166)
    WHITE = (255, 255, 255)
    YELLOW = (255, 255, 0)

    def __init__(self, screen, maze_map_file):
        self.screen = screen
        self.map_file = maze_map_file
        self.block_size = 20

        # Create Block
        self.block_image = pygame.Surface((self.block_size, self.block_size)) 
        self.block_image.fill(Maze.BLUE)

        # Create Shield
        self.shield_image = pygame.Surface((self.block_size, self.block_size // 2))
        self.shield_image.fill(Maze.WHITE)

        # Create Pellet
        self.pellet_image = pygame.Surface((self.block_size // 4, self.block_size // 4))
        pygame.draw.circle(self.pellet_image, Maze.YELLOW, (self.block_size // 8, self.block_size // 8), self.block_size // 8)

        # Create Power Pellet
        self.ppellet_image = pygame.Surface((self.block_size // 2, self.block_size // 2))
        pygame.draw.circle(self.ppellet_image, Maze.WHITE, (self.block_size // 4, self.block_size // 4), self.block_size // 4)

        # Open and read file
        with open(self.map_file, 'r') as file:
            self.map_lines = file.readlines()

        # Create Sprite Groups 
        self.maze_blocks = pygame.sprite.Group()  
        self.shield_blocks = pygame.sprite.Group()
        self.pellets = pygame.sprite.Group()
        self.power_pellets = pygame.sprite.Group()
        self.fruits = pygame.sprite.Group()
        self.player_spawn = None 
        self.ghost_spawn = []
        self.build_maze()


    def build_maze(self):
        # reset maze assets if they exist already
        if self.maze_blocks or self.pellets or self.fruits or self.power_pellets or self.shield_blocks:
            self.maze_blocks.empty()
            self.pellets.empty()
            self.power_pellets.empty()
            self.fruits.empty()
            self.player_spawn = None    # spawn points
            self.ghost_spawn = []
            self.shield_blocks.empty()

        y_start = self.screen.get_height() // 12
        y = 0
        for i in range(len(self.map_lines)):
            line = self.map_lines[i]
            x_start = self.screen.get_width() // 5
            x = 0
            for j in range(len(line)):
                co = line[j]
                if co == 'x':
                    self.maze_blocks.add(Block(x_start + (x * self.block_size),
                                                y_start + (y * self.block_size),
                                                self.block_size, self.block_size,
                                                self.block_image))
                elif co == '*':
                    if randrange(0, 100) > 1:
                        self.pellets.add(Block(x_start + (self.block_size // 3) + (x * self.block_size),
                                                y_start + (self.block_size // 3) + (y * self.block_size),
                                                self.block_size, self.block_size,
                                                self.pellet_image))
                    else:
                        self.fruits.add(Fruit(x_start + (self.block_size // 4) + (x * self.block_size),
                                                y_start + (self.block_size // 4) + (y * self.block_size),
                                                self.block_size, self.block_size))
                elif co == '@':
                    self.power_pellets.add(Block(x_start + (self.block_size // 3) + (x * self.block_size),
                                                    y_start + (self.block_size // 3) + (y * self.block_size),
                                                    self.block_size, self.block_size,
                                                    self.ppellet_image))
                elif co == 's':
                    self.shield_blocks.add(Block(x_start + (x * self.block_size),
                                                    y_start + (y * self.block_size),
                                                    self.block_size // 2, self.block_size // 2,
                                                    self.shield_image))
                elif co == 'p':
                    self.player_spawn = [(i, j), (x_start + (x * self.block_size) + (self.block_size // 2),
                                            y_start + (y * self.block_size) + (self.block_size // 2))]
                elif co == 'g':
                    self.ghost_spawn.append(((i, j), (x_start + (x * self.block_size),
                                            y_start + (y * self.block_size))))
                x += 1
            y += 1

    def blit(self):
        self.maze_blocks.draw(self.screen)
        self.pellets.draw(self.screen)
        self.power_pellets.draw(self.screen)
        self.fruits.draw(self.screen)
        self.shield_blocks.draw(self.screen)