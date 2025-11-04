import pygame
import math

class UpgradesPanel:
    def __init__(self, game, x, y, width, height):
        self.game = game
        self.rect = pygame.Rect(x, y, width, height)
        
        # Загрузка шрифтов
        try:
            self.title_font = pygame.font.Font('assets/fonts/main.ttf', 20)
            self.font = pygame.font.Font('assets/fonts/main.ttf', 16)
            self.small_font = pygame.font.Font('assets/fonts/main.ttf', 14)
        except:
            self.title_font = pygame.font.SysFont('Arial', 20, bold=True)
            self.font = pygame.font.SysFont('Arial', 16)
            self.small_font = pygame.font.SysFont('Arial', 14)
        
        # Цветовая схема
        self.colors = {
            'background': (255, 255, 255, 200),
            'card_background': (245, 248, 255, 180),
            'text': (50, 50, 80),
            'text_secondary': (100, 100, 130),
            'success': (65, 185, 130),
            'error': (220, 90, 90),
            'button': (80, 150, 220),
            'button_hover': (100, 170, 240),
            'button_disabled': (200, 210, 220),
            'upgrade_available': (255, 240, 150)
        }
        
        # Иконки улучшений
        self.upgrade_icons = {
            "elevator_system": "🔼",
            "facade_renovation": "🏢", 
            "infrastructure": "⚡"
        }

    def draw_glass_card(self, surface, rect, color):
        """Рисует стеклянную карточку"""
        card_surface = pygame.Surface((rect.width, rect.height), pygame.SRCALPHA)
        pygame.draw.rect(card_surface, color, (0, 0, rect.width, rect.height), border_radius=12)
        
        # Блик
        pygame.draw.rect(card_surface, (255, 255, 255, 40), 
                        (0, 0, rect.width, rect.height//4), 
                        border_radius=12)
        
        surface.blit(card_surface, (rect.x, rect.y))
        return rect

    def draw_upgrade_card(self, surface, rect, upgrade_data, can_afford):
        """Рисует карточку улучшения"""
        # Фон карточки
        self.draw_glass_card(surface, rect, self.colors['card_background'])
        
        # Иконка и название
        icon = self.upgrade_icons.get(upgrade_data['name'], "⭐")
        title_text = f"{icon} {upgrade_data.get('display_name', upgrade_data['name'])}"
        title_surface = self.font.render(title_text, True, self.colors['text'])
        surface.blit(title_surface, (rect.x + 15, rect.y + 12))
        
        # Уровень
        level_text = f"Ур. {upgrade_data['current_level']}/{upgrade_data['max_level']}"
        level_surface = self.small_font.render(level_text, True, self.colors['text_secondary'])
        surface.blit(level_surface, (rect.x + 15, rect.y + 35))
        
        # Эффекты
        if upgrade_data['effects']:
            effects_text = " • ".join(upgrade_data['effects'])
            effects_surface = self.small_font.render(effects_text, True, self.colors['text_secondary'])
            surface.blit(effects_surface, (rect.x + 15, rect.y + 55))
        
        # Кнопка улучшения
        if upgrade_data['current_level'] < upgrade_data['max_level']:
            button_rect = pygame.Rect(rect.right - 130, rect.y + 15, 115, 50)
            self.draw_upgrade_button(surface, button_rect, upgrade_data, can_afford)

    def draw_upgrade_button(self, surface, rect, upgrade_data, can_afford):
        """Рисует кнопку улучшения"""
        mouse_pos = pygame.mouse.get_pos()
        hover = rect.collidepoint(mouse_pos) and can_afford
        
        # Тень
        shadow_rect = rect.copy()
        shadow_rect.x += 2
        shadow_rect.y += 2
        pygame.draw.rect(surface, (0, 0, 0, 30), shadow_rect, border_radius=8)
        
        # Основная кнопка
        if can_afford:
            color = self.colors['button_hover'] if hover else self.colors['button']
        else:
            color = self.colors['button_disabled']
            
        pygame.draw.rect(surface, color, rect, border_radius=8)
        
        # Блик
        highlight_rect = pygame.Rect(rect.x, rect.y, rect.width, rect.height//3)
        pygame.draw.rect(surface, (255, 255, 255, 60), highlight_rect, border_radius=8)
        
        # Текст стоимости
        cost_text = f"{upgrade_data['next_cost']} руб."
        text_surface = self.small_font.render(cost_text, True, self.colors['text'])
        surface.blit(text_surface, (rect.centerx - text_surface.get_width()//2, 
                                  rect.centery - text_surface.get_height()//2))

    def render(self, surface):
        """Отрисовка панели улучшений"""
        # Фон панели
        self.draw_glass_card(surface, self.rect, self.colors['background'])
        
        # Заголовок
        title = self.title_font.render("🚀 Глобальные улучшения", True, self.colors['text'])
        surface.blit(title, (self.rect.x + 15, self.rect.y + 15))
        
        y_offset = 50
        card_height = 100
        
        # Улучшения
        upgrades = [
            ("elevator_system", "Система лифтов"),
            ("facade_renovation", "Реновация фасада"), 
            ("infrastructure", "Инфраструктура")
        ]
        
        for upgrade_type, display_name in upgrades:
            info = self.game.get_global_upgrade_info(upgrade_type)
            
            if "error" in info:
                continue
            
            info['display_name'] = display_name
            info['name'] = upgrade_type
            
            card_rect = pygame.Rect(self.rect.x + 10, self.rect.y + y_offset, 
                                  self.rect.width - 20, card_height)
            
            can_afford = self.game.money >= info.get('next_cost', 0) if info['current_level'] < info['max_level'] else False
            
            self.draw_upgrade_card(surface, card_rect, info, can_afford)
            y_offset += card_height + 10

    def handle_click(self, pos):
        """Обработка кликов по панели улучшений"""
        if not self.rect.collidepoint(pos):
            return False
        
        x, y = pos
        y_offset = 50
        card_height = 100
        
        upgrades = ["elevator_system", "facade_renovation", "infrastructure"]
        
        for upgrade_type in upgrades:
            card_rect = pygame.Rect(self.rect.x + 10, self.rect.y + y_offset, 
                                  self.rect.width - 20, card_height)
            
            if card_rect.collidepoint(x, y):
                button_rect = pygame.Rect(card_rect.right - 130, card_rect.y + 15, 115, 50)
                if button_rect.collidepoint(x, y):
                    if self.game.buy_global_upgrade(upgrade_type):
                        return True
            
            y_offset += card_height + 10
        
        return False