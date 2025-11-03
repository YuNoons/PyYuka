import pygame

# Размеры окна
SCREEN_WIDTH = 800
SCREEN_HEIGHT = 600
FPS = 60

# Цвета
WHITE = (255, 255, 255)
BLACK = (0, 0, 0)
GRAY = (200, 200, 200)
LIGHT_GRAY = (230, 230, 230)
DARK_GRAY = (100, 100, 100)
GREEN = (100, 200, 100)
LIGHT_GREEN = (150, 255, 150)
DARK_GREEN = (50, 150, 50)
BLUE = (100, 100, 200)
LIGHT_BLUE = (150, 150, 255)
DARK_BLUE = (50, 50, 150)
YELLOW = (255, 255, 0)

# Игровые константы
STARTING_BALANCE = 10.0
SHOP_BASE_COST = 10.0
SHOP_BASE_INCOME = 0.5  # Увеличили с 0.1 до 0.5
UPGRADE_INCOME_MULTIPLIER = 1.1  # Уменьшили с 1.2 до 1.1 (+10%)
UPGRADE_COST_MULTIPLIER = 1.15
MAX_UPGRADES = 20
DAY_DURATION = 5  # секунд
CONSTRUCTION_TIME = 1  # дней

# Шрифты
def init_fonts():
    pygame.font.init()
    return {
        'small': pygame.font.SysFont('Arial', 20),
        'medium': pygame.font.SysFont('Arial', 24),
        'large': pygame.font.SysFont('Arial', 32)
    }