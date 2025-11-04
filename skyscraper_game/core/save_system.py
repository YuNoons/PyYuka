import json, os, time
from datetime import datetime

class SaveSystem:
    def __init__(self, save_dir="data/saves"):
        self.save_dir = save_dir
        os.makedirs(save_dir, exist_ok=True)
    
    def save_game(self, game, filename=None):
        """Сохраняет игру в файл"""
        if filename is None:
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            filename = f"save_{timestamp}.json"
        
        save_path = os.path.join(self.save_dir, filename)
        
        save_data = {
            "metadata": {
                "version": "1.1",
                "save_date": datetime.now().isoformat(),
                "game_days": game.day,
                "play_time": game.stats.get_play_time()
            },
            "player": {
                "money": game.money,
                "day": game.day
            },
            "statistics": {
                "total_earned": game.stats.total_earned,
                "total_spent": game.stats.total_spent,
                "floors_purchased": game.stats.floors_purchased,
                "managers_hired": game.stats.managers_hired,
                "upgrades_bought": game.stats.upgrades_bought,
                "start_time": game.stats.start_time
            },
            "building": {
                "floors": []
            },
            "upgrades": {
                "elevator_system_level": getattr(game, 'elevator_system_level', 0),
                "facade_renovation_level": getattr(game, 'facade_renovation_level', 0),
                "infrastructure_level": getattr(game, 'infrastructure_level', 0)
            }
        }
        
        # Сохраняем данные по каждому этажу
        for floor in game.building.floors:
            floor_data = {
                "floor_number": floor.floor_number,
                "owned": floor.owned,
                "floor_type": floor.floor_type,
                "manager": floor.manager,
                "repair_level": floor.repair_level,
                "income_collected": floor.income_collected
            }
            save_data["building"]["floors"].append(floor_data)
        
        try:
            with open(save_path, 'w', encoding='utf-8') as f:
                json.dump(save_data, f, indent=2, ensure_ascii=False)
            print(f"💾 Игра сохранена: {filename}")
            return True
        except Exception as e:
            print(f"❌ Ошибка сохранения: {e}")
            return False
    
    def load_game(self, game, filename):
        """Загружает игру из файла"""
        save_path = os.path.join(self.save_dir, filename)
        
        try:
            with open(save_path, 'r', encoding='utf-8') as f:
                save_data = json.load(f)
            
            print(f"💾 Загрузка игры: {filename}")
            
            # Загружаем данные игрока
            game.money = save_data["player"]["money"]
            game.day = save_data["player"]["day"]
            
            # Загружаем статистику
            if "statistics" in save_data:
                stats = save_data["statistics"]
                game.stats.total_earned = stats.get("total_earned", 0)
                game.stats.total_spent = stats.get("total_spent", 0)
                game.stats.floors_purchased = stats.get("floors_purchased", 0)
                game.stats.managers_hired = stats.get("managers_hired", 0)
                game.stats.upgrades_bought = stats.get("upgrades_bought", 0)
                game.stats.start_time = stats.get("start_time", time.time())
            
            # Загружаем улучшения
            game.elevator_system_level = save_data["upgrades"].get("elevator_system_level", 0)
            game.facade_renovation_level = save_data["upgrades"].get("facade_renovation_level", 0)
            game.infrastructure_level = save_data["upgrades"].get("infrastructure_level", 0)
            
            # Загружаем этажи
            for floor_data in save_data["building"]["floors"]:
                floor_num = floor_data["floor_number"]
                if 1 <= floor_num <= len(game.building.floors):
                    floor = game.building.floors[floor_num - 1]
                    floor.owned = floor_data["owned"]
                    floor.floor_type = floor_data["floor_type"]
                    floor.manager = floor_data["manager"]
                    floor.repair_level = floor_data["repair_level"]
                    floor.income_collected = floor_data["income_collected"]
            
            print("✅ Игра успешно загружена")
            return True
        except Exception as e:
            print(f"❌ Ошибка загрузки: {e}")
            return False
    
    def auto_load(self, game):
        """Автоматическая загрузка последнего сохранения"""
        save_files = self.get_save_files()
        if save_files:
            if "autosave.json" in save_files:
                return self.load_game(game, "autosave.json")
            elif save_files:
                return self.load_game(game, save_files[-1])
        return False
    
    def get_save_files(self):
        """Возвращает список файлов сохранений"""
        try:
            files = [f for f in os.listdir(self.save_dir) if f.endswith('.json')]
            return sorted(files)
        except:
            return []
    
    def get_save_info(self, filename):
        """Получить информацию о сохранении"""
        save_path = os.path.join(self.save_dir, filename)
        try:
            with open(save_path, 'r', encoding='utf-8') as f:
                save_data = json.load(f)
            
            return {
                'filename': filename,
                'date': save_data['metadata']['save_date'],
                'day': save_data['player']['day'],
                'money': save_data['player']['money'],
                'floors_owned': len([f for f in save_data['building']['floors'] if f['owned']])
            }
        except:
            return None