import pygame
import time
from .building import Building
from .save_system import SaveSystem

class GameStatistics:
    """Класс для отслеживания статистики игры"""
    def __init__(self):
        self.total_earned = 0
        self.total_spent = 0
        self.floors_purchased = 0
        self.managers_hired = 0
        self.upgrades_bought = 0
        self.start_time = time.time()
        self.last_save_time = time.time()
    
    def get_play_time(self):
        """Возвращает время игры в секундах"""
        return time.time() - self.start_time
    
    def get_play_time_formatted(self):
        """Возвращает отформатированное время игры"""
        total_seconds = int(self.get_play_time())
        hours = total_seconds // 3600
        minutes = (total_seconds % 3600) // 60
        seconds = total_seconds % 60
        return f"{hours:02d}:{minutes:02d}:{seconds:02d}"
    
    def add_income(self, amount):
        """Добавляет доход к общей статистике"""
        self.total_earned += amount
    
    def add_expense(self, amount):
        """Добавляет расход к общей статистике"""
        self.total_spent += amount

class Game:
    def __init__(self):
        from config.game_config import GameConfig
        self.config = GameConfig()
        self.building = Building(self.config)
        self.save_system = SaveSystem()
        
        # Игровая экономика
        self.money = self.config.STARTING_MONEY
        self.day = 1
        self.last_day_time = time.time()
        self.selected_floor = None
        self.game_speed = 1.0
        
        # Статистика
        self.stats = GameStatistics()
        
        # Глобальные улучшения
        self.elevator_system_level = 0  
        self.facade_renovation_level = 0  
        self.infrastructure_level = 0
        
        # Система событий
        self.random_events = RandomEvents(self)
        
    def update(self):
        """Обновление игрового состояния"""
        current_time = time.time()
        
        # Обновление дней
        if current_time - self.last_day_time >= self.config.DAY_DURATION / self.game_speed:
            self.day += 1
            self.last_day_time = current_time
            self.collect_income()
            
            # Случайные события
            self.random_events.trigger_random_event()
            
            # Авто-сохранение каждые 5 минут
            if current_time - self.stats.last_save_time >= 300:
                self.save_system.save_game(self, "autosave.json")
                self.stats.last_save_time = current_time

    def save_on_exit(self):
        """Сохранение при выходе из игры"""
        success = self.save_system.save_game(self, "autosave.json")
        if success:
            print("💾 Игра сохранена при выходе")
        else:
            print("❌ Ошибка сохранения при выходе")
        return success

    def calculate_operational_costs(self):
        """Расчет операционных расходов"""
        total_costs = 0
        for floor in self.building.floors:
            if floor.owned:
                cost = floor.calculate_maintenance_cost(self.config)
                total_costs += cost
        return int(total_costs)

    def buy_global_upgrade(self, upgrade_type):
        """Покупка глобального улучшения"""
        if not hasattr(self.config, 'UPGRADE_CONFIG') or not self.config.UPGRADE_CONFIG:
            return False
            
        upgrade_config = self.config.UPGRADE_CONFIG["global_upgrades"].get(upgrade_type)
        if not upgrade_config:
            return False
        
        current_level = getattr(self, f"{upgrade_type}_level", 0)
        
        if current_level >= len(upgrade_config["levels"]):
            return False
        
        next_level_cost = upgrade_config["levels"][current_level]["cost"]
        
        if self.money >= next_level_cost:
            self.money -= next_level_cost
            self.stats.add_expense(next_level_cost)
            self.stats.upgrades_bought += 1
            setattr(self, f"{upgrade_type}_level", current_level + 1)
            
            # Показываем сообщение об успехе
            if hasattr(self, 'window'):
                self.window.show_message(
                    f"🚀 Улучшение '{upgrade_config.get('name', upgrade_type)}' повышено до уровня {current_level + 1}!",
                    self.window.colors['success']
                )
            return True
        else:
            # Показываем сообщение об ошибке
            if hasattr(self, 'window'):
                self.window.show_message(
                    f"❌ Недостаточно денег для улучшения! Нужно: {next_level_cost} руб.",
                    self.window.colors['error']
                )
            return False
    
    def get_global_upgrade_info(self, upgrade_type):
        """Возвращает информацию о глобальном улучшении"""
        if not hasattr(self.config, 'UPGRADE_CONFIG') or not self.config.UPGRADE_CONFIG:
            return {"error": "Конфиг улучшений не загружен"}
            
        upgrade_config = self.config.UPGRADE_CONFIG["global_upgrades"].get(upgrade_type)
        if not upgrade_config:
            return {"error": f"Конфиг для {upgrade_type} не найден"}
            
        current_level = getattr(self, f"{upgrade_type}_level", 0)
        
        info = {
            "name": upgrade_type,
            "current_level": current_level,
            "max_level": len(upgrade_config["levels"]),
            "effects": []
        }
        
        if current_level > 0:
            current_effect = upgrade_config["levels"][current_level - 1]
            for key, value in current_effect.items():
                if key != "cost":
                    if key == "income_bonus":
                        info["effects"].append(f"Доход: +{value*100}%")
                    elif key == "attraction_bonus":
                        info["effects"].append(f"Привлекательность: +{value*100}%")
                    elif key == "maintenance_reduction":
                        info["effects"].append(f"Снижение расходов: {value*100}%")
        
        if current_level < info["max_level"]:
            next_level = upgrade_config["levels"][current_level]
            info["next_cost"] = next_level["cost"]
            info["next_effects"] = []
            for key, value in next_level.items():
                if key != "cost":
                    if key == "income_bonus":
                        info["next_effects"].append(f"Доход: +{value*100}%")
                    elif key == "attraction_bonus":
                        info["next_effects"].append(f"Привлекательность: +{value*100}%")
                    elif key == "maintenance_reduction":
                        info["next_effects"].append(f"Снижение расходов: {value*100}%")
        
        return info

    def collect_income(self):
        """Сбор дохода со всех этажей (доход уже за вычетом расходов)"""
        for floor in self.building.floors:
            if floor.owned:
                income = floor.calculate_income(self.config)
                # Авто-сбор если есть менеджер с авто-сбором
                if floor.manager and self.config.MANAGER_CONFIG["managers"][floor.manager].get("auto_collect", False):
                    self.money += income
                    self.stats.add_income(income)
                else:
                    floor.income_collected += income

    def collect_floor_income(self, floor_number):
        """Ручной сбор дохода с конкретного этажа"""
        if floor_number < 1 or floor_number > len(self.building.floors):
            return False
            
        floor = self.building.floors[floor_number - 1]
        if floor.owned and floor.income_collected > 0:
            collected_amount = floor.income_collected
            self.money += collected_amount
            self.stats.add_income(collected_amount)
            floor.income_collected = 0
            
            # Показываем сообщение о собранной сумме
            if hasattr(self, 'window'):
                self.window.show_message(f"💰 Собрано {collected_amount} руб.!", self.window.colors['success'])
            return True
        return False

    def buy_floor(self, floor_number, floor_type="office"):
        """Покупка этажа"""
        if 1 <= floor_number <= len(self.building.floors):
            floor = self.building.floors[floor_number - 1]

            if not floor.owned:
                cost = self.building.get_floor_cost(floor_number)
                cost = int(cost)
                money_int = int(self.money)

                if money_int >= cost:
                    self.money = money_int - cost
                    self.stats.add_expense(cost)
                    self.stats.floors_purchased += 1
                    floor.owned = True
                    floor.floor_type = floor_type
                    return True
                else:
                    # Показываем сообщение об ошибке
                    if hasattr(self, 'window'):
                        self.window.show_message(
                            f"❌ Недостаточно денег! Нужно: {cost} руб.",
                            self.window.colors['error']
                        )
        return False

    def hire_manager(self, floor_number, manager_type):
        """Найм менеджера на этаж"""
        if floor_number < 1 or floor_number > len(self.building.floors):
            return False
            
        floor = self.building.floors[floor_number - 1]
        if floor.owned:
            manager_config = self.config.MANAGER_CONFIG["managers"][manager_type]
            if self.money >= manager_config["cost"]:
                self.money -= manager_config["cost"]
                self.stats.add_expense(manager_config["cost"])
                self.stats.managers_hired += 1
                floor.manager = manager_type
                return True
        return False

    def repair_floor(self, floor_number, repair_level):
        """Ремонт этажа"""
        if floor_number < 1 or floor_number > len(self.building.floors):
            return False
            
        floor = self.building.floors[floor_number - 1]
        if floor.owned:
            cost = floor.calculate_repair_cost(self.config, repair_level)
            
            if self.money >= cost:
                self.money -= cost
                self.stats.add_expense(cost)
                floor.repair_level = repair_level
                return True
        return False
    
    def get_total_income_per_day(self):
        """Общий доход в день (уже за вычетом расходов)"""
        total = 0
        for floor in self.building.floors:
            if floor.owned:
                total += floor.calculate_income(self.config)
        return int(total)
    
    def get_available_managers(self, floor_number):
        """Получить доступных менеджеров для этажа"""
        if floor_number < 1 or floor_number > len(self.building.floors):
            return []
            
        available = []
        floor = self.building.floors[floor_number - 1]
        
        for manager_id, manager_data in self.config.MANAGER_CONFIG["managers"].items():
            if floor_number >= manager_data.get("unlock_at_floor", 1):
                available.append((manager_id, manager_data))
                
        return available

class RandomEvents:
    """Система случайных событий"""
    def __init__(self, game):
        self.game = game
        self.events = [
            {
                "name": "Экономический бум", 
                "effect": lambda: self.modify_income(0.2),
                "message": "📈 Экономический бум! Доход увеличен на 20% на сегодня!"
            },
            {
                "name": "Кризис", 
                "effect": lambda: self.modify_income(-0.15),
                "message": "📉 Экономический кризис! Доход уменьшен на 15% на сегодня!"
            }
        ]
        self.active_events = []
    
    def modify_income(self, multiplier):
        """Временное изменение дохода"""
        pass
    
    def trigger_random_event(self):
        """Активировать случайное событие"""
        if len(self.game.building.get_owned_floors()) < 3:
            return
            
        if pygame.time.get_ticks() % 100 < 2:  # 2% шанс каждый день
            event = pygame.time.get_ticks() % len(self.events)
            event_data = self.events[event]
            event_data["effect"]()
            
            if hasattr(self.game, 'window'):
                self.game.window.show_message(
                    event_data["message"], 
                    self.game.window.colors['warning']
                )