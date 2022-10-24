import pygame as pg
import time


class Sound:
    def __init__(self, bg_music):
        pg.mixer.init()
        pg.mixer.music.load(bg_music)
        pg.mixer.music.set_volume(0.1)
        gameover_sound = pg.mixer.Sound('sounds/pacman_death.wav')
        eatfruit_sound = pg.mixer.Sound('sounds/pacman_eatfruit.wav')
        eatdot_sound = pg.mixer.Sound('sounds/wakawaka.wav')
        self.sounds = {'gameover': gameover_sound, 'eatfruit':eatfruit_sound, 'eatdot': eatdot_sound}

    def play_bg(self):
        pg.mixer.music.play(-1, 0.0)

    def stop_bg(self):
        pg.mixer.music.stop()

    def eat_fruit(self):
        pg.mixer.Sound.play(self.sound['eatfruit'])

    def eat_dot(self):
        pg.mixer.Sound.play(self.sound['eatdot'])

    def gameover(self):
        self.stop_bg()
        pg.mixer.music.load('sounds/pacman_death.wav')
        self.play_bg()
        time.sleep(2.8)
