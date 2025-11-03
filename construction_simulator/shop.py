from config import *

class Shop:
    def __init__(self, shop_id, name, base_cost, base_income):
        self.id = shop_id
        self.name = name
        self.base_cost = base_cost
        self.base_income = base_income
        self.upgrade_level = 0
        self.income_multiplier = 1.0
        self.is_operational = False
        self.days_until_operational = CONSTRUCTION_TIME
        
    @property
    def current_income(self):
        return self.base_income * self.income_multiplier
    
    @property
    def current_upgrade_cost(self):
        return self.base_cost * (UPGRADE_COST_MULTIPLIER ** self.upgrade_level)
    
    def buy_upgrade(self):
        if self.upgrade_level < MAX_UPGRADES:
            self.upgrade_level += 1
            self.income_multiplier *= UPGRADE_INCOME_MULTIPLIER
            return True
        return False
    
    def update_construction(self):
        if not self.is_operational:
            self.days_until_operational -= 1
            if self.days_until_operational <= 0:
                self.is_operational = True
                return True
        return False