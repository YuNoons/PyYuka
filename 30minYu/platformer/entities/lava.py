# entities/lava.py
import pygame
from config import COLORS, SCREEN_WIDTH, LAVA_RISE_SPEED, WORLD_HEIGHT

class Lava:
    def __init__(self):
        self.height = 100
        self.world_y = WORLD_HEIGHT - 100  # ИСПРАВЛЕНО: было -200, стало -100 (выше!)
        self.rise_speed = LAVA_RISE_SPEED
        self.rect = pygame.Rect(0, self.world_y, SCREEN_WIDTH, self.height)
    
    def update(self):
        """Подъём лавы"""
        self.world_y -= self.rise_speed
        self.rect.y = self.world_y
    
    def check_collision(self, player_rect):
        return player_rect.colliderect(self.rect)
    
    def draw(self, screen, camera_y):
        """Отрисовка с учётом камеры"""
        screen_y = self.world_y - camera_y
        lava_rect = pygame.Rect(0, screen_y, SCREEN_WIDTH, self.height)
        
        # Основной цвет
        pygame.draw.rect(screen, COLORS['lava'], lava_rect)
        
        # Верхняя полоса
        pygame.draw.rect(screen, (255, 100, 50), (0, screen_y, SCREEN_WIDTH, 15))
    
    def get_height(self):
        return self.world_y