class Floor:
    def __init__(self, floor_number, floor_type="office"):
        self.floor_number = floor_number
        self.floor_type = floor_type
        self.owned = False
        self.manager = None
        self.repair_level = "basic"
        self.income_collected = 0  # ЧИСТЫЙ доход (доход за вычетом расходов)
        
    def calculate_income(self, config):
        """Рассчитываем ЧИСТЫЙ доход для этажа (доход минус расходы)"""
        if not self.owned:
            return 0
            
        # Проверка на существование типа этажа
        if self.floor_type not in config.FLOOR_CONFIG["floor_types"]:
            self.floor_type = "office"
            
        floor_config = config.FLOOR_CONFIG["floor_types"][self.floor_type]
        
        # Проверка на существование уровня ремонта
        if self.repair_level not in config.FLOOR_CONFIG["repair_levels"]:
            self.repair_level = "basic"
            
        repair_config = config.FLOOR_CONFIG["repair_levels"][self.repair_level]
        
        base_income = floor_config["base_income"]
        income_multiplier = repair_config["income_multiplier"]
        
        # Бонус от менеджера
        manager_bonus = 1.0
        if self.manager and self.manager in config.MANAGER_CONFIG["managers"]:
            manager_config = config.MANAGER_CONFIG["managers"][self.manager]
            manager_bonus += manager_config.get("income_bonus", 0)
        
        # Бонус от высоты этажа
        height_bonus = 1.0
        if hasattr(config, '_game') and hasattr(config._game, 'elevator_system_level') and config._game.elevator_system_level > 0:
            if self.floor_number > 10:
                height_bonus += min(0.5, (self.floor_number - 10) * 0.02 * config._game.elevator_system_level)
        
        # ВАЛОВОЙ доход
        gross_income = base_income * income_multiplier * manager_bonus * height_bonus
        
        # Операционные расходы
        maintenance_cost = self.calculate_maintenance_cost(config)
        
        # ЧИСТЫЙ доход (доход минус расходы)
        net_income = gross_income - maintenance_cost
        
        # Убеждаемся, что доход не отрицательный
        return max(0, int(net_income))

    def calculate_maintenance_cost(self, config):
        """Рассчитываем операционные расходы этажа"""
        if not self.owned:
            return 0
            
        if self.floor_type not in config.FLOOR_CONFIG["floor_types"]:
            return 0
            
        floor_config = config.FLOOR_CONFIG["floor_types"][self.floor_type]
        base_cost = floor_config["maintenance_cost"]
        
        # Скидка от менеджера
        manager_discount = 1.0
        if self.manager and self.manager in config.MANAGER_CONFIG["managers"]:
            manager_config = config.MANAGER_CONFIG["managers"][self.manager]
            manager_discount -= manager_config.get("maintenance_reduction", 0)
        
        # Учет уровня ремонта
        repair_multiplier = 1.0
        if self.repair_level == "quality":
            repair_multiplier = 1.2
        elif self.repair_level == "luxury":
            repair_multiplier = 1.5
        
        return int(base_cost * manager_discount * repair_multiplier)

    def calculate_repair_cost(self, config, target_repair_level=None):
        """Рассчитываем стоимость ремонта"""
        if self.floor_type not in config.FLOOR_CONFIG["floor_types"]:
            return 0
            
        floor_config = config.FLOOR_CONFIG["floor_types"][self.floor_type]
        
        repair_level = target_repair_level if target_repair_level else self.repair_level
        
        if repair_level not in config.FLOOR_CONFIG["repair_levels"]:
            return 0
            
        repair_config = config.FLOOR_CONFIG["repair_levels"][repair_level]
        
        base_repair_cost = config.FLOOR_CONFIG["base_floor_cost"] * 0.5
        type_multiplier = floor_config["repair_cost_multiplier"]
        repair_multiplier = repair_config["cost_multiplier"]
        
        # Скидка от менеджера-ремонтника
        manager_discount = 1.0
        if self.manager and self.manager in config.MANAGER_CONFIG["managers"]:
            manager_config = config.MANAGER_CONFIG["managers"][self.manager]
            manager_discount -= manager_config.get("repair_cost_reduction", 0)
        
        cost = base_repair_cost * type_multiplier * repair_multiplier * manager_discount
        
        return int(cost)
    
    
class Building:
    def __init__(self, config):
        self.config = config
        self.floors = []
        self.initialize_floors()
        
    def initialize_floors(self):
        """Создаём все этажи здания"""
        max_floors = self.config.FLOOR_CONFIG["max_floors"]
        for i in range(max_floors):
            self.floors.append(Floor(i + 1))
        
        # Первый этаж покупается автоматически
        if self.floors:
            self.floors[0].owned = True
            self.floors[0].repair_level = "basic"
    
    def get_floor_cost(self, floor_number):
        """Получаем стоимость этажа"""
        if floor_number < 1 or floor_number > len(self.floors):
            return 0
            
        base_cost = self.config.FLOOR_CONFIG["base_floor_cost"]
        increase_rate = self.config.FLOOR_CONFIG["cost_increase_per_floor"]
        
        # Нелинейный рост после определенных этапов
        milestone_multiplier = 1.0
        if floor_number > 50:
            milestone_multiplier = 1.3
        elif floor_number > 25:
            milestone_multiplier = 1.15
        elif floor_number > 10:
            milestone_multiplier = 1.05
            
        return int(base_cost * (increase_rate ** (floor_number - 1)) * milestone_multiplier)
    
    def get_owned_floors(self):
        """Получаем список купленных этажей"""
        return [floor for floor in self.floors if floor.owned]