import pygame
from config import *

class ShopSelectionWindow:
    def __init__(self, game):
        self.game = game
        self.visible = False
        self.rect = pygame.Rect(100, 100, 600, 400)
        self.close_button = pygame.Rect(self.rect.right - 30, self.rect.y + 10, 20, 20)
    
    def is_shop_available(self, shop_type):
        if self.game.balance < shop_type.cost:
            return False, "Недостаточно денег"
        
        if shop_type.requirement:
            for req_id, count in shop_type.requirement.items():
                current_count = sum(1 for shop in self.game.shops 
                                  if shop.shop_type.id == req_id and shop.is_operational)
                if current_count < count:
                    return False, f"Нужно {count} {self.game.shop_types[req_id].name}"
        
        return True, "Доступен"
    
    def draw(self, surface, fonts):
        # Фон окна
        pygame.draw.rect(surface, WHITE, self.rect)
        pygame.draw.rect(surface, BLACK, self.rect, 2)
        
        # Заголовок
        title_text = fonts['medium'].render("Выберите магазин для покупки", True, BLACK)
        surface.blit(title_text, (self.rect.x + 20, self.rect.y + 20))
        
        # Кнопка закрытия
        pygame.draw.rect(surface, RED, self.close_button)
        close_text = fonts['small'].render("X", True, WHITE)
        surface.blit(close_text, (self.close_button.x + 6, self.close_button.y + 2))
        
        # Список магазинов
        y_pos = self.rect.y + 60
        for shop_type in self.game.shop_types.values():
            self.draw_shop_info(surface, fonts, shop_type, y_pos)
            y_pos += 90
    
    def draw_shop_info(self, surface, fonts, shop_type, y_pos):
        available, reason = self.is_shop_available(shop_type)
        color = LIGHT_GREEN if available else LIGHT_GRAY
        
        shop_rect = pygame.Rect(self.rect.x + 20, y_pos, 560, 80)
        pygame.draw.rect(surface, color, shop_rect)
        pygame.draw.rect(surface, BLACK, shop_rect, 2)
        
        # Основная информация
        name_text = fonts['medium'].render(f"{shop_type.name} - ${shop_type.cost}", True, BLACK)
        surface.blit(name_text, (shop_rect.x + 10, shop_rect.y + 10))
        
        income_text = fonts['small'].render(f"Доход: ${shop_type.base_income}/сек", True, BLACK)
        surface.blit(income_text, (shop_rect.x + 10, shop_rect.y + 35))
        
        # ROI информация
        roi_text = fonts['small'].render(f"Окупаемость: {shop_type.roi_seconds:.1f} сек", True, DARK_GRAY)
        surface.blit(roi_text, (shop_rect.x + 10, shop_rect.y + 55))
        
        # Статус доступности
        status_color = GREEN if available else RED
        status_text = fonts['small'].render(reason, True, status_color)
        surface.blit(status_text, (shop_rect.x + 300, shop_rect.y + 35))
        
        # Кнопка покупки
        if available:
            buy_rect = pygame.Rect(shop_rect.right - 100, shop_rect.y + 40, 80, 30)
            pygame.draw.rect(surface, BLUE, buy_rect)
            buy_text = fonts['small'].render("Купить", True, WHITE)
            surface.blit(buy_text, (buy_rect.x + 15, buy_rect.y + 8))
    
    def handle_events(self, event_list):
        for event in event_list:
            if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
                mouse_pos = pygame.mouse.get_pos()
                
                # Закрытие окна
                if self.close_button.collidepoint(mouse_pos):
                    self.visible = False
                    return
                
                # Обработка покупки магазинов
                y_pos = self.rect.y + 60
                for shop_type in self.game.shop_types.values():
                    shop_rect = pygame.Rect(self.rect.x + 20, y_pos, 560, 80)
                    buy_rect = pygame.Rect(shop_rect.right - 100, shop_rect.y + 40, 80, 30)
                    
                    if buy_rect.collidepoint(mouse_pos):
                        available, _ = self.is_shop_available(shop_type)
                        if available:
                            self.game.buy_shop(shop_type)
                            self.visible = False
                            return
                    
                    y_pos += 90