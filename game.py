import pygame
from event_loop import EventLoop
from maze import Maze
from pacman import PacMan
from live_status import PacManCounter
from ghost import Ghost
import shelve
from score import ScoreController, LevelTransition
from sound import Sound
from ReusedTimer import Timer
from Highscores import highscore_menu


class PacmanPortalGame:
    BLACK_BG = (0, 0, 0)
    START_EVENT = pygame.USEREVENT + 1
    REBUILD_EVENT = pygame.USEREVENT + 2
    LEVEL_TRANSITION_EVENT = pygame.USEREVENT + 3

    def __init__(self):
        pygame.init()
        self.screen = pygame.display.set_mode(
            (800, 600)
        )
        pygame.display.set_caption('PacMan Portal')
        self.clock = pygame.time.Clock()
        self.score_keeper = ScoreController(screen=self.screen,
                                            sb_pos=((self.screen.get_width() // 5),
                                                    (self.screen.get_height() * 0.965)),
                                            items_image='cherry.png',
                                            itc_pos=(int(self.screen.get_width() * 0.6),
                                                     self.screen.get_height() * 0.965))
        self.maze = Maze(screen=self.screen, maze_map_file='maze_map.txt')
        self.life_counter = PacManCounter(screen=self.screen, ct_pos=((self.screen.get_width() // 3),
                                                                      (self.screen.get_height() * 0.965)),
                                          images_size=(self.maze.block_size, self.maze.block_size))
        self.level_transition = LevelTransition(screen=self.screen, score_controller=self.score_keeper)
        self.game_over = True
        self.pause = False
        self.player = PacMan(screen=self.screen, maze=self.maze)
        self.ghosts = pygame.sprite.Group()
        self.ghost_active_interval = 2500
        self.ghosts_to_activate = None
        self.first_ghost = None
        self.other_ghosts = []
        self.spawn_ghosts()
        self.actions = {PacmanPortalGame.START_EVENT: self.init_ghosts,
                        PacmanPortalGame.REBUILD_EVENT: self.rebuild_maze,
                        PacmanPortalGame.LEVEL_TRANSITION_EVENT: self.next_level}
        
        self.sound = Sound(bg_music="sounds/wakawaka.wav")

    def init_ghosts(self):
        if not self.first_ghost.state['enabled']:
            self.first_ghost.enable()
            self.ghosts_to_activate = self.other_ghosts.copy()
            pygame.time.set_timer(PacmanPortalGame.START_EVENT, 0) 
            pygame.time.set_timer(PacmanPortalGame.START_EVENT, self.ghost_active_interval)
        else:
            try:
                g = self.ghosts_to_activate.pop()
                g.enable()
            except IndexError:
                pygame.time.set_timer(PacmanPortalGame.START_EVENT, 0) 

    def spawn_ghosts(self):
        files = ['ghost-pink.png', 'ghost-lblue.png', 'ghost-orange.png', 'ghost-red.png']
        idx = 0
        while len(self.maze.ghost_spawn) > 0:
            spawn_info = self.maze.ghost_spawn.pop()
            g = Ghost(screen=self.screen, maze=self.maze, target=self.player,
                      spawn_info=spawn_info, ghost_file=files[idx])
            if files[idx] == 'ghost-red.png':
                self.first_ghost = g    # red ghost should be first
            else:
                self.other_ghosts.append(g)
            self.ghosts.add(g)
            idx = (idx + 1) % len(files)

    def next_level(self):
        pygame.time.set_timer(PacmanPortalGame.LEVEL_TRANSITION_EVENT, 0)
        self.player.clear_portals()
        self.score_keeper.increment_level()
        self.rebuild_maze()

    def rebuild_maze(self):
        if self.life_counter.lives > 0:
            for g in self.ghosts:
                if g.state['enabled']:
                    g.disable()
            self.maze.build_maze()
            self.player.reset_position()
            for g in self.ghosts:
                g.reset_position()
            if self.player.dead:
                self.player.revive()
                if self.player.lives == 0:
                    self.player.lives=3
                    main()
            if self.pause:
                self.pause = False
            self.level_transition.set_show_transition()
        else:
            self.game_over = True
        pygame.time.set_timer(PacmanPortalGame.REBUILD_EVENT, 0)  

    def check_player(self):
        n_score, n_fruits, power = self.player.eat()
        self.score_keeper.add_score(score=n_score, items=n_fruits if n_fruits > 0 else None)
        if power:
            for g in self.ghosts:
                g.begin_blue_state()
        ghost_collide = pygame.sprite.spritecollideany(self.player, self.ghosts)
        if ghost_collide and ghost_collide.state['blue']:
            ghost_collide.set_eaten()
            self.score_keeper.add_score(200)
        elif ghost_collide and not (self.player.dead or ghost_collide.state['return']):
            self.life_counter.decrement()
            self.player.clear_portals()
            self.player.set_death()
            for g in self.ghosts:
                if g.state['enabled']:   # disable any ghosts
                    g.disable()
            pygame.time.set_timer(PacmanPortalGame.START_EVENT, 0)  # cancel start event
            pygame.time.set_timer(PacmanPortalGame.REBUILD_EVENT, 4000)
        elif not self.maze.pellets_left() and not self.pause:
            pygame.mixer.stop()
            self.pause = True
            pygame.time.set_timer(PacmanPortalGame.LEVEL_TRANSITION_EVENT, 1000)

    def update_screen(self):
        if not self.level_transition.transition_show:
            self.screen.fill(PacmanPortalGame.BLACK_BG)
            self.check_player()
            self.maze.blit()
            if not self.pause:
                self.ghosts.update()
                self.player.update()
                self.maze.teleport.check_teleport(self.player.rect) 
            for g in self.ghosts:
                if self.score_keeper.level > 3:
                    if not g.state['speed_boost']:
                        g.increase_speed()
                    self.maze.teleport.check_teleport(g.rect) 
                g.blit()
            self.player.blit()
        elif self.player.dead:
            self.player.update()
            self.player.blit()
        else:
            self.level_transition.draw()
            if not self.level_transition.transition_show:
                self.init_ghosts()
        pygame.display.flip()

    def run(self):
        e_loop = EventLoop(loop_running=True)

        while e_loop.loop_running:
            self.clock.tick(60)  
            e_loop.check_events()
            self.screen.fill(PacmanPortalGame.BLACK_BG)
            pygame.mixer.music.stop() 
            self.play_game()  
            for g in self.ghosts:
                g.reset_speed()
            self.score_keeper.save_high_scores() 
            pygame.display.flip()

    def play_game(self):
        self.sound.play_bg()
        e_loop = EventLoop(loop_running=True, actions={**self.player.event_map, **self.actions})
        self.level_transition.set_show_transition()
        self.game_over = False
        if self.player.dead:
            self.player.revive()
            self.score_keeper.reset_level()
            self.life_counter.reset_counter()
            self.rebuild_maze()

        while e_loop.loop_running:
            self.clock.tick(60)
            e_loop.check_events()
            self.update_screen()
            if self.game_over:
                pygame.mixer.stop()
                self.score_keeper.reset_level()
                e_loop.loop_running = False

import pygame as pg


def main():
    highmenu = highscore_menu()
    
    pg.init() 

    resolution = (800, 600) 
    
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
        a = shelve.open('score1.txt')  # here you will save the score variable   
        highscore = a['score1']           # thats all, now it is saved on disk.  
    except:
        highscore = 0
        a = shelve.open('score1.txt')
        a['score1'] = highscore

    try:
        b = shelve.open('score2.txt')  
        highscore2 = b['score2'] 
        
    except:
        highscore2 = 0
        b = shelve.open('score2.txt')
        b['score2'] = highscore2

    try:
        c = shelve.open('score3.txt')  
        highscore3 = c['score3'] 
    except: 
        highscore3 = 0
        c = shelve.open('score3.txt')
        c['score3'] = highscore3
    try:
        d = shelve.open('score4.txt')  
        highscore4 = d['score4'] 
    except: 
        highscore4 = 0
        d = shelve.open('score4.txt')
        d['score4'] = highscore4
    try:
        e = shelve.open('score5.txt')  
        highscore5 = e['score5'] 
    except: 
        highscore5 = 0
        e = shelve.open('score5.txt')
        e['score5'] = highscore5
    
    
    Highscore_str = f"Highscore: {str(highscore)}"
    d.close()
    quitText = buttonFont.render('Quit' , True , white) 
    playtext = buttonFont.render('Play' , True , white) 
    scorestext = buttonFont.render('Scores' , True , white) 
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
                if width/2-5 <= mouse[0] <= width/2+70 and height/2 +150 <= mouse[1] <= height/2+190:
                    highmenu.run()
                    
                    
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

        if width/2-5 <= mouse[0] <= width/2+70 and height/2 + 150<= mouse[1] <= height/2+190: 
            pg.draw.rect(screen,hoverButton,[width/2-20,height/2+150,100,40]) 
            
        else: 
            pg.draw.rect(screen,restingButton,[width/2-20, height/2+150,100,40]) 
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
        titleimages0 = [pg.transform.rotozoom(pg.image.load(f'startani/frame_{n}_delay-0.1s.jpg'), 0, .6) for n in range(5, 16 , 1)]
        timerAni = Timer(image_list=titleimages0, delay = 10, is_loop = True)
        
        image = timerAni.image()
        
        screen.blit(image, (width/2-100,height/2-150) )
        #titleimageTimer = Timer(titleimages0)
        screen.blit(quitText , (width/2,height/2+100)) 
        screen.blit(scorestext , (width/2-15,height/2+150)) 
        screen.blit(playtext , (width/2,height/2+52))
        screen.blit(title1, (width/2.8,height/2-300))
        screen.blit(highscoreText, (width/2-530,height/2-350)) 
        
        #screen.blit(redGhost, (width/2-50,height/2-150))
        #screen.blit(blueGhost, (width/2+50,height/2-150))
        #screen.blit(orangeGhost, (width/2+150,height/2-150))
       
        
        pg.font.get_fonts()

        
        # updates the frames of the game 
        pg.display.update() 
    
        

if __name__ == '__main__':
    game = PacmanPortalGame()
    #game.run()
    main()
