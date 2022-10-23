import pygame
from image_manager import ImageManager
import shelve


class PacMan(pygame.sprite.Sprite):
    PAC_YELLOW = (255, 255, 0)

    def __init__(self, screen, maze):
        super().__init__()
        self.screen = screen
        self.radius = maze.block_size // 5
        self.maze = maze
        self.score = 0
        self.bg_color = (0, 0, 0)
        d = shelve.open('score.txt')
        self.high_score = d['score']
        d.close()
        self.text_color = (150, 150, 150)
        self.font = pygame.font.SysFont(None, 48)
        self.score_image = None 
        self.score_rect = None
        self.prep_score()

        self.horizontal_images = ImageManager('pacman-horiz.png', sheet=True, pos_offsets=[(0, 0, 32, 32),
                                                                                           (32, 0, 32, 32),
                                                                                           (0, 32, 32, 32),
                                                                                           (32, 32, 32, 32),
                                                                                           (0, 64, 32, 32)],
                                              resize=(self.maze.block_size // 1.2, self.maze.block_size // 1.2),
                                              reversible=True)
        self.vertical_images = ImageManager('pacman-vert.png', sheet=True, pos_offsets=[(0, 0, 32, 32),
                                                                                        (32, 0, 32, 32),
                                                                                        (0, 32, 32, 32),
                                                                                        (32, 32, 32, 32),
                                                                                        (0, 64, 32, 32)],
                                            resize=(self.maze.block_size // 1.2, self.maze.block_size // 1.2),
                                            reversible=True)
        self.death_images = ImageManager('pacman-death.png', sheet=True, pos_offsets=[(0, 0, 32, 32),
                                                                                      (32, 0, 32, 32),
                                                                                      (0, 32, 32, 32),
                                                                                      (32, 32, 32, 32),
                                                                                      (0, 64, 32, 32),
                                                                                      (32, 64, 32, 32)],
                                         resize=(self.maze.block_size // 1.2, self.maze.block_size // 1.2),
                                         animation_delay=150, repeat=False)
        self.flip_status = {'use_horiz': True, 'h_flip': False, 'v_flip': False}
        self.spawn_info = self.maze.player_spawn[1]
        self.tile = self.maze.player_spawn[0]
        self.direction = None
        self.moving = False
        self.speed = maze.block_size // 7
        self.image, self.rect = self.horizontal_images.get_image()
        self.rect.centerx, self.rect.centery = self.spawn_info   # screen coordinates for spawn
        self.dead = False

        # Keyboard related events/actions/releases
        self.event_map = {pygame.KEYDOWN: self.perform_action, pygame.KEYUP: self.reset_direction}
        self.action_map = {pygame.K_UP: self.set_move_up, pygame.K_LEFT: self.set_move_left,
                           pygame.K_DOWN: self.set_move_down, pygame.K_RIGHT: self.set_move_right}

    def set_death(self):
        self.dead = True
        self.image, _ = self.death_images.get_image()

    def revive(self):
        self.dead = False
        self.image, _ = self.horizontal_images.get_image()
        self.death_images.image_index = 0

    def reset_position(self):
        self.rect.centerx, self.rect.centery = self.spawn_info 

    def reset_direction(self, event):
        if event.key in (pygame.K_UP, pygame.K_DOWN, pygame.K_LEFT, pygame.K_RIGHT):
            self.moving = False

    def perform_action(self, event):
        if event.key in self.action_map:
            self.action_map[event.key]()

    def set_move_up(self):
        if self.direction != 'u':
            self.direction = 'u'
            if self.flip_status['v_flip']:
                self.vertical_images.flip(False, True)
                self.flip_status['v_flip'] = False
            self.flip_status['use_horiz'] = False
        self.moving = True

    def set_move_left(self):
        if self.direction != 'l':
            self.direction = 'l'
            if not self.flip_status['h_flip']:
                self.horizontal_images.flip()
                self.flip_status['h_flip'] = True
            self.flip_status['use_horiz'] = True
        self.moving = True

    def set_move_down(self):
        if self.direction != 'd':
            self.direction = 'd'
            if not self.flip_status['v_flip']:
                self.vertical_images.flip(x_bool=False, y_bool=True)
                self.flip_status['v_flip'] = True
            self.flip_status['use_horiz'] = False
        self.moving = True

    def set_move_right(self):
        if self.direction != 'r':
            self.direction = 'r'
            if self.flip_status['h_flip']:
                self.horizontal_images.flip()
                self.flip_status['h_flip'] = False
            self.flip_status['use_horiz'] = True
        self.moving = True

    def get_nearest_col(self):
        return (self.rect.x - (self.screen.get_width() // 5)) // self.maze.block_size

    def get_nearest_row(self):
        return (self.rect.y - (self.screen.get_height() // 12)) // self.maze.block_size

    def is_blocked(self):
        result = False
        if self.direction is not None and self.moving:
            original_pos = self.rect
            if self.direction == 'u':
                test = self.rect.move((0, -self.speed))
            elif self.direction == 'l':
                test = self.rect.move((-self.speed, 0))
            elif self.direction == 'd':
                test = self.rect.move((0, self.speed))
            else:
                test = self.rect.move((self.speed, 0))
            self.rect = test    # temporarily move self

            # if any collision, result = True
            if pygame.sprite.spritecollideany(self, self.maze.maze_blocks):
                result = True
            elif pygame.sprite.spritecollideany(self, self.maze.shield_blocks):
                result = True
            self.rect = original_pos    # reset position
        return result

    def update(self):
        if not self.dead:
            if self.direction and self.moving:
                if self.flip_status['use_horiz']:
                    self.image = self.horizontal_images.next_image()
                else:
                    self.image = self.vertical_images.next_image()
                if not self.is_blocked():
                    if self.direction == 'u':
                        self.rect.centery -= self.speed
                    elif self.direction == 'l':
                        self.rect.centerx -= self.speed
                    elif self.direction == 'd':
                        self.rect.centery += self.speed
                    elif self.direction == 'r':
                        self.rect.centerx += self.speed
                self.tile = (self.get_nearest_row(), self.get_nearest_col())
        else:
            self.image = self.death_images.next_image()
        self.eat()

    def blit(self):
        self.screen.blit(self.image, self.rect)

    def eat(self):
        score = 0
        fruit_count = 0
        power = None
        collision = pygame.sprite.spritecollideany(self, self.maze.pellets)
        if collision:
            collision.kill()
            score += 10
            self.score += 10
        collision = pygame.sprite.spritecollideany(self, self.maze.fruits)
        if collision:
            collision.kill()
            score += 20
            self.score += 10
            fruit_count += 1
        collision = pygame.sprite.spritecollideany(self, self.maze.power_pellets)
        if collision:
            collision.kill()
            score += 20
            self.score += 10
            power = True
        if self.score > self.high_score:
            self.high_score = self.score
            d = shelve.open('score.txt')
            d['score'] = self.high_score
            d.close() 
        self.prep_score()
        self.update_score()
        return score, fruit_count, power
    
    
    def prep_score(self):
        score_str = f"Score: {str(self.score)}"
        #high = shelve.open('score.txt')
        #high_str = f"Highscore: {str(high['score'])}"
        #high.close()

        self.score_image = self.font.render(score_str, True, self.text_color, self.bg_color)
        #self.highscore_image = self.font.render(high_str, True, self.text_color, self.settings.bg_color)
        # Display the score at the top right of the screen.
        self.score_rect = self.score_image.get_rect()
        #self.score_rect.right = 680
        #self.score_rect.top = 20

       #self.highscore_rect = self.highscore_image.get_rect()
       #self.highscore_rect.left = self.screen_rect.left + 20
       #self.highscore_rect.top = 20
    
    def reset_score(self): 
        self.score = 0
        self.update()

    def update_score(self): 
        # other stuff
        self.draw_score()

    def draw_score(self): 
        self.screen.blit(self.score_image, self.score_rect)
        #self.screen.blit(self.highscore_image, self.highscore_rect)
    
    
