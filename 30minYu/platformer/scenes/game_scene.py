# scenes/game_scene.py
import pygame
from scenes.base_scene import BaseScene
from entities.player import Player
from entities.platforms import PlatformManager
from entities.lava import Lava
from camera import Camera
from config import COLORS, FONT_MEDIUM, SCREEN_WIDTH, SCREEN_HEIGHT, WORLD_HEIGHT

class GameScene(BaseScene):
    def __init__(self, game):
        super().__init__(game)
        self.reset()
    
    def reset(self, **kwargs):
        # Создаём игрока ВЫШЕ лавы
        start_x = SCREEN_WIDTH // 2 - 15
        start_y = WORLD_HEIGHT - 400
        
        self.player = Player(start_x, start_y)
        self.platform_manager = PlatformManager()
        self.lava = Lava()
        self.camera = Camera()
        
        # Игровые переменные
        self.score = 0
        self.coins_collected = 0
        self.start_time = pygame.time.get_ticks()
        self.is_game_over = False
        
        # Границы мира
        self.world_bounds = pygame.Rect(0, 0, SCREEN_WIDTH, WORLD_HEIGHT)
    
    def handle_event(self, event):
        if self.is_game_over:
            if event.type == pygame.KEYDOWN and event.key == pygame.K_SPACE:
                self.game.switch_scene('death', score=self.score, coins=self.coins_collected)
            return
        
        if event.type == pygame.KEYDOWN:
            if event.key == pygame.K_SPACE:
                self.player.jump()
            elif event.key == pygame.K_LEFT:
                self.player.move_left()
            elif event.key == pygame.K_RIGHT:
                self.player.move_right()
                
        elif event.type == pygame.KEYUP:
            if event.key in (pygame.K_LEFT, pygame.K_RIGHT):
                self.player.stop()
    
    def update(self):
        if self.is_game_over:
            return
        
        # Обновление времени и счёта
        current_time = pygame.time.get_ticks()
        self.score = (current_time - self.start_time) // 1000
        
        # Обновление игрока
        platforms = self.platform_manager.get_platforms()
        self.player.update(platforms, self.world_bounds)
        
        # Обновление камеры
        self.camera.update(self.player.rect.y)
        
        # Обновление лавы
        self.lava.update()
        
        # Проверка сбора монет
        new_coins = self.platform_manager.update(self.player.rect)
        self.coins_collected += new_coins
        
        # Проверка условий проигрыша
        if (self.lava.check_collision(self.player.rect) or 
            not self.player.is_alive or 
            self.player.rect.top > WORLD_HEIGHT):
            self.is_game_over = True
        
        # Обновление рекорда
        if self.score > self.game.best_score:
            self.game.best_score = self.score

    def draw(self, screen):
        # Очистка экрана
        screen.fill(COLORS['background'])
        
        # Отрисовка игровых объектов с учётом камеры
        camera_y = self.camera.y
        self.platform_manager.draw(screen, camera_y)
        self.lava.draw(screen, camera_y)
        self.player.draw(screen, camera_y)
        
        # Интерфейс
        score_text = FONT_MEDIUM.render(f"Счёт: {self.score}", True, COLORS['text'])
        screen.blit(score_text, (20, 20))
        
        coins_text = FONT_MEDIUM.render(f"Монеты: {self.coins_collected}", True, COLORS['coin'])
        screen.blit(coins_text, (20, 50))
        
        # Отладочная информация
        debug_text = FONT_MEDIUM.render(f"На земле: {self.player.on_ground}", True, COLORS['text'])
        screen.blit(debug_text, (20, 80))
        
        # Сообщение о поражении
        if self.is_game_over:
            overlay = pygame.Surface((SCREEN_WIDTH, SCREEN_HEIGHT))
            overlay.set_alpha(128)
            overlay.fill((0, 0, 0))
            screen.blit(overlay, (0, 0))
            
            game_over_font = pygame.font.Font(None, 64)
            game_over_text = game_over_font.render("ПОРАЖЕНИЕ!", True, (255, 50, 50))
            text_rect = game_over_text.get_rect(center=(SCREEN_WIDTH // 2, SCREEN_HEIGHT // 2 - 50))
            screen.blit(game_over_text, text_rect)
            
            continue_text = FONT_MEDIUM.render("Нажмите ПРОБЕЛ для продолжения", True, COLORS['text'])
            continue_rect = continue_text.get_rect(center=(SCREEN_WIDTH // 2, SCREEN_HEIGHT // 2 + 20))
            screen.blit(continue_text, continue_rect)