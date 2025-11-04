# entities/player.py
import pygame
from config import PLAYER_WIDTH, PLAYER_HEIGHT, COLORS, GRAVITY, JUMP_FORCE, PLAYER_SPEED, TERMINAL_VELOCITY

class Player:
    def __init__(self, x, y):
        self.rect = pygame.Rect(x, y, PLAYER_WIDTH, PLAYER_HEIGHT)
        self.velocity_x = 0
        self.velocity_y = 0
        self.on_ground = False
        self.is_alive = True
        
    def update(self, platforms, world_bounds):
        """Обновление физики игрока"""
        # Гравитация с ограничением максимальной скорости
        self.velocity_y = min(self.velocity_y + GRAVITY, TERMINAL_VELOCITY)
        
        # Сохраняем старую позицию для корректной обработки коллизий
        old_rect = self.rect.copy()
        
        # Горизонтальное движение
        self.rect.x += self.velocity_x
        
        # Ограничение по горизонтали
        self.rect.x = max(world_bounds.left, min(self.rect.x, world_bounds.right - PLAYER_WIDTH))
        
        # Вертикальное движение
        self.rect.y += self.velocity_y
        
        # Сбрасываем состояние на земле
        self.on_ground = False
        
        # Проверка коллизий с платформами
        for platform in platforms:
            if self._check_platform_collision(platform, old_rect):
                break
        
        # Проверка выхода за нижнюю границу мира
        if self.rect.top > world_bounds.bottom:
            self.is_alive = False
    
    def _check_platform_collision(self, platform, old_rect):
        """Проверка и обработка коллизии с платформой"""
        # Проверяем пересечение с платформой
        if not self.rect.colliderect(platform.rect):
            return False
            
        # Определяем направление движения
        if old_rect.bottom <= platform.rect.top and self.velocity_y > 0:
            # Падаем на платформу сверху
            self.rect.bottom = platform.rect.top
            self.velocity_y = 0
            self.on_ground = True
            return True
        elif old_rect.top >= platform.rect.bottom and self.velocity_y < 0:
            # Ударяемся головой о платформу снизу
            self.rect.top = platform.rect.bottom
            self.velocity_y = 0
            return True
        elif old_rect.right <= platform.rect.left and self.velocity_x > 0:
            # Ударяемся о платформу слева
            self.rect.right = platform.rect.left
            return True
        elif old_rect.left >= platform.rect.right and self.velocity_x < 0:
            # Ударяемся о платформу справа
            self.rect.left = platform.rect.right
            return True
            
        return False
    
    def jump(self):
        """Прыжок"""
        if self.on_ground:
            self.velocity_y = JUMP_FORCE
            self.on_ground = False
    
    def move_left(self):
        self.velocity_x = -PLAYER_SPEED
    
    def move_right(self):
        self.velocity_x = PLAYER_SPEED
    
    def stop(self):
        self.velocity_x = 0
    
    def get_position(self):
        """Возвращает позицию в мировых координатах"""
        return self.rect.x, self.rect.y
    
    def draw(self, screen, camera_y):
        """Отрисовка с учётом камеры"""
        screen_rect = self.rect.move(0, -camera_y)
        pygame.draw.rect(screen, COLORS['player'], screen_rect, border_radius=8)