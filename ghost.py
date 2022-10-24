from pygame import time, sysfont
from pygame.sprite import Sprite, spritecollideany
from image_manager import ImageManager


class Ghost(Sprite):

    def __init__(self, screen, maze, target, spawn_info, ghost_file='ghost-red.png'):
        super().__init__()
        self.screen = screen
        self.maze = maze
        self.internal_map = maze.map_lines
        self.target = target
        self.norm_images = ImageManager(ghost_file, sheet=True, pos_offsets=[(0, 0, 32, 32), (0, 32, 32, 32)],
                                        resize=(self.maze.block_size // 1.8, self.maze.block_size // 1.8),
                                        animation_delay=250)
        self.blue_images = ImageManager('ghost-ppellet.png', sheet=True, pos_offsets=[(0, 0, 32, 32), (0, 32, 32, 32)],
                                        resize=(self.maze.block_size // 1.8, self.maze.block_size // 1.8),
                                        animation_delay=150)
        self.blue_warnings = ImageManager('ghost-ppellet-warn.png', sheet=True, pos_offsets=[(0, 0, 32, 32),
                                                                                             (0, 32, 32, 32)],
                                          resize=(self.maze.block_size // 1.8, self.maze.block_size // 1.8),
                                          animation_delay=150)
        self.eyes = ImageManager('ghost-eyes.png', sheet=True, pos_offsets=[(0, 0, 32, 32), (32, 0, 32, 32),
                                                                            (0, 32, 32, 32), (32, 32, 32, 32)],
                                 resize=(self.maze.block_size // 1.8, self.maze.block_size // 1.8),
                                 keys=['r', 'u', 'd', 'l'])
        self.score_font = sysfont.SysFont(None, 22)
        self.score_image = None
        self.image, self.rect = self.norm_images.get_image()
        self.curr_eye, _ = self.eyes.get_image(key='r')    # default eye to looking right
        self.image.blit(self.curr_eye, (0, 0))  # combine eyes and body
        self.return_tile = spawn_info[0]    # spawn tile
        self.return_path = None     # path back to spawn tile
        self.return_delay = 1000    # 1 second delay from being eaten to returning
        self.eaten_time = None   # timestamp for being eaten
        self.start_pos = spawn_info[1]
        self.reset_position()
        self.tile = spawn_info[0]
        self.direction = None
        self.last_position = None
        self.speed = maze.block_size / 10
        self.state = {'enabled': False, 'blue': False, 'return': False, 'speed_boost': False}
        self.blue_interval = 5000   # 5 second time limit for blue status
        self.blue_start = None  # timestamp for blue status start
        self.blink = False
        self.last_blink = time.get_ticks()
        self.blink_interval = 250

    @staticmethod
    def find_path(maze_map, start, target):
        path = []   # path list
        tried = set()   # set for faster membership checks
        done = False
        curr_tile = start
        while not done:
            if curr_tile == target:
                done = True     # if at target tile, we are done
            else:
                options = [     # possible moves
                    (curr_tile[0] + 1, curr_tile[1]),
                    (curr_tile[0] - 1, curr_tile[1]),
                    (curr_tile[0], curr_tile[1] + 1),
                    (curr_tile[0], curr_tile[1] - 1)
                ]
                test = (abs(target[0] - start[0]), abs(target[1] - start[0]))
                prefer = test.index(max(test[0], test[1]))
                if prefer == 0:
                    options.sort(key=lambda x: x[0], reverse=True)
                else:
                    options.sort(key=lambda x: x[1], reverse=True)
                backtrack = True    # assume we must backtrack
                for opt in options:
                    try:
                        if maze_map[opt[0]][opt[1]] not in ('x', ) and opt not in tried:
                            backtrack = False   # if we haven't tried this option before, and it's not blocked
                            path.append(opt)    # then add to the path, and remember that it's been tried
                            tried.add(opt)
                            curr_tile = opt
                            break
                    except IndexError:
                        continue
                if backtrack:   # backtrack to the previous position in the path
                    curr_tile = path.pop()
        return path

    def increase_speed(self):
        self.state['speed_boost'] = True
        self.speed = self.maze.block_size / 8

    def reset_speed(self):
        self.state['speed_boost'] = False
        self.speed = self.maze.block_size / 10

    def reset_position(self):
        self.rect.left, self.rect.top = self.start_pos

    def get_dir_from_path(self):
        try:
            next_step = self.return_path[0]
            if next_step[0] > self.tile[0]:
                return 'd'  # move up next
            if next_step[0] < self.tile[0]:
                return 'u'  # move down next
            if next_step[1] > self.tile[1]:
                return 'r'  # move right next
            if next_step[1] < self.tile[1]:
                return 'l'  # move left next
        except IndexError as ie:
            print('Error while trying to get new path direction', ie)
            return None

    def set_eaten(self):
        self.state['return'] = True
        self.state['blue'] = False
        self.tile = (self.get_nearest_row(), self.get_nearest_col())
        self.return_path = Ghost.find_path(self.internal_map, self.tile, self.return_tile)
        self.direction = self.get_dir_from_path()
        self.image = self.score_font.render('200', True, (255, 255, 255))
        self.eaten_time = time.get_ticks()

    def get_direction_options(self):
        tests = {
            'u': self.rect.move((0, -self.speed)),
            'l': self.rect.move((-self.speed, 0)),
            'd': self.rect.move((0, self.speed)),
            'r': self.rect.move((self.speed, 0))
        }
        remove = []
        original_pos = self.rect

        for d, t in tests.items():
            self.rect = t   # temporarily move self
            if spritecollideany(self, self.maze.maze_blocks) and d not in remove:
                remove.append(d)    # if collision, mark this direction for removal
            if spritecollideany(self, self.target.portal_controller.blue_portal) and d not in remove:
                remove.append(d)
            if spritecollideany(self, self.target.portal_controller.orange_portal) and d not in remove:
                remove.append(d)
        for rem in remove:
            del tests[rem]
        self.rect = original_pos    # reset position
        return list(tests.keys())

    def begin_blue_state(self):
        if not self.state['return']:
            self.state['blue'] = True
            self.image, _ = self.blue_images.get_image()
            self.blue_start = time.get_ticks()

    def change_eyes(self, look_direction):
        self.image, _ = self.norm_images.get_image()
        self.curr_eye, _ = self.eyes.get_image(key=look_direction)
        self.image.blit(self.curr_eye, (0, 0))  # combine eyes and body

    def get_chase_direction(self, options):
        pick_direction = None
        target_pos = (self.target.rect.centerx, self.target.rect.centery)
        test = (abs(target_pos[0]), abs(target_pos[1]))
        prefer = test.index(max(test[0], test[1]))
        if prefer == 0:     # x direction
            if target_pos[prefer] < self.rect.centerx:  # to the left
                pick_direction = 'l'
            elif target_pos[prefer] > self.rect.centerx:    # to the right
                pick_direction = 'r'
        else:   # y direction
            if target_pos[prefer] < self.rect.centery:  # upward
                pick_direction = 'u'
            elif target_pos[prefer] > self.rect.centery:    # downward
                pick_direction = 'd'
        if pick_direction not in options:   # desired direction not available
            if 'u' in options:  # pick a direction that is available
                return 'u'
            if 'l' in options:
                return 'l'
            if 'r' in options:
                return 'r'
            if 'd' in options:
                return 'd'
        else:   # desired direction available, return it
            return pick_direction

    def get_flee_direction(self, options):
        pick_direction = None
        target_pos = (self.target.rect.centerx, self.target.rect.centery)
        test = (abs(target_pos[0]), abs(target_pos[1]))
        prefer = test.index(max(test[0], test[1]))
        if prefer == 0:  # x direction
            if target_pos[prefer] < self.rect.centerx:  # to the left, so move right
                pick_direction = 'r'
            elif target_pos[prefer] > self.rect.centerx:  # to the right, so move left
                pick_direction = 'l'
        else:  # y direction
            if target_pos[prefer] < self.rect.centery:  # upward, so move down
                pick_direction = 'd'
            elif target_pos[prefer] > self.rect.centery:  # downward, so move up
                pick_direction = 'u'
        if pick_direction not in options:  # desired direction not available
            if 'u' in options:  # pick a direction that is available
                return 'u'
            if 'l' in options:
                return 'l'
            if 'd' in options:
                return 'd'
            if 'r' in options:
                return 'r'
        else:  # desired direction available, return it
            return pick_direction

    def get_nearest_col(self):
        return (self.rect.left - (self.screen.get_width() // 5)) // self.maze.block_size

    def get_nearest_row(self):
        return (self.rect.top - (self.screen.get_height() // 12)) // self.maze.block_size

    def is_at_intersection(self):
        directions = 0
        self.tile = (self.get_nearest_row(), self.get_nearest_col())
        if self.internal_map[self.tile[0] - 1][self.tile[1]] not in ('x', ):
            directions += 1
        if self.internal_map[self.tile[0] + 1][self.tile[1]] not in ('x', ):
            directions += 1
        if self.internal_map[self.tile[0]][self.tile[1] - 1] not in ('x', ):
            directions += 1
        if self.internal_map[self.tile[0]][self.tile[1] + 1] not in ('x', ):
            directions += 1
        return True if directions > 2 else False

    def enable(self):
        options = self.get_direction_options()
        self.direction = options[0]
        self.state['enabled'] = True

    def disable(self):
        self.direction = None 
        self.state['enabled'] = False  
        self.state['return'] = False
        self.return_path = None 
        if self.state['blue']:
            self.stop_blue_state()
        self.image, _ = self.norm_images.get_image() 

    def stop_blue_state(self):
        self.state['blue'] = False
        self.state['return'] = False
        self.image, _ = self.norm_images.get_image()

    def check_path_tile(self):
        self.tile = (self.get_nearest_row(), self.get_nearest_col())
        if self.return_path and self.tile == self.return_path[0]:
            del self.return_path[0]
            if not len(self.return_path) > 0:
                return '*' 
        return None

    def update_normal(self):
        options = self.get_direction_options()
        if self.is_at_intersection() or self.last_position == (self.rect.centerx, self.rect.centery):
            self.direction = self.get_chase_direction(options)
        if self.direction == 'u' and 'u' in options:
            self.rect.centery -= self.speed
        elif self.direction == 'l' and 'l' in options:
            self.rect.centerx -= self.speed
        elif self.direction == 'd' and 'd' in options:
            self.rect.centery += self.speed
        elif self.direction == 'r' and 'r' in options:
            self.rect.centerx += self.speed
        self.change_eyes(self.direction or 'r') 
        self.image = self.norm_images.next_image()

    def update_blue(self):
        self.image = self.blue_images.next_image()
        options = self.get_direction_options()
        if self.is_at_intersection() or self.last_position == (self.rect.centerx, self.rect.centery):
            self.direction = self.get_flee_direction(options)
        # print(self.internal_map[self.tile[0]][self.tile[1]])
        if self.direction == 'u' and 'u' in options:
            self.rect.centery -= self.speed
        elif self.direction == 'l' and 'l' in options:
            self.rect.centerx -= self.speed
        elif self.direction == 'd' and 'd' in options:
            self.rect.centery += self.speed
        elif self.direction == 'r' and 'r' in options:
            self.rect.centerx += self.speed
        if abs(self.blue_start - time.get_ticks()) > self.blue_interval:
            self.stop_blue_state()
        elif abs(self.blue_start - time.get_ticks()) > int(self.blue_interval * 0.5):
            if self.blink:
                self.image = self.blue_warnings.next_image()
                self.blink = False
                self.last_blink = time.get_ticks()
            elif abs(self.last_blink - time.get_ticks()) > self.blink_interval:
                self.blink = True

    def update_return(self):
        if abs(self.eaten_time - time.get_ticks()) > self.return_delay:
            self.image, _ = self.eyes.get_image(key=self.direction)
            test = self.check_path_tile()
            if test == '*':
                self.state['return'] = False
                self.direction = self.get_chase_direction(self.get_direction_options())
            else:
                self.direction = self.get_dir_from_path()
            if self.direction == 'u':
                self.rect.centery -= self.speed
            elif self.direction == 'l':
                self.rect.centerx -= self.speed
            elif self.direction == 'd':
                self.rect.centery += self.speed
            elif self.direction == 'r':
                self.rect.centerx += self.speed

    def update(self):
        if self.state['enabled']:
            if not self.state['blue'] and not self.state['return']:
                self.update_normal()
            elif self.state['blue']:
                self.update_blue()
            elif self.state['return']:
                self.update_return()
            self.last_position = (self.rect.centerx, self.rect.centery)

    def blit(self):
        self.screen.blit(self.image, self.rect)