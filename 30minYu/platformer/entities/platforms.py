# entities/platforms.py
import pygame
import random
from config import PLATFORM_WIDTH, PLATFORM_HEIGHT, COLORS, COIN_SPAWN_CHANCE, COIN_SIZE, WORLD_HEIGHT, SCREEN_WIDTH

class Platform:
    def __init__(self, x, y, width=PLATFORM_WIDTH, height=PLATFORM_HEIGHT):
        self.rect = pygame.Rect(x, y, width, height)
        self.has_coin = random.random() < COIN_SPAWN_CHANCE
        self.coin_collected = False
        
        if self.has_coin:
            coin_x = x + width // 2 - COIN_SIZE // 2
            coin_y = y - COIN_SIZE - 5
            self.coin_rect = pygame.Rect(coin_x, coin_y, COIN_SIZE, COIN_SIZE)
    
    def draw(self, screen, camera_y):
        """Отрисовка с учётом камеры"""
        screen_rect = self.rect.move(0, -camera_y)
        pygame.draw.rect(screen, COLORS['platform'], screen_rect, border_radius=5)
        pygame.draw.rect(screen, COLORS['text'], screen_rect, 2, border_radius=5)
        
        if self.has_coin and not self.coin_collected:
            coin_screen_rect = self.coin_rect.move(0, -camera_y)
            pygame.draw.circle(screen, COLORS['coin'], coin_screen_rect.center, COIN_SIZE // 2)
    
    def check_coin_collision(self, player_rect):
        if self.has_coin and not self.coin_collected and self.coin_rect.colliderect(player_rect):
            self.coin_collected = True
            return True
        return False

class PlatformManager:
    def __init__(self):
        self.platforms = []
        self._generate_initial_platforms()
    
    def _generate_initial_platforms(self):
        """Генерация начальных платформ"""
        # Стартовая платформа точно под игроком
        start_x = SCREEN_WIDTH // 2 - PLATFORM_WIDTH // 2
        start_y = WORLD_HEIGHT - 350
        self.platforms.append(Platform(start_x, start_y))

        # Генерация остальных платформ
        for i in range(50):
            x = random.randint(50, SCREEN_WIDTH - PLATFORM_WIDTH - 50)
            y = random.randint(100, WORLD_HEIGHT - 250)
            # Проверяем, чтобы платформы не пересекались
            new_platform = Platform(x, y)
            if not any(p.rect.colliderect(new_platform.rect) for p in self.platforms):
                self.platforms.append(new_platform)

    def update(self, player_rect):
        """Обновление состояния платформ и проверка монет"""
        coins_collected = 0
        for platform in self.platforms:
            if platform.check_coin_collision(player_rect):
                coins_collected += 1
        return coins_collected
    
    def draw(self, screen, camera_y):
        for platform in self.platforms:
            platform.draw(screen, camera_y)
    
    def get_platforms(self):
        return self.platforms