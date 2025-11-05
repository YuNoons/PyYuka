import pygame
import time
import math
from config.game_config import GameConfig
from .upgrades_panel import UpgradesPanel
from .ui_components import Button, UIManager

class VisualEffects:
    """Класс для визуальных эффектов и анимаций"""
    @staticmethod
    def draw_gradient_rect(surface, rect, start_color, end_color, vertical=True):
        """Рисует градиентный прямоугольник"""
        if vertical:
            for y in range(rect.height):
                ratio = y / rect.height
                color = [
                    start_color[i] + (end_color[i] - start_color[i]) * ratio
                    for i in range(3)
                ]
                pygame.draw.line(surface, color, 
                               (rect.x, rect.y + y), 
                               (rect.x + rect.width, rect.y + y))
        else:
            for x in range(rect.width):
                ratio = x / rect.width
                color = [
                    start_color[i] + (end_color[i] - start_color[i]) * ratio
                    for i in range(3)
                ]
                pygame.draw.line(surface, color,
                               (rect.x + x, rect.y),
                               (rect.x + x, rect.y + rect.height))

    @staticmethod
    def draw_glass_effect(surface, rect, color, alpha=128):
        """Рисует стеклянный эффект"""
        glass_surface = pygame.Surface((rect.width, rect.height), pygame.SRCALPHA)
        pygame.draw.rect(glass_surface, (*color, alpha), 
                        (0, 0, rect.width, rect.height), 
                        border_radius=12)
        # Добавляем блик
        pygame.draw.rect(glass_surface, (255, 255, 255, 60),
                        (0, 0, rect.width, rect.height//3),
                        border_radius=12)
        surface.blit(glass_surface, (rect.x, rect.y))

    @staticmethod
    def draw_modern_button(surface, rect, text, font, colors, hover=False, disabled=False):
        """Рисует современную кнопку"""
        if disabled:
            bg_color = colors['button_disabled']
            text_color = colors['text_disabled']
        elif hover:
            bg_color = colors['button_hover']
            text_color = colors['text']
        else:
            bg_color = colors['button']
            text_color = colors['text']

        # Тень
        shadow_rect = rect.copy()
        shadow_rect.x += 3
        shadow_rect.y += 3
        pygame.draw.rect(surface, (0, 0, 0, 30), shadow_rect, border_radius=8)
        
        # Основная кнопка
        pygame.draw.rect(surface, bg_color, rect, border_radius=8)
        
        # Блик
        highlight_rect = pygame.Rect(rect.x, rect.y, rect.width, rect.height//3)
        pygame.draw.rect(surface, (255, 255, 255, 60), highlight_rect, border_radius=8)
        
        # Текст
        text_surf = font.render(text, True, text_color)
        text_rect = text_surf.get_rect(center=rect.center)
        surface.blit(text_surf, text_rect)
        
        return rect

    @staticmethod
    def draw_floor_card(surface, rect, floor_data, colors, selected=False):
        """Рисует красивую карточку этажа"""
        # Градиентный фон
        if floor_data['owned']:
            start_color = (100, 200, 100)
            end_color = (70, 160, 70)
        else:
            start_color = (200, 200, 200)
            end_color = (160, 160, 160)
            
        VisualEffects.draw_gradient_rect(surface, rect, start_color, end_color)
        
        # Выделение выбранного этажа
        if selected:
            pygame.draw.rect(surface, (255, 215, 0), rect, 3, border_radius=6)
        
        # Внутренняя рамка
        inner_rect = rect.inflate(-6, -6)
        pygame.draw.rect(surface, (255, 255, 255, 30), inner_rect, 1, border_radius=4)
        
        return rect
    

class ParticleSystem:
    """Система частиц для визуальных эффектов"""
    def __init__(self):
        self.particles = []
    
    def add_money_particles(self, pos, amount):
        """Добавляет частицы денег"""
        for i in range(10):
            self.particles.append({
                'pos': [pos[0], pos[1]],
                'velocity': [pygame.time.get_ticks() % 5 - 2.5, -2 - (pygame.time.get_ticks() % 3)],
                'color': (255, 215, 0),
                'size': 3 + (pygame.time.get_ticks() % 4),
                'life': 60 + (pygame.time.get_ticks() % 40)
            })
    
    def update(self):
        """Обновляет частицы"""
        for particle in self.particles[:]:
            particle['pos'][0] += particle['velocity'][0]
            particle['pos'][1] += particle['velocity'][1]
            particle['life'] -= 1
            particle['velocity'][1] += 0.1  # гравитация
            
            if particle['life'] <= 0:
                self.particles.remove(particle)
    
    def draw(self, surface):
        """Рисует частицы"""
        for particle in self.particles:
            alpha = min(255, particle['life'] * 4)
            color = (*particle['color'], alpha)
            pos = (int(particle['pos'][0]), int(particle['pos'][1]))
            pygame.draw.circle(surface, color, pos, particle['size'])


class GameWindow:
    def __init__(self, game):
        self.game = game
        self.config = game.config
        self.screen = pygame.display.set_mode((self.config.SCREEN_WIDTH, self.config.SCREEN_HEIGHT))
        pygame.display.set_caption("🏢 Небоскрёб Мечты")
        
        # Менеджер UI для централизованной обработки событий
        self.ui_manager = UIManager()

        # Шрифты
        try:
            self.title_font = pygame.font.Font('assets/fonts/title.ttf', 36)
            self.font = pygame.font.Font('assets/fonts/main.ttf', 22)
            self.small_font = pygame.font.Font('assets/fonts/main.ttf', 16)
        except:
            # Fallback на системные шрифты
            self.title_font = pygame.font.SysFont('Arial', 36, bold=True)
            self.font = pygame.font.SysFont('Arial', 22)
            self.small_font = pygame.font.SysFont('Arial', 16)

        # Визуальные эффекты
        self.particles = ParticleSystem()
        self.visual_effects = VisualEffects()

        # Анимации
        self.pulse_value = 0
        self.pulse_direction = 1

        # Настройки скролла
        self.scroll_offset = 0
        self.max_visible_floors = 20
        self.floor_height = 30
        self.scroll_sensitivity = 15
        
        # Премиум цветовая схема
        self.colors = {
            'background': (240, 245, 255),  # Нежно-голубой
            'panel': (255, 255, 255),       # Белый
            'panel_secondary': (245, 248, 255),  # Светло-голубой
            'text': (50, 50, 80),           # Темно-синий
            'text_secondary': (100, 100, 130),   # Серо-синий
            'text_disabled': (180, 180, 200),    # Серый
            'accent': (70, 130, 180),       # Стальной синий
            'success': (65, 185, 130),      # Изумрудный
            'error': (220, 90, 90),         # Коралловый
            'warning': (255, 185, 70),      # Золотой
            'button': (80, 150, 220),       # Ярко-синий
            'button_hover': (100, 170, 240), # Светло-синий
            'button_disabled': (200, 210, 220),
            'owned_floor': (120, 200, 120), # Зеленый
            'not_owned_floor': (200, 210, 220), # Серый
            'selected_floor': (255, 215, 0), # Золотой
            'manager_indicator': (180, 120, 220), # Фиолетовый
            'income_highlight': (255, 240, 150)  # Светло-желтый
        }
        
        # Размеры элементов
        self.building_width = 300
        self.info_panel_width = 400
        
        # Состояние UI
        self.message_queue = []
        self.current_message = None
        self.message_timer = 0
        self.last_click_time = 0
        self.clock = pygame.time.Clock()
        
        # Кэш для оптимизации
        self.text_cache = {}

        # Фоновые текстуры
        self.background_pattern = self.create_background_pattern()
        
        # Добавляем панель улучшений
        upgrades_panel_height = 280
        self.upgrades_panel = UpgradesPanel(
            game, 
            self.building_width + 15,
            self.config.SCREEN_HEIGHT - upgrades_panel_height - 15,
            self.info_panel_width - 30,
            upgrades_panel_height
        )

        # Инициализация UI компонентов
        self.setup_ui_components()

    def setup_ui_components(self):
        """Инициализация UI компонентов"""
        # Кнопка сохранения
        save_button = Button(
            pygame.Rect(self.config.SCREEN_WIDTH - 130, 25, 110, 40),
            "💾 Сохранить",
            self.save_game_action,
            self.small_font,
            {
                'normal': self.colors['button'],
                'hover': self.colors['button_hover'], 
                'pressed': self.colors['accent'],
                'text': (255, 255, 255)
            }
        )
        self.ui_manager.add_component(save_button)

    def create_background_pattern(self):
        """Создает фоновый узор"""
        pattern = pygame.Surface((100, 100), pygame.SRCALPHA)
        for i in range(0, 100, 20):
            for j in range(0, 100, 20):
                if (i + j) % 40 == 0:
                    pygame.draw.rect(pattern, (230, 235, 255, 30), (i, j, 15, 15))
        return pattern
        
    def show_message(self, text, color=None, duration=180, effect=None):
        """Показать красивое сообщение"""
        if not text:
            text = "Произошла ошибка"  # Защита от пустых сообщений
            
        message_data = {
            'text': text,
            'color': color or self.colors['text'],
            'duration': duration,
            'timer': duration,
            'effect': effect,
            'y_offset': -50  # Для анимации появления
        }
        
        self.message_queue.append(message_data)
        
        # Если нет текущего сообщения, сразу показать
        if not self.current_message:
            self.next_message()
    
    def next_message(self):
        """Перейти к следующему сообщению в очереди"""
        if self.message_queue:
            self.current_message = self.message_queue.pop(0)
            self.message_timer = self.current_message['duration']
        else:
            self.current_message = None
    
    def get_text_surface(self, text, font, color):
        """Кэширование поверхностей текста для оптимизации"""
        key = f"{text}_{font}_{color}"
        if key not in self.text_cache:
            self.text_cache[key] = font.render(text, True, color)
        return self.text_cache[key]
    
    def handle_events(self):
        """Обработка событий через UI менеджер"""
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                self.game.save_on_exit()
                return False
                
            # Обрабатываем события через UI менеджер
            if self.ui_manager.handle_event(event):
                continue  # Событие обработано UI
                
            # Обработка специальных событий (скролл, выбор этажа)
            if event.type == pygame.MOUSEBUTTONDOWN:
                if event.button in [4, 5]:  # Скролл колесом
                    self.handle_scroll(event.button)
                else:
                    self.handle_special_click(event.pos)
                    
        return True
    
    def handle_special_click(self, pos):
        """Обработка кликов не связанных с UI компонентами"""
        x, y = pos
        
        # Клик по этажам в здании
        if x < self.building_width:
            self.handle_building_click(x, y)
        # Клик по информационной панели
        elif x > self.building_width and x < self.building_width + self.info_panel_width:
            self.handle_info_panel_click(x, y)
        # Клик по панели улучшений
        elif self.upgrades_panel.rect.collidepoint(pos):
            self.upgrades_panel.handle_click(pos)
    
    def handle_building_click(self, x, y):
        """Обработка кликов по зданию"""
        start_y = 150
        floor_height = 30
        
        if y >= start_y:
            start_index = self.scroll_offset // self.floor_height
            relative_y = y - start_y
            floor_index = start_index + (relative_y // floor_height)
            
            if 0 <= floor_index < len(self.game.building.floors):
                self.game.selected_floor = floor_index + 1
                
    def handle_scroll(self, button):
        """Обработка скролла"""
        if button == 4:  # Скролл вверх
            self.scroll_offset = max(0, self.scroll_offset - self.scroll_sensitivity)
        elif button == 5:  # Скролл вниз
            max_scroll = max(0, len(self.game.building.floors) - self.max_visible_floors) * self.floor_height
            self.scroll_offset = min(self.scroll_offset + self.scroll_sensitivity, max_scroll)

    def handle_info_panel_click(self, x, y):
        """Обработка кликов в информационной панели"""
        if not self.game.selected_floor:
            return
            
        floor = self.game.building.floors[self.game.selected_floor - 1]
        panel_x = self.building_width + 30
        current_y = 180
        
        # Создаем временные кнопки для обработки кликов
        buttons = []

        if not floor.owned:
            # Кнопка покупки этажа
            buy_button_rect = pygame.Rect(panel_x, current_y + 90, self.info_panel_width - 90, 70)
            buttons.append(("buy", buy_button_rect))
        else:
            # Кнопка сбора дохода
            if floor.income_collected > 0 and not self.has_auto_collect(floor):
                collect_button_rect = pygame.Rect(panel_x, current_y + 250, self.info_panel_width - 90, 40)
                buttons.append(("collect", collect_button_rect))
                current_y += 50
            
            # Кнопки улучшения ремонта
            repair_levels = list(self.config.FLOOR_CONFIG["repair_levels"].keys())
            if floor.repair_level in repair_levels:
                current_repair_index = repair_levels.index(floor.repair_level)
                if current_repair_index < len(repair_levels) - 1:
                    repair_button_rect = pygame.Rect(panel_x, current_y + 250, self.info_panel_width - 90, 40)
                    buttons.append(("repair", repair_button_rect))
                    current_y += 50
            
            # Кнопки менеджеров
            available_managers = self.game.get_available_managers(self.game.selected_floor)
            for manager_id, manager_data in available_managers:
                if manager_id != floor.manager:
                    manager_button_rect = pygame.Rect(panel_x, current_y + 250, self.info_panel_width - 90, 40)
                    buttons.append((f"manager_{manager_id}", manager_button_rect))
                    current_y += 50
        
        # Проверяем клик по кнопкам
        for button_type, button_rect in buttons:
            if button_rect.collidepoint((x, y)):
                self.handle_info_panel_action(button_type, floor)
                return True
        
        return False

    def handle_info_panel_action(self, action_type, floor):
        """Обработка действий информационной панели"""
        if action_type == "buy":
            cost = self.game.building.get_floor_cost(self.game.selected_floor)
            if self.game.buy_floor(self.game.selected_floor):
                self.show_message(f"Этаж {self.game.selected_floor} куплен!", self.colors['success'])
            else:
                self.show_message(f"Недостаточно денег! Нужно: {cost} руб.", self.colors['error'])
                
        elif action_type == "collect":
            self.game.collect_floor_income(self.game.selected_floor)
            
        elif action_type == "repair":
            repair_levels = list(self.config.FLOOR_CONFIG["repair_levels"].keys())
            current_repair_index = repair_levels.index(floor.repair_level)
            next_repair = repair_levels[current_repair_index + 1]
            repair_cost = floor.calculate_repair_cost(self.game.config, next_repair)
            
            if self.game.repair_floor(self.game.selected_floor, next_repair):
                self.show_message(f"Ремонт улучшен до {next_repair}!", self.colors['success'])
            else:
                self.show_message(f"Недостаточно денег для ремонта! Нужно: {repair_cost} руб.", self.colors['error'])
                
        elif action_type.startswith("manager_"):
            manager_id = action_type.split("_")[1]
            manager_data = self.config.MANAGER_CONFIG["managers"][manager_id]
            
            if self.game.hire_manager(self.game.selected_floor, manager_id):
                self.show_message(f"Нанят {manager_data['name']}!", self.colors['success'])
            else:
                self.show_message(f"Недостаточно денег! Нужно: {manager_data['cost']} руб.", self.colors['error'])

    def has_auto_collect(self, floor):
        """Проверяет, есть ли у этажа авто-сбор"""
        return (floor.manager and 
                self.config.MANAGER_CONFIG["managers"][floor.manager].get("auto_collect", False))

    def update(self):
        """Обновление анимаций и эффектов"""
        self.game.update()
        self.ui_manager.update()
        
        # Пульсация для анимаций
        self.pulse_value += 0.1 * self.pulse_direction
        if self.pulse_value >= 1.0:
            self.pulse_direction = -1
        elif self.pulse_value <= 0.0:
            self.pulse_direction = 1
        
        # Обновление частиц
        self.particles.update()
        
        # Обновление сообщений
        if self.current_message:
            self.message_timer -= 1
            if self.current_message['y_offset'] < 0:
                self.current_message['y_offset'] += 2
            
            if self.message_timer <= 0:
                self.next_message()
        
        self.clock.tick(60)

    def render(self):
        """Отрисовка всего интерфейса"""
        # Фон с узором
        for x in range(0, self.config.SCREEN_WIDTH, 100):
            for y in range(0, self.config.SCREEN_HEIGHT, 100):
                self.screen.blit(self.background_pattern, (x, y))
        
        # Градиентный верхний фон
        header_rect = pygame.Rect(0, 0, self.config.SCREEN_WIDTH, 200)
        self.visual_effects.draw_gradient_rect(
            self.screen, header_rect, 
            (220, 230, 255), (240, 245, 255)
        )
        
        # Отрисовка основных элементов
        self.render_building()
        self.render_info_panel()
        self.upgrades_panel.render(self.screen)
        self.render_top_panel()
        self.ui_manager.draw(self.screen)
        
        # Сообщения поверх всего
        if self.current_message:
            self.render_message()
        
        # Частицы поверх всего
        self.particles.draw(self.screen)
        
        pygame.display.flip()
    
    def render_building(self):
        """Отрисовка небоскрёба с премиум графикой"""
        # Фон здания с тенью
        building_bg = pygame.Rect(15, 85, self.building_width - 30, self.config.SCREEN_HEIGHT - 100)
        pygame.draw.rect(self.screen, (0, 0, 0, 30), 
                        building_bg.move(3, 3), 
                        border_radius=15)
        pygame.draw.rect(self.screen, self.colors['panel'], 
                        building_bg, border_radius=15)
        
        # Заголовок здания
        title_rect = pygame.Rect(25, 90, self.building_width - 50, 40)
        self.visual_effects.draw_glass_effect(self.screen, title_rect, self.colors['accent'], 180)
        title_text = self.font.render("🏢 Ваш Небоскрёб", True, (255, 255, 255))
        self.screen.blit(title_text, (title_rect.centerx - title_text.get_width()//2, 
                                    title_rect.centery - title_text.get_height()//2))
        
        # Область этажей
        floors_rect = pygame.Rect(25, 140, self.building_width - 50, self.config.SCREEN_HEIGHT - 160)
        pygame.draw.rect(self.screen, self.colors['panel_secondary'], 
                        floors_rect, border_radius=12)
        
        # Отрисовка видимых этажей
        start_index = self.scroll_offset // self.floor_height
        end_index = min(start_index + self.max_visible_floors, len(self.game.building.floors))
        
        for i in range(start_index, end_index):
            floor = self.game.building.floors[i]
            y_position = 150 + (i - start_index) * self.floor_height
            
            floor_rect = pygame.Rect(35, y_position, self.building_width - 70, 35)
            
            # Анимированная карточка этажа
            floor_data = {
                'owned': floor.owned,
                'selected': self.game.selected_floor == i + 1,
                'has_income': floor.income_collected > 0,
                'has_manager': floor.manager is not None
            }
            
            self.visual_effects.draw_floor_card(self.screen, floor_rect, floor_data, self.colors)
            
            # Иконки и текст этажа
            self.render_floor_content(floor_rect, floor, i + 1)
        
        # Полоса прокрутки
        self.render_scrollbar()

    def render_floor_content(self, rect, floor, floor_number):
        """Отрисовка содержимого карточки этажа"""
        # Номер этажа
        number_text = self.small_font.render(f"{floor_number}", True, self.colors['text'])
        self.screen.blit(number_text, (rect.x + 10, rect.centery - number_text.get_height()//2))
        
        if floor.owned:
            # Тип этажа с иконкой
            type_icons = {
                "office": "💼",
                "commercial": "🛍️", 
                "residential": "🏠",
                "premium": "⭐"
            }
            icon = type_icons.get(floor.floor_type, "🏢")
            type_text = self.small_font.render(f"{icon} {floor.floor_type}", True, self.colors['text_secondary'])
            self.screen.blit(type_text, (rect.x + 40, rect.centery - type_text.get_height()//2))
            
            # Менеджер
            if floor.manager:
                manager_text = self.small_font.render("👨‍💼", True, self.colors['manager_indicator'])
                self.screen.blit(manager_text, (rect.right - 50, rect.centery - manager_text.get_height()//2))
            
            # Накопленный доход с анимацией
            if floor.income_collected > 0:
                income_alpha = int(150 + 105 * math.sin(pygame.time.get_ticks() * 0.01))
                income_text = self.small_font.render(f"+{floor.income_collected}", True, self.colors['success'])
                income_text.set_alpha(income_alpha)
                self.screen.blit(income_text, (rect.right - 100, rect.centery - income_text.get_height()//2))
        else:
            # Стоимость этажа
            cost = self.game.building.get_floor_cost(floor_number)
            cost_text = self.small_font.render(f"{cost} руб.", True, self.colors['text_secondary'])
            self.screen.blit(cost_text, (rect.centerx - cost_text.get_width()//2, 
                                       rect.centery - cost_text.get_height()//2))

    def render_scrollbar(self):
        """Отрисовка полосы прокрутки"""
        if len(self.game.building.floors) <= self.max_visible_floors:
            return

        scrollbar_width = 12
        scrollbar_x = self.building_width - scrollbar_width - 20
        
        total_height = len(self.game.building.floors) * self.floor_height
        visible_ratio = (self.config.SCREEN_HEIGHT - 160) / total_height
        scrollbar_height = max(50, (self.config.SCREEN_HEIGHT - 160) * visible_ratio)
        
        scroll_ratio = self.scroll_offset / (total_height - (self.config.SCREEN_HEIGHT - 160))
        scrollbar_y = 150 + scroll_ratio * ((self.config.SCREEN_HEIGHT - 160) - scrollbar_height)
        
        # Фон скроллбара
        scrollbar_bg = pygame.Rect(scrollbar_x, 150, scrollbar_width, self.config.SCREEN_HEIGHT - 160)
        pygame.draw.rect(self.screen, (200, 210, 220), scrollbar_bg, border_radius=6)
        
        # Бегунок с градиентом
        scrollbar_thumb = pygame.Rect(scrollbar_x, scrollbar_y, scrollbar_width, scrollbar_height)
        self.visual_effects.draw_gradient_rect(
            self.screen, scrollbar_thumb,
            self.colors['accent'], (100, 150, 200)
        )
    
    def render_info_panel(self):
        """Отрисовка информационной панели с премиум дизайном"""
        # Основная панель с тенью
        panel_bg = pygame.Rect(self.building_width + 15, 85, self.info_panel_width - 30, self.config.SCREEN_HEIGHT - 100)
        pygame.draw.rect(self.screen, (0, 0, 0, 30), 
                        panel_bg.move(3, 3), 
                        border_radius=15)
        pygame.draw.rect(self.screen, self.colors['panel'], 
                        panel_bg, border_radius=15)
        
        if self.game.selected_floor:
            self.render_floor_info_details()
        else:
            # Красивое сообщение о выборе этажа
            text = self.font.render("Выберите этаж для просмотра", True, self.colors['text_secondary'])
            self.screen.blit(text, (panel_bg.centerx - text.get_width()//2, 
                                  panel_bg.centery - text.get_height()//2))
            
            # Анимированная стрелка
            arrow_y = panel_bg.centery + 30 + math.sin(pygame.time.get_ticks() * 0.005) * 10
            arrow_text = self.font.render("↓", True, self.colors['accent'])
            self.screen.blit(arrow_text, (panel_bg.centerx - arrow_text.get_width()//2, arrow_y))

    def render_floor_info_details(self):
        """Детальная информация о выбранном этаже"""
        if self.game.selected_floor > len(self.game.building.floors):
            return
            
        floor = self.game.building.floors[self.game.selected_floor - 1]
        panel_x = self.building_width + 30
        current_y = 110
        
        # Заголовок с градиентом
        title_rect = pygame.Rect(panel_x, current_y, self.info_panel_width - 60, 50)
        self.visual_effects.draw_gradient_rect(
            self.screen, title_rect, 
            self.colors['accent'], (60, 110, 160)
        )
        
        title_text = self.font.render(f"Этаж {self.game.selected_floor}", True, (255, 255, 255))
        self.screen.blit(title_text, (title_rect.centerx - title_text.get_width()//2, 
                                    title_rect.centery - title_text.get_height()//2))
        
        current_y += 70
        
        if floor.owned:
            self.render_owned_floor_info(floor, panel_x, current_y)
        else:
            self.render_unowned_floor_info(floor, panel_x, current_y)

    def render_owned_floor_info(self, floor, x, y):
        """Информация о купленном этаже"""
        current_y = y
        
        # Статистика в красивых карточках
        stats = [
            ("Тип", f"{floor.floor_type}"),
            ("Доход/день", f"{floor.calculate_income(self.game.config)} руб."),
            ("Накоплено", f"{floor.income_collected} руб."),
            ("Уровень ремонта", f"{floor.repair_level}"),
            ("Менеджер", f"{self.config.MANAGER_CONFIG['managers'][floor.manager]['name'] if floor.manager else 'Нет'}")
        ]
        
        for label, value in stats:
            stat_rect = pygame.Rect(x, current_y, self.info_panel_width - 90, 35)
            self.visual_effects.draw_glass_effect(self.screen, stat_rect, (240, 245, 255), 100)
            
            label_text = self.small_font.render(label, True, self.colors['text_secondary'])
            value_text = self.small_font.render(value, True, self.colors['text'])
            
            self.screen.blit(label_text, (stat_rect.x + 10, stat_rect.centery - label_text.get_height()//2))
            self.screen.blit(value_text, (stat_rect.right - value_text.get_width() - 10, 
                                        stat_rect.centery - value_text.get_height()//2))
            
            current_y += 45
        
        current_y += 20
        
        # Интерактивные кнопки
        self.render_floor_actions(floor, x, current_y)

    def render_unowned_floor_info(self, floor, x, y):
        """Информация о непокупном этаже"""
        cost = self.game.building.get_floor_cost(self.game.selected_floor)
        can_afford = self.game.money >= cost
        
        # Красивое отображение стоимости
        cost_rect = pygame.Rect(x, y, self.info_panel_width - 90, 80)
        self.visual_effects.draw_glass_effect(self.screen, cost_rect, (250, 250, 255), 150)
        
        cost_title = self.small_font.render("Стоимость покупки", True, self.colors['text_secondary'])
        cost_value = self.font.render(f"{cost} руб.", True, 
                                    self.colors['success'] if can_afford else self.colors['error'])
        
        self.screen.blit(cost_title, (cost_rect.centerx - cost_title.get_width()//2, cost_rect.y + 15))
        self.screen.blit(cost_value, (cost_rect.centerx - cost_value.get_width()//2, cost_rect.y + 40))
        
        # Кнопка покупки
        button_rect = pygame.Rect(x, y + 100, self.info_panel_width - 90, 50)
        mouse_pos = pygame.mouse.get_pos()
        hover = button_rect.collidepoint(mouse_pos) and can_afford
        
        self.visual_effects.draw_modern_button(
            self.screen, button_rect,
            "🏗️ Купить этаж",
            self.font, self.colors, hover, not can_afford
        )

    def render_floor_actions(self, floor, x, y):
        """Отрисовка действий для этажа"""
        current_y = y
        mouse_pos = pygame.mouse.get_pos()
        
        # Кнопка сбора дохода
        if floor.income_collected > 0 and (not floor.manager or not self.config.MANAGER_CONFIG["managers"][floor.manager].get("auto_collect", False)):
            button_rect = pygame.Rect(x, current_y, self.info_panel_width - 90, 40)
            hover = button_rect.collidepoint(mouse_pos)
            
            # Рисуем кнопку и сохраняем её координаты для обработки кликов
            self.visual_effects.draw_modern_button(
                self.screen, button_rect,
                f"💰 Собрать {floor.income_collected} руб.",
                self.small_font, self.colors, hover
            )
            current_y += 50
        
        # Кнопка улучшения ремонта
        repair_levels = list(self.config.FLOOR_CONFIG["repair_levels"].keys())
        if floor.repair_level in repair_levels:
            current_repair_index = repair_levels.index(floor.repair_level)
            
            if current_repair_index < len(repair_levels) - 1:
                next_repair = repair_levels[current_repair_index + 1]
                repair_cost = floor.calculate_repair_cost(self.game.config, next_repair)
                can_afford = self.game.money >= repair_cost
                
                button_rect = pygame.Rect(x, current_y, self.info_panel_width - 90, 40)
                hover = button_rect.collidepoint(mouse_pos) and can_afford
                
                self.visual_effects.draw_modern_button(
                    self.screen, button_rect,
                    f"🔧 Улучшить до {next_repair}",
                    self.small_font, self.colors, hover, not can_afford
                )
                
                # Стоимость под кнопкой
                cost_text = self.small_font.render(f"Стоимость: {repair_cost} руб.", True, 
                                                 self.colors['text_secondary'] if can_afford else self.colors['error'])
                self.screen.blit(cost_text, (x + 10, current_y + 45))
                current_y += 70
        
        # Кнопки менеджеров
        available_managers = self.game.get_available_managers(self.game.selected_floor)
        for manager_id, manager_data in available_managers:
            if manager_id != floor.manager:
                can_afford = self.game.money >= manager_data["cost"]
                button_rect = pygame.Rect(x, current_y, self.info_panel_width - 90, 40)
                hover = button_rect.collidepoint(mouse_pos) and can_afford
                
                button_text = f"👨‍💼 Нанять {manager_data['name']}"
                self.visual_effects.draw_modern_button(
                    self.screen, button_rect, button_text,
                    self.small_font, self.colors, hover, not can_afford
                )
                
                # Стоимость и бонусы под кнопкой
                cost_text = self.small_font.render(f"Стоимость: {manager_data['cost']} руб.", True, 
                                                 self.colors['text_secondary'] if can_afford else self.colors['error'])
                self.screen.blit(cost_text, (x + 10, current_y + 45))
                
                bonus_text = self.get_manager_bonus_text(manager_data)
                if bonus_text:
                    bonus_surface = self.small_font.render(bonus_text, True, self.colors['text_secondary'])
                    self.screen.blit(bonus_surface, (x + 10, current_y + 65))
                    current_y += 90
                else:
                    current_y += 70
        
        return current_y

    def get_manager_bonus_text(self, manager_data):
        """Возвращает текст бонуса менеджера"""
        bonuses = []
        if manager_data.get("income_bonus", 0) > 0:
            bonuses.append(f"+{manager_data['income_bonus']*100}% доход")
        if manager_data.get("repair_cost_reduction", 0) > 0:
            bonuses.append(f"-{manager_data['repair_cost_reduction']*100}% ремонт")
        if manager_data.get("maintenance_reduction", 0) > 0:
            bonuses.append(f"-{manager_data['maintenance_reduction']*100}% расходы")
        if manager_data.get("auto_collect", False):
            bonuses.append("авто-сбор")
        
        return " (" + ", ".join(bonuses) + ")" if bonuses else ""
    
    def render_top_panel(self):
        """Отрисовка верхней панели с общей информацией"""
        # Основная панель с тенью и градиентом
        panel_rect = pygame.Rect(15, 15, self.config.SCREEN_WIDTH - 30, 70)
        pygame.draw.rect(self.screen, (0, 0, 0, 30), 
                        panel_rect.move(2, 2), 
                        border_radius=20)
        
        self.visual_effects.draw_gradient_rect(
            self.screen, panel_rect,
            (80, 150, 220), (100, 170, 240)
        )
        
        # Основные показатели
        indicators = [
            (f"💰 {int(self.game.money)} руб.", 30),
            (f"📅 День: {self.game.day}", 200),
            (f"💵 Доход/день: {self.game.get_total_income_per_day()} руб.", 350),
            (f"💸 Расходы/день: {self.game.calculate_operational_costs()} руб.", 550),
            (f"🏢 Этажи: {len(self.game.building.get_owned_floors())}/{self.config.FLOOR_CONFIG['max_floors']}", 750)
        ]
        
        for text, x_pos in indicators:
            text_surf = self.small_font.render(text, True, (255, 255, 255))
            self.screen.blit(text_surf, (x_pos, 40))

    def render_message(self):
        """Отрисовка текущего сообщения"""
        if not self.current_message:
            return
            
        # Анимация появления/исчезновения
        alpha = min(255, self.current_message['timer'] * 4)
        y_offset = self.current_message['y_offset']
        
        # Фон сообщения
        message_bg = pygame.Rect(0, 0, self.config.SCREEN_WIDTH, 60)
        message_bg.y = 80 + y_offset
        
        self.visual_effects.draw_glass_effect(
            self.screen, message_bg, 
            self.current_message['color'], 
            alpha // 2
        )
        
        # Текст сообщения
        message_surf = self.font.render(
            self.current_message['text'], 
            True, 
            self.current_message['color']
        )
        message_surf.set_alpha(alpha)
        
        message_rect = message_surf.get_rect(center=(self.config.SCREEN_WIDTH // 2, 110 + y_offset))
        self.screen.blit(message_surf, message_rect)

    def save_game_action(self):
        """Действие кнопки сохранения"""
        success = self.game.save_system.save_game(self.game, "manual_save.json")
        if success:
            self.show_message("💾 Игра сохранена!", self.colors['success'])
        else:
            self.show_message("❌ Ошибка сохранения!", self.colors['error'])