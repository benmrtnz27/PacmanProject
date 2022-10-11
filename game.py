import pygame
from event_loop import EventLoop
from maze import Maze

class PacmanPortalGame:
    BLACK_BG = (0, 0, 0)

    def __init__(self):
        pygame.init()
        self.screen = pygame.display.set_mode((800, 600))
        pygame.display.set_caption('PacMan Portal')
        self.maze = Maze(screen=self.screen, maze_map_file='maze.txt')

    def rebuild_maze(self):
        self.maze.build_maze()

    def update_screen(self):
        self.screen.fill(PacmanPortalGame.BLACK_BG)
        self.maze.blit()
        pygame.display.flip()

    def run(self):
        e_loop = EventLoop(loop_running=True)

        while e_loop.loop_running:
            e_loop.check_events()
            self.screen.fill(PacmanPortalGame.BLACK_BG)
            self.play_game()
            pygame.display.flip()

    def play_game(self):
        e_loop = EventLoop(loop_running=True)
        while e_loop.loop_running:
            e_loop.check_events()
            self.update_screen()

if __name__ == '__main__':
    game = PacmanPortalGame()
    game.run()