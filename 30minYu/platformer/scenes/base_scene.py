# scenes/base_scene.py
import pygame

class BaseScene:
    def __init__(self, game):
        self.game = game
    
    def handle_event(self, event):
        pass
    
    def update(self):
        pass
    
    def draw(self, screen):
        pass
    
    def reset(self, **kwargs):
        pass