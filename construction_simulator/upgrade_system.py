from config import UPGRADE_BASE_COST, UPGRADE_COST_MULTIPLIER

class UpgradeSystem:
    def __init__(self):
        self.level = 0
        
    @property
    def current_cost(self):
        if self.level == 0:
            return UPGRADE_BASE_COST
        
        # Умный рост цены: сначала медленный, потом ускоряется
        growth_factor = UPGRADE_COST_MULTIPLIER + (0.01 * min(self.level // 5, 4))
        return UPGRADE_BASE_COST * (growth_factor ** self.level)
    
    @property
    def income_multiplier(self):
        base_multiplier = 1.12  # +12%
        
        # Увеличиваем эффективность на высоких уровнях
        if self.level > 10:
            base_multiplier = 1.14
        if self.level > 15:
            base_multiplier = 1.16
            
        return base_multiplier ** self.level
    
    @property
    def next_income_multiplier(self):
        next_level = self.level + 1
        base_multiplier = 1.12
        if next_level > 10: base_multiplier = 1.14
        if next_level > 15: base_multiplier = 1.16
        return base_multiplier ** next_level
    
    def buy_upgrade(self):
        self.level += 1
        return True