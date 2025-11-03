import pygame
import time
from config import *
from shop import Shop
from shop_type import create_shop_types
from button import Button
from upgrade_system import UpgradeSystem
from shop_selection_window import ShopSelectionWindow
from save_system import save_game, load_game

class Game:
    def __init__(self):
        self.screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
        pygame.display.set_caption("Строительный бизнес симулятор")
        self.clock = pygame.time.Clock()
        self.fonts = init_fonts()
        
        # Игровое состояние
        self.balance = STARTING_BALANCE
        self.day = 0
        self.last_day_update = time.time()
        
        # Системы игры
        self.shops = []
        self.shop_types = create_shop_types(SHOP_TYPES_CONFIG)
        self.upgrade_system = UpgradeSystem()
        self.shop_selection_window = ShopSelectionWindow(self)
        
        # UI и скролл
        self.buttons = []
        self.selected_shop = None
        self.shop_scroll_offset = 0
        self.shop_item_height = 60
        self.visible_shops_count = 5
        self.setup_ui()
        
        # Временные переменные
        self.total_income = 0.0
        self.last_income_update = time.time()
        
        self.load_game_state()
    
    def setup_ui(self):
        self.buy_shop_button = Button(50, 500, 200, 50, "Купить магазин", 
                                     self.open_shop_selection, "buy")
        self.buttons.append(self.buy_shop_button)
        
        self.upgrade_button = Button(300, 500, 200, 50, "Улучшить все магазины", 
                                    self.buy_global_upgrade, "upgrade")
        self.buttons.append(self.upgrade_button)
        
        self.settings_button = Button(550, 500, 200, 50, "Настройки", 
                                     self.open_settings, "normal")
        self.buttons.append(self.settings_button)
    
    def open_shop_selection(self):
        self.shop_selection_window.visible = True
    
    def buy_global_upgrade(self):
        upgrade_cost = self.upgrade_system.current_cost
        if self.balance >= upgrade_cost:
            self.balance -= upgrade_cost
            self.upgrade_system.buy_upgrade()
            return True
        return False
    
    def buy_shop(self, shop_type):
        if self.balance >= shop_type.cost:
            self.balance -= shop_type.cost
            new_shop = Shop(shop_type)
            self.shops.append(new_shop)
            return True
        return False
    
    def open_settings(self):
        print("Открыть настройки")
    
    def handle_shop_selection(self, event_list):
        mouse_pos = pygame.mouse.get_pos()
        shop_list_rect = pygame.Rect(20, 110, 300, self.visible_shops_count * self.shop_item_height)
        
        if shop_list_rect.collidepoint(mouse_pos):
            for event in event_list:
                if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
                    # Вычисляем индекс магазина по позиции клика
                    relative_y = mouse_pos[1] - 110
                    shop_index = self.shop_scroll_offset + (relative_y // self.shop_item_height)
                    
                    if 0 <= shop_index < len(self.shops):
                        self.selected_shop = self.shops[shop_index]
                
                # Обработка скролла
                elif event.type == pygame.MOUSEWHEEL:
                    self.shop_scroll_offset -= event.y
                    self.shop_scroll_offset = max(0, min(self.shop_scroll_offset, 
                                                       len(self.shops) - self.visible_shops_count))
    
    def calculate_total_income(self):
        base_income = sum(shop.get_effective_income() for shop in self.shops if shop.is_operational)
        return base_income * self.upgrade_system.income_multiplier
    
    def update(self):
        current_time = time.time()
        
        # Обновление дней
        if current_time - self.last_day_update >= DAY_DURATION:
            self.day += 1
            self.last_day_update = current_time
            
            for shop in self.shops:
                shop.update_construction()
        
        # Начисление дохода
        delta_time = current_time - self.last_income_update
        self.last_income_update = current_time
        
        self.total_income = self.calculate_total_income()
        self.balance += self.total_income * delta_time
        
        # Обновление UI кнопок
        self.update_buttons_state()
    
    def update_buttons_state(self):
        upgrade_cost = self.upgrade_system.current_cost
        self.upgrade_button.text = f"Улучшить (${upgrade_cost:.1f})"
        self.upgrade_button.state = 'normal' if self.balance >= upgrade_cost else 'disabled'
        self.buy_shop_button.state = 'normal'
    
    def draw(self):
        self.screen.fill(WHITE)
        self.draw_top_panel()
        self.draw_shops_list()
        self.draw_upgrades_panel()
        
        for button in self.buttons:
            button.draw(self.screen, self.fonts)
        
        # Окно выбора магазинов
        if self.shop_selection_window.visible:
            self.shop_selection_window.draw(self.screen, self.fonts)
        
        pygame.display.flip()
    
    def draw_top_panel(self):
        panel_rect = pygame.Rect(0, 0, SCREEN_WIDTH, 60)
        pygame.draw.rect(self.screen, LIGHT_GRAY, panel_rect)
        pygame.draw.line(self.screen, BLACK, (0, 60), (SCREEN_WIDTH, 60), 2)
        
        day_text = self.fonts['medium'].render(f"День: {self.day}", True, BLACK)
        self.screen.blit(day_text, (20, 20))
        
        balance_text = self.fonts['medium'].render(f"Баланс: ${self.balance:.2f}", True, BLACK)
        self.screen.blit(balance_text, (200, 20))
        
        income_text = self.fonts['medium'].render(f"Доход: ${self.total_income:.2f}/сек", True, BLACK)
        self.screen.blit(income_text, (400, 20))
    
    def draw_shops_list(self):
        # Заголовок
        title_text = self.fonts['medium'].render("Ваши магазины:", True, BLACK)
        self.screen.blit(title_text, (20, 70))
        
        # Область списка магазинов
        list_bg = pygame.Rect(20, 110, 300, self.visible_shops_count * self.shop_item_height)
        pygame.draw.rect(self.screen, LIGHT_GRAY, list_bg)
        pygame.draw.rect(self.screen, BLACK, list_bg, 2)
        
        # Отображение магазинов с учетом скролла
        start_index = self.shop_scroll_offset
        end_index = min(start_index + self.visible_shops_count, len(self.shops))
        
        for i in range(start_index, end_index):
            shop = self.shops[i]
            shop_rect = pygame.Rect(25, 115 + (i - start_index) * self.shop_item_height, 
                                  290, self.shop_item_height - 5)
            
            # Выделение выбранного магазина
            if shop == self.selected_shop:
                pygame.draw.rect(self.screen, YELLOW, shop_rect)
                pygame.draw.rect(self.screen, BLACK, shop_rect, 2)
            else:
                pygame.draw.rect(self.screen, WHITE, shop_rect)
                pygame.draw.rect(self.screen, BLACK, shop_rect, 1)
            
            # Информация о магазине
            name_text = self.fonts['small'].render(shop.shop_type.name, True, BLACK)
            self.screen.blit(name_text, (shop_rect.x + 10, shop_rect.y + 10))
            
            if shop.is_operational:
                income = shop.get_effective_income() * self.upgrade_system.income_multiplier
                status_text = self.fonts['small'].render(f"Доход: ${income:.2f}/сек", True, BLACK)
                self.screen.blit(status_text, (shop_rect.x + 10, shop_rect.y + 35))
            else:
                status_text = self.fonts['small'].render(f"Строится: {shop.days_until_operational} д.", True, BLACK)
                self.screen.blit(status_text, (shop_rect.x + 10, shop_rect.y + 35))
    
    def draw_upgrades_panel(self):
        panel_rect = pygame.Rect(350, 60, SCREEN_WIDTH - 370, 400)
        pygame.draw.rect(self.screen, WHITE, panel_rect)
        pygame.draw.rect(self.screen, BLACK, panel_rect, 2)
        
        title_text = self.fonts['medium'].render("Глобальные улучшения:", True, BLACK)
        self.screen.blit(title_text, (360, 70))
        
        # Информация об улучшениях
        level_text = self.fonts['small'].render(f"Уровень улучшений: {self.upgrade_system.level}", True, BLACK)
        self.screen.blit(level_text, (360, 110))
        
        multiplier_text = self.fonts['small'].render(f"Множитель дохода: {self.upgrade_system.income_multiplier:.2f}x", True, BLACK)
        self.screen.blit(multiplier_text, (360, 140))
        
        if self.upgrade_system.level < 20:
            next_cost = self.upgrade_system.current_cost
            current_multiplier = self.upgrade_system.income_multiplier
            next_multiplier = self.upgrade_system.next_income_multiplier
            increase = (next_multiplier - current_multiplier) / current_multiplier * 100
            
            cost_text = self.fonts['small'].render(f"Следующее улучшение: ${next_cost:.2f}", True, BLACK)
            multiplier_increase_text = self.fonts['small'].render(f"+{increase:.1f}% к множителю", True, BLACK)
            
            self.screen.blit(cost_text, (360, 170))
            self.screen.blit(multiplier_increase_text, (360, 195))
    
    def load_game_state(self):
        saved_data = load_game()
        if saved_data:
            self.balance = saved_data.get('balance', STARTING_BALANCE)
            self.day = saved_data.get('day', 0)
            
            # Загрузка магазинов
            saved_shops = saved_data.get('shops', [])
            for i, shop_data in enumerate(saved_shops):
                shop_type_id = shop_data.get('shop_type_id', 1)
                shop_type = self.shop_types[shop_type_id]
                shop = Shop(shop_type)
                shop.upgrade_level = shop_data.get('upgrade_level', 0)
                shop.income_multiplier = shop_data.get('income_multiplier', 1.0)
                shop.is_operational = shop_data.get('is_operational', False)
                shop.days_until_operational = shop_data.get('days_until_operational', shop_type.construction_days)
                self.shops.append(shop)
    
    def run(self):
        running = True
        while running:
            event_list = pygame.event.get()
            for event in event_list:
                if event.type == pygame.QUIT:
                    save_game(self)
                    running = False
            
            # Обработка взаимодействий
            self.handle_shop_selection(event_list)
            
            # Обработка кнопок
            for button in self.buttons:
                action = button.update(event_list)
                if action:
                    action()
            
            # Обработка окна выбора магазинов
            if self.shop_selection_window.visible:
                self.shop_selection_window.handle_events(event_list)
            
            self.update()
            self.draw()
            self.clock.tick(FPS)
        
        pygame.quit()