from config import *

class Shop:
    def __init__(self, shop_type):
        self.shop_type = shop_type
        self.upgrade_level = 0
        self.income_multiplier = 1.0
        self.is_operational = False
        self.days_until_operational = shop_type.construction_days
        
    def get_effective_income(self):
        return self.shop_type.base_income * self.income_multiplier
    
    def update_construction(self):
        if not self.is_operational:
            self.days_until_operational -= 1
            if self.days_until_operational <= 0:
                self.is_operational = True
                return True
        return False