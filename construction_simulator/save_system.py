import json
import os

SAVE_FILE = "construction_simulator/game_save.json"

def save_game(game_state):
    data = {
        'balance': game_state.balance,
        'day': game_state.day,
        'shops': []
    }
    
    for shop in game_state.shops:
        shop_data = {
            'name': shop.name,
            'upgrade_level': shop.upgrade_level,
            'income_multiplier': shop.income_multiplier,
            'is_operational': shop.is_operational,
            'days_until_operational': shop.days_until_operational
        }
        data['shops'].append(shop_data)
    
    try:
        with open(SAVE_FILE, 'w') as f:
            json.dump(data, f, indent=2)
        return True
    except Exception as e:
        print(f"Ошибка сохранения: {e}")
        return False

def load_game():
    if not os.path.exists(SAVE_FILE):
        return None
    
    try:
        with open(SAVE_FILE, 'r') as f:
            data = json.load(f)
        return data
    except Exception as e:
        print(f"Ошибка загрузки: {e}")
        return None

def delete_save():
    if os.path.exists(SAVE_FILE):
        os.remove(SAVE_FILE)