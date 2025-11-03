class ShopType:
    def __init__(self, id, name, cost, income, construction_days, requirement=None):
        self.id = id
        self.name = name
        self.cost = cost
        self.base_income = income
        self.construction_days = construction_days
        self.requirement = requirement
        
    @property
    def roi_seconds(self):
        """Время окупаемости в секундах"""
        return self.cost / self.base_income

# Создание типов магазинов из конфига
def create_shop_types(config):
    return {id: ShopType(id, **data) for id, data in config.items()}