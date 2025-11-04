import json
import os

class GameConfig:
    def __init__(self):
        # Основные настройки
        self.SCREEN_WIDTH = 1200
        self.SCREEN_HEIGHT = 800
        self.STARTING_MONEY = 10000
        self.DAY_DURATION = 5  # секунд на игровой день
        
        # Настройки отладки
        self.DEBUG_MODE = True
        self.DEBUG_LEVEL = 3  # 1-ERROR, 2-WARNING, 3-INFO, 4-DEBUG
        
        # Загрузка конфигураций из JSON
        self.FLOOR_CONFIG = self.load_json_config('config/floor_prices.json')
        self.MANAGER_CONFIG = self.load_json_config('config/manager_prices.json')
        self.UPGRADE_CONFIG = self.load_json_config('config/upgrade_costs.json')
        
        # Проверка загрузки конфигураций
        self.validate_configs()
    
    def load_json_config(self, filepath):
        """Загрузка конфигурации из JSON файла"""
        try:
            if os.path.exists(filepath):
                with open(filepath, 'r', encoding='utf-8') as f:
                    return json.load(f)
            else:
                print(f"⚠️ Файл конфигурации не найден: {filepath}")
                return {}
        except Exception as e:
            print(f"❌ Ошибка загрузки {filepath}: {e}")
            return {}
    
    def validate_configs(self):
        """Проверка корректности загруженных конфигураций"""
        required_configs = [
            ('FLOOR_CONFIG', ['base_floor_cost', 'floor_types']),
            ('MANAGER_CONFIG', ['managers']),
            ('UPGRADE_CONFIG', ['global_upgrades'])
        ]
        
        for config_name, required_fields in required_configs:
            config = getattr(self, config_name)
            if not config:
                print(f"❌ Конфигурация {config_name} не загружена")
                continue
                
            for field in required_fields:
                if field not in config:
                    print(f"⚠️ В {config_name} отсутствует поле: {field}")
    
    def log(self, message, level='INFO'):
        """Логирование с уровнями"""
        level_numbers = {'ERROR': 1, 'WARNING': 2, 'INFO': 3, 'DEBUG': 4}
        current_level = level_numbers.get(level, 3)
        
        if current_level <= self.DEBUG_LEVEL:
            print(f"[{level}] {message}")
    
    @property
    def dynamic_day_duration(self):
        """Динамическая длительность игрового дня"""
        base_duration = 5  # секунд
        # Увеличивать длительность дня с прогрессом (макс +50%)
        return base_duration * (1 + min(0.5, getattr(self, '_game_day', 1) / 200))
    
    def set_game_day(self, day):
        """Установить текущий игровой день для динамических расчетов"""
        self._game_day = day