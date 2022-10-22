import pygame
from event_loop import EventLoop
from maze import Maze
from pacman import PacMan
import shelve

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
import pygame as pg
import shelve



def main():

    pg.init() 

    resolution = (1080,720) 
    
    screen = pg.display.set_mode(resolution) 
    
    
    #for button placement
    width = screen.get_width() 
    height = screen.get_height() 

    white = (255,255,255) 
    
    
    # for hovering over the button 
    hoverButton = (140,140,140) 
    
    # resting button shade 
    restingButton = (50,50,50) 
    
    buttonFont = pg.font.SysFont('bahnschrift',30) 
    titlefont = pg.font.SysFont('bahnschrift',80) 
    try:
        d = shelve.open('score.txt')  # here you will save the score variable   
        highscore = d['score']           # thats all, now it is saved on disk.
    except:
        highscore = 0
        d = shelve.open('score.txt')
        d['score'] = highscore
    
    Highscore_str = f"Highscore: {str(highscore)}"
    d.close()
    quitText = buttonFont.render('Quit' , True , white) 
    playtext = buttonFont.render('Play' , True , white) 
    highscoreText = buttonFont.render(Highscore_str, True , white) 
    
    
    
    

    
    while True: 
        
        for ev in pg.event.get(): 
            
            if ev.type == pg.MOUSEBUTTONDOWN: 
                
                if width/2-5 <= mouse[0] <= width/2+70 and height/2 + 100 <= mouse[1] <= height/2 + 140: 
                    pg.quit() 
                if width/2-5 <= mouse[0] <= width/2+70 and height/2 +52 <= mouse[1] <= height/2+90:
                    pass
                    game.run()
                    #g.play()
                    
        # black background maybe add stars later
        screen.fill((0,0,0)) 
        
        
        mouse = pg.mouse.get_pos() 
        
        # if mouse is hovered on a button it 
        # changes to lighter shade 
        if width/2-5 <= mouse[0] <= width/2+70 and height/2 + 100<= mouse[1] <= height/2+140: 
            pg.draw.rect(screen,hoverButton,[width/2-5,height/2+100,70,40]) 
            
        else: 
            pg.draw.rect(screen,restingButton,[width/2-5,height/2+100,70,40]) 
        
        if width/2-5 <= mouse[0] <= width/2+70 and height/2+52 <= mouse[1] <= height/2+90: 
            pg.draw.rect(screen,hoverButton,[width/2-5,height/2+52,70,40]) 
            
        else: 
            pg.draw.rect(screen,restingButton,[width/2-5,height/2+52,70,40]) 
        pinkGhost   = pg.image.load(f'images/pinkGhost.png')
        pinkGhost   = pg. transform. scale(pinkGhost, (104, 104))
        redGhost    = pg.image.load(f'images/redGhost.png')
        redGhost    = pg. transform. scale(redGhost, (104, 104))
        blueGhost   = pg.image.load(f'images/blueGhost.png')
        blueGhost   = pg. transform. scale(blueGhost, (104, 104))
        orangeGhost = pg.image.load(f'images/orangeGhost.png')
        orangeGhost = pg. transform. scale(orangeGhost, (104, 104))
        title1 = pg.image.load(f'images/pacmanTitle.png')
        title1 = pg. transform. scale(title1, (400, 123))

        
        screen.blit(quitText , (width/2,height/2+100)) 
        screen.blit(playtext , (width/2,height/2+52))
        screen.blit(title1, (width/2.8,height/2-300))
        screen.blit(highscoreText, (width/2-530,height/2-350))
        
        screen.blit(pinkGhost, (width/2-150,height/2-150))
        screen.blit(redGhost, (width/2-50,height/2-150))
        screen.blit(blueGhost, (width/2+50,height/2-150))
        screen.blit(orangeGhost, (width/2+150,height/2-150))
       
        
        pg.font.get_fonts()

        
        # updates the frames of the game 
        pg.display.update() 
    
        

if __name__ == '__main__':
    game = PacmanPortalGame()
    main()
