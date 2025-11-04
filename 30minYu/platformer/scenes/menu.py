# scenes/menu.py
import pygame
from scenes.base_scene import BaseScene
from config import COLORS, FONT_LARGE, FONT_MEDIUM, SCREEN_WIDTH, SCREEN_HEIGHT

class MenuScene(BaseScene):
    def __init__(self, game):
        super().__init__(game)
        self.buttons = []
        self._create_buttons()
    
    def _create_buttons(self):
        button_width, button_height = 200, 50
        center_x = SCREEN_WIDTH // 2 - button_width // 2
        
        # Кнопка "Играть"
        play_button = {
            'rect': pygame.Rect(center_x, 250, button_width, button_height),
            'text': 'ИГРАТЬ',
            'action': lambda: self.game.switch_scene('game')
        }
        
        # Кнопка "Магазин"
        shop_button = {
            'rect': pygame.Rect(center_x, 320, button_width, button_height),
            'text': 'МАГАЗИН', 
            'action': lambda: self.game.switch_scene('shop')
        }
        
        self.buttons = [play_button, shop_button]
    
    def handle_event(self, event):
        if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
            for button in self.buttons:
                if button['rect'].collidepoint(event.pos):
                    button['action']()
    
    def update(self):
        # Можно добавить анимации фона
        pass
    
    def draw(self, screen):
        # Заголовок
        title_text = FONT_LARGE.render("LAVA JUMPER", True, COLORS['text'])
        screen.blit(title_text, (SCREEN_WIDTH // 2 - title_text.get_width() // 2, 100))
        
        # Лучший счёт
        score_text = FONT_MEDIUM.render(f"Рекорд: {self.game.best_score}", True, COLORS['text'])
        screen.blit(score_text, (SCREEN_WIDTH // 2 - score_text.get_width() // 2, 170))
        
        # Монеты
        coins_text = FONT_MEDIUM.render(f"Монеты: {self.game.coins}", True, COLORS['coin'])
        screen.blit(coins_text, (SCREEN_WIDTH // 2 - coins_text.get_width() // 2, 200))
        
        # Кнопки
        for button in self.buttons:
            mouse_pos = pygame.mouse.get_pos()
            color = COLORS['button_hover'] if button['rect'].collidepoint(mouse_pos) else COLORS['button_normal']
            
            pygame.draw.rect(screen, color, button['rect'], border_radius=10)
            pygame.draw.rect(screen, COLORS['text'], button['rect'], 2, border_radius=10)
            
            text_surf = FONT_MEDIUM.render(button['text'], True, COLORS['button_text'])
            text_rect = text_surf.get_rect(center=button['rect'].center)
            screen.blit(text_surf, text_rect)