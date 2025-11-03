import pygame
from config import *

class Button:
    def __init__(self, x, y, width, height, text, action=None, button_type="normal"):
        self.rect = pygame.Rect(x, y, width, height)
        self.text = text
        self.action = action
        self.state = 'normal'
        self.type = button_type
        
        # Цвета в зависимости от типа кнопки
        if button_type == "buy":
            self.colors = {
                'normal': LIGHT_GREEN,
                'hover': GREEN,
                'pressed': DARK_GREEN,
                'disabled': LIGHT_GRAY
            }
        elif button_type == "upgrade":
            self.colors = {
                'normal': LIGHT_BLUE,
                'hover': BLUE,
                'pressed': DARK_BLUE,
                'disabled': LIGHT_GRAY
            }
        else:  # normal/settings
            self.colors = {
                'normal': LIGHT_GRAY,
                'hover': GRAY,
                'pressed': DARK_GRAY,
                'disabled': LIGHT_GRAY
            }
    
    def draw(self, surface, fonts):
        pygame.draw.rect(surface, self.colors[self.state], self.rect)
        pygame.draw.rect(surface, BLACK, self.rect, 2)
        
        text_surf = fonts['small'].render(self.text, True, BLACK)
        text_rect = text_surf.get_rect(center=self.rect.center)
        surface.blit(text_surf, text_rect)
    
    def update(self, event_list):
        mouse_pos = pygame.mouse.get_pos()
        if self.state != 'disabled':
            if self.rect.collidepoint(mouse_pos):
                self.state = 'hover'
                for event in event_list:
                    if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
                        self.state = 'pressed'
                        if self.action:
                            return self.action
            else:
                self.state = 'normal'
        return None