# game.py
import pygame
from config import SCREEN_WIDTH, SCREEN_HEIGHT, FPS, COLORS
from scenes.menu import MenuScene
from scenes.game_scene import GameScene
from scenes.shop import ShopScene
from scenes.death_screen import DeathScreen

class Game:
    def __init__(self):
        self.screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
        pygame.display.set_caption("Lava Jumper")
        self.clock = pygame.time.Clock()
        
        # Сцены
        self.scenes = {
            'menu': MenuScene(self),
            'game': GameScene(self),
            'shop': ShopScene(self),
            'death': DeathScreen(self)
        }
        
        self.current_scene = 'menu'
        self.running = True
        
        # Данные игры
        self.score = 0
        self.coins = 0
        self.best_score = 0
        
    def run(self):
        """Запуск одного кадра игры"""
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                return False
            self.scenes[self.current_scene].handle_event(event)
        
        self.scenes[self.current_scene].update()
        
        self.screen.fill(COLORS['background'])
        self.scenes[self.current_scene].draw(self.screen)
        pygame.display.flip()
        
        self.clock.tick(FPS)
        return self.running
    
    def switch_scene(self, scene_name, **kwargs):
        if scene_name in self.scenes:
            if hasattr(self.scenes[scene_name], 'reset'):
                self.scenes[scene_name].reset(**kwargs)
            self.current_scene = scene_name
    
    def quit_game(self):
        self.running = False