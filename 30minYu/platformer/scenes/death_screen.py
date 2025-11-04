# scenes/death_screen.py
import pygame
from scenes.base_scene import BaseScene
from config import COLORS, FONT_LARGE, FONT_MEDIUM, SCREEN_WIDTH, SCREEN_HEIGHT

class DeathScreen(BaseScene):
    def __init__(self, game):
        super().__init__(game)
        self.fade_alpha = 0
        self.max_fade_alpha = 180
        self.fade_speed = 8
        self.is_fade_complete = False
        self.final_score = 0
        self.final_coins = 0
        self.buttons = []
        
    def reset(self, **kwargs):
        self.fade_alpha = 0
        self.is_fade_complete = False
        self.final_score = kwargs.get('score', 0)
        self.final_coins = kwargs.get('coins', 0)
        self.game.coins += self.final_coins
        self._create_buttons()
    
    def _create_buttons(self):
        button_width, button_height = 200, 50
        center_x = SCREEN_WIDTH // 2 - button_width // 2
        
        self.buttons = [
            {
                'rect': pygame.Rect(center_x, 350, button_width, button_height),
                'text': 'ЗАНОВО',
                'action': lambda: self.game.switch_scene('game')
            },
            {
                'rect': pygame.Rect(center_x, 420, button_width, button_height),
                'text': 'МАГАЗИН',
                'action': lambda: self.game.switch_scene('shop')
            },
            {
                'rect': pygame.Rect(center_x, 490, button_width, button_height),
                'text': 'В МЕНЮ',
                'action': lambda: self.game.switch_scene('menu')
            }
        ]
    
    def handle_event(self, event):
        if not self.is_fade_complete:
            return
            
        if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
            for button in self.buttons:
                if button['rect'].collidepoint(event.pos):
                    button['action']()
    
    def update(self):
        if self.fade_alpha < self.max_fade_alpha:
            self.fade_alpha += self.fade_speed
            if self.fade_alpha >= self.max_fade_alpha:
                self.fade_alpha = self.max_fade_alpha
                self.is_fade_complete = True
    
    def draw(self, screen):
        # Затемнение
        fade_surface = pygame.Surface((SCREEN_WIDTH, SCREEN_HEIGHT))
        fade_surface.set_alpha(self.fade_alpha)
        fade_surface.fill((0, 0, 0))
        screen.blit(fade_surface, (0, 0))
        
        if self.is_fade_complete:
            title_text = FONT_LARGE.render("ИГРА ОКОНЧЕНА", True, (255, 100, 100))
            screen.blit(title_text, (SCREEN_WIDTH // 2 - title_text.get_width() // 2, 150))
            
            score_text = FONT_MEDIUM.render(f"Ваш счёт: {self.final_score}", True, COLORS['text'])
            screen.blit(score_text, (SCREEN_WIDTH // 2 - score_text.get_width() // 2, 220))
            
            coins_text = FONT_MEDIUM.render(f"Собрано монет: {self.final_coins}", True, COLORS['coin'])
            screen.blit(coins_text, (SCREEN_WIDTH // 2 - coins_text.get_width() // 2, 260))
            
            best_text = FONT_MEDIUM.render(f"Рекорд: {self.game.best_score}", True, COLORS['text'])
            screen.blit(best_text, (SCREEN_WIDTH // 2 - best_text.get_width() // 2, 300))
            
            # Кнопки
            for button in self.buttons:
                mouse_pos = pygame.mouse.get_pos()
                color = COLORS['button_hover'] if button['rect'].collidepoint(mouse_pos) else COLORS['button_normal']
                
                pygame.draw.rect(screen, color, button['rect'], border_radius=10)
                pygame.draw.rect(screen, COLORS['text'], button['rect'], 2, border_radius=10)
                
                text_surf = FONT_MEDIUM.render(button['text'], True, COLORS['button_text'])
                text_rect = text_surf.get_rect(center=button['rect'].center)
                screen.blit(text_surf, text_rect)