import pygame
from sys import exit


class EventLoop:
    """Contains the logic for checking events in a game loop"""
    def __init__(self, loop_running=False, actions=None):
        self.action_map = {pygame.QUIT: exit, }
        if isinstance(actions, dict):
            self.action_map.update(actions)     # add custom actions, if provided
        self.loop_running = loop_running

    def check_events(self):
        """Check events to see if any match mapped actions"""
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                self.action_map[event.type]()   # quit game with no argument passed
            elif event.type in self.action_map:
                try:
                    self.action_map[event.type](event)    # execute events from map
                except TypeError:
                    self.action_map[event.type]()   # event function may not accept any parameters