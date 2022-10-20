import pygame
from event_loop import EventLoop
from maze import Maze
from pacman import PacMan

class PacmanPortalGame:
    BLACK_BG = (0, 0, 0)
    START_EVENT = pygame.USEREVENT + 1
    REBUILD_EVENT = pygame.USEREVENT + 2
    LEVEL_TRANSITION_EVENT = pygame.USEREVENT + 3

    def __init__(self):
        pygame.init()
        self.screen = pygame.display.set_mode((800, 600))
        pygame.display.set_caption('PacMan Portal')
        self.clock = pygame.time.Clock()
        self.maze = Maze(screen=self.screen, maze_map_file='maze.txt')

        self.pause = False
        self.player = PacMan(screen=self.screen, maze=self.maze)

        self.actions = {PacmanPortalGame.REBUILD_EVENT: self.rebuild_maze}

    def rebuild_maze(self):
        self.maze.build_maze()
        self.player.reset_position()
        if self.player.dead:
                self.player.revive()
        if self.pause:
            self.pause = False

    def check_player(self):
        if not self.pause:
            pygame.mixer.stop()

    def update_screen(self):
        self.screen.fill(PacmanPortalGame.BLACK_BG)
        self.check_player()
        self.maze.blit()
        self.player.update()
        self.player.blit()
        pygame.display.flip()

    def run(self):
        e_loop = EventLoop(loop_running=True)

        while e_loop.loop_running:
            self.clock.tick(60)
            e_loop.check_events()
            self.screen.fill(PacmanPortalGame.BLACK_BG)
            self.play_game()
            pygame.display.flip()

    def play_game(self):
        e_loop = EventLoop(loop_running=True, actions={**self.player.event_map, **self.actions})
        if self.player.dead:
            self.player.revive()
            self.rebuild_maze()

        while e_loop.loop_running:
            self.clock.tick(60)
            e_loop.check_events()
            self.update_screen()

if __name__ == '__main__':
    game = PacmanPortalGame()
    game.run()