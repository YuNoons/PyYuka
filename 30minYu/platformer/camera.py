# camera.py
from config import SCREEN_HEIGHT, WORLD_HEIGHT

class Camera:
    def __init__(self):
        self.y = 0
        self.target_y = 0
    
    def update(self, player_y):
        """Обновление позиции камеры"""
        # Камера следует за игроком, когда он поднимается выше центра экрана
        screen_center = SCREEN_HEIGHT // 2
        
        if player_y < screen_center:
            # Игрок близко к земле - камера у нижней границы
            self.target_y = 0
        else:
            # Игрок поднимается - камера следует за ним, оставляя его в центре
            self.target_y = player_y - screen_center
        
        # Плавное движение камеры (интерполяция)
        self.y += (self.target_y - self.y) * 0.1
        
        # Ограничение камеры границами мира
        self.y = max(0, min(self.y, WORLD_HEIGHT - SCREEN_HEIGHT))
    
    def apply(self, y):
        """Применение смещения камеры к координате для отрисовки"""
        return y - self.y
    
    def get_position(self):
        """Возвращает текущую позицию камеры"""
        return self.y