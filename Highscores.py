import pygame as pg
import shelve

class highscore_menu:

    def __init__(self):
        """Initialize the game's static settings."""
        

        self.resolution = (800,600) 
    
        self.screen = pg.display.set_mode(self.resolution)
        self.width = self.screen.get_width() 
        self.height = self.screen.get_height()
        self.hoverButton = (140,140,140) 
        self.restingButton = (50,50,50)
         
    
    
    def run(self):
        buttonFont = pg.font.SysFont('bahnschrift',30)
        white = (255,255,255) 
        a = shelve.open('score1.txt')
        highscore = a['score1']
        b = shelve.open('score2.txt')  
        highscore2 = b['score2'] 
        c = shelve.open('score3.txt')  
        highscore3 = c['score3']
        d = shelve.open('score4.txt')  
        highscore4 = d['score4']
        e = shelve.open('score5.txt')  
        highscore5 = e['score5'] 

        Highscore_str = f"1: {str(highscore)}"
        Highscore_str2 = f"2: {str(highscore2)}"
        Highscore_str3 = f"3: {str(highscore3)}"
        Highscore_str4 = f"4: {str(highscore4)}"
        Highscore_str5 = f"5: {str(highscore5)}"

        highscoreText = buttonFont.render(Highscore_str, True , white)
        highscoreText2 = buttonFont.render(Highscore_str2, True , white)
        highscoreText3 = buttonFont.render(Highscore_str3, True , white)
        highscoreText4 = buttonFont.render(Highscore_str4, True , white)
        highscoreText5 = buttonFont.render(Highscore_str5, True , white)
        
        





        white = (255,255,255) 
        buttonFont = pg.font.SysFont('bahnschrift',30)
        backText = buttonFont.render('Back' , True , white)
        while True:
            for ev in pg.event.get(): 

                if ev.type == pg.MOUSEBUTTONDOWN: 

                    if self.width/2-5 <= mouse[0] <= self.width/2+70 and self.height/2 -300 <= mouse[1] <= self.height/2 - 260: 
                        return
            pg.init() 
            self.screen.fill((0,0,0)) 
            mouse = pg.mouse.get_pos()
            if self.width/2-5 <= mouse[0] <= self.width/2+70 and self.height/2 - 300<= mouse[1] <= self.height/2-260: 
                pg.draw.rect(self.screen,self.hoverButton,[self.width/2-5,self.height/2-300,70,40])         
            else: 
                pg.draw.rect(self.screen,self.restingButton,[self.width/2-5,self.height/2-300,70,40]) 
            self.screen.blit(highscoreText, (self.width/2,self.height/2-200))
            self.screen.blit(highscoreText2, (self.width/2,self.height/2-100))
            self.screen.blit(highscoreText3, (self.width/2,self.height/2))
            self.screen.blit(highscoreText4, (self.width/2,self.height/2+100))
            self.screen.blit(highscoreText5, (self.width/2,self.height/2+200))
            self.screen.blit(backText , (self.width/2-5,self.height/2-300)) 
            pg.display.update()    





    
    
    
    
    #try:
    #    a = shelve.open('score.txt')  # here you will save the score variable   
    #    highscore = a['score']           # thats all, now it is saved on disk.  
    #except:
    #    highscore = 0
    #    a = shelve.open('score.txt')
    #    a['score'] = highscore
#
    #try:
    #    b = shelve.open('score2.txt')  
    #    highscore2 = b['score2'] 
    #    
    #except:
    #    highscore2 = 0
    #    b = shelve.open('score2.txt')
    #    b['score2'] = highscore2
    #    
    #try:
    #    c = shelve.open('score3.txt')  
    #    highscore3 = c['score3'] 
    #except: 
    #    highscore3 = 0
    #    c = shelve.open('score3.txt')
    #    c['score3'] = highscore3
    #try:
    #    d = shelve.open('score4.txt')  
    #    highscore4 = d['score4'] 
    #except: 
    #    highscore4 = 0
    #    d = shelve.open('score4.txt')
    #    d['score4'] = highscore4
    #try:
    #    e = shelve.open('score5.txt')  
    #    highscore5 = e['score5'] 
    #except: 
    #    highscore5 = 0
    #    e = shelve.open('score5.txt')
    #    e['score5'] = highscore5