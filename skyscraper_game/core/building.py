class Floor:
    def __init__(self, floor_number, floor_type="office"):
        self.floor_number = floor_number
        self.floor_type = floor_type
        self.owned = False
        self.manager = None
        self.repair_level = "basic"
        self.income_collected = 0  # Теперь здесь хранится ЧИСТЫЙ доход (после вычета расходов)
        
    def calculate_income(self, config):
        """Рассчитываем ВАЛОВЫЙ доход для этажа (без учета расходов)"""
        if not self.owned:
            return 0
            
        floor_config = config.FLOOR_CONFIG["floor_types"][self.floor_type]
        repair_config = config.FLOOR_CONFIG["repair_levels"][self.repair_level]
        
        base_income = floor_config["base_income"]
        income_multiplier = repair_config["income_multiplier"]
        
        # Бонус от менеджера
        manager_bonus = 1.0
        if self.manager:
            manager_config = config.MANAGER_CONFIG["managers"][self.manager]
            manager_bonus += manager_config.get("income_bonus", 0)
        
        # Бонус от высоты этажа (если есть улучшения лифтов)
        height_bonus = 1.0
        if hasattr(config, '_game') and config._game.elevator_system_level > 0:
            if self.floor_number > 10:
                height_bonus += min(0.5, (self.floor_number - 10) * 0.02 * config._game.elevator_system_level)
            
        return base_income * income_multiplier * manager_bonus * height_bonus

    def calculate_maintenance_cost(self, config):
        """Рассчитываем операционные расходы этажа"""
        if not self.owned:
            return 0
            
        floor_config = config.FLOOR_CONFIG["floor_types"][self.floor_type]
        base_cost = floor_config["maintenance_cost"]
        
        # Скидка от менеджера
        manager_discount = 1.0
        if self.manager:
            manager_config = config.MANAGER_CONFIG["managers"][self.manager]
            manager_discount -= manager_config.get("maintenance_reduction", 0)
        
        # Учет уровня ремонта (люкс ремонт дороже в обслуживании)
        repair_multiplier = 1.0
        if self.repair_level == "quality":
            repair_multiplier = 1.2
        elif self.repair_level == "luxury":
            repair_multiplier = 1.5
        
        return base_cost * manager_discount * repair_multiplier

    def calculate_repair_cost(self, config, target_repair_level=None):
        """Рассчитываем стоимость ремонта"""
        floor_config = config.FLOOR_CONFIG["floor_types"][self.floor_type]
        
        repair_level = target_repair_level if target_repair_level else self.repair_level
        repair_config = config.FLOOR_CONFIG["repair_levels"][repair_level]
        
        base_repair_cost = config.FLOOR_CONFIG["base_floor_cost"] * 0.5
        type_multiplier = floor_config["repair_cost_multiplier"]
        repair_multiplier = repair_config["cost_multiplier"]
        
        # Скидка от менеджера-ремонтника
        manager_discount = 1.0
        if self.manager:
            manager_config = config.MANAGER_CONFIG["managers"][self.manager]
            manager_discount -= manager_config.get("repair_cost_reduction", 0)
        
        cost = base_repair_cost * type_multiplier * repair_multiplier * manager_discount
        
        return int(cost)
    
    def can_afford_repair(self, money, config, target_repair_level=None):
        """Проверяем, хватает ли денег на ремонт"""
        cost = self.calculate_repair_cost(config, target_repair_level)
        return money >= cost
    
    
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
        self.floors[0].owned = True
        self.floors[0].repair_level = "basic"
    
    def get_floor_cost(self, floor_number):
        """Получаем стоимость этажа"""
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
    
    def get_available_floor_types(self, current_floor):
        """Получаем доступные типы этажей для текущего прогресса"""
        available_types = []
        for floor_type, config in self.config.FLOOR_CONFIG["floor_types"].items():
            if current_floor >= config["unlock_at_floor"]:
                available_types.append(floor_type)
        return available_types
    
    def get_total_income(self, config):
        """Общий валовый доход от всех этажей"""
        total = 0
        for floor in self.floors:
            if floor.owned:
                total += floor.calculate_income(config)
        return int(total)
    
    def get_total_maintenance_costs(self, config):
        """Общие операционные расходы"""
        total = 0
        for floor in self.floors:
            if floor.owned:
                total += floor.calculate_maintenance_cost(config)
        return int(total)
    
    def get_net_profit(self, config):
        """Чистая прибыль (валовый доход - расходы)"""
        return self.get_total_income(config) - self.get_total_maintenance_costs(config)
    
    def get_owned_floors(self):
        """Получаем список купленных этажей"""
        return [floor for floor in self.floors if floor.owned]