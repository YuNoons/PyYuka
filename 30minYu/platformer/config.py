# config.py
import pygame
import os

# Инициализация Pygame
pygame.init()

# ========== ПУТИ ==========
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
ASSETS_DIR = os.path.join(BASE_DIR, 'assets')

# ========== ОКНО ==========
SCREEN_WIDTH = 800
SCREEN_HEIGHT = 600
FPS = 60

# ========== ЦВЕТА ==========
COLORS = {
    'background': (20, 20, 30),
    'player': (50, 150, 200),
    'platform': (100, 200, 100),
    'lava': (200, 80, 50),
    'text': (255, 255, 255),
    'button_normal': (70, 130, 180),
    'button_hover': (90, 160, 210),
    'button_text': (255, 255, 255),
    'coin': (255, 215, 0),
}

# ========== ФИЗИКА ==========
GRAVITY = 0.5
JUMP_FORCE = -12
PLAYER_SPEED = 5
TERMINAL_VELOCITY = 15

# ========== РАЗМЕРЫ ==========
PLAYER_WIDTH = 30
PLAYER_HEIGHT = 40
PLATFORM_WIDTH = 80
PLATFORM_HEIGHT = 20
COIN_SIZE = 15

# ========== МИР ==========
WORLD_HEIGHT = 2000  # Высота игрового мира
LAVA_START_HEIGHT = WORLD_HEIGHT - 200

# ========== ШРИФТЫ ==========
FONT_SMALL = pygame.font.Font(None, 24)
FONT_MEDIUM = pygame.font.Font(None, 32)
FONT_LARGE = pygame.font.Font(None, 48)

# ========== ГЕЙМПЛЕЙ ==========
PLATFORM_SPAWN_RATE = 45
COIN_SPAWN_CHANCE = 0.3
LAVA_RISE_SPEED = 0.5