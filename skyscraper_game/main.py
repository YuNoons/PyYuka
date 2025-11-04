import pygame
import sys
import os
import atexit

# Добавляем пути для импорта
sys.path.append('config')
sys.path.append('core')
sys.path.append('ui')

from config.game_config import GameConfig
from core.game import Game
from ui.main_window import GameWindow

def cleanup(game):
    """Функция очистки при выходе"""
    print("🔄 Завершение работы...")
    game.save_on_exit()
    
def setup_directories():
    """Создание необходимых директорий"""
    directories = ['data/saves', 'config', 'core', 'ui', 'assets/fonts', 'assets/images']
    for directory in directories:
        os.makedirs(directory, exist_ok=True)
    
def main():
    """Главная функция запуска игры"""
    game = None
    try:
        # Создание директорий
        setup_directories()
        
        # Инициализация Pygame
        pygame.init()
        
        # Создаем экземпляр игры и окно
        game = Game()
        game_window = GameWindow(game)
        game.window = game_window  # Ссылка на окно для доступа из игры
        
        # Пробуем загрузить авто-сохранение
        if game.save_system.auto_load(game):
            print("✅ Авто-загрузка выполнена")
            game_window.show_message("🎮 Игра загружена из авто-сохранения!", game_window.colors['success'])
        else:
            print("ℹ️  Авто-сохранение не найдено, начинаем новую игру")
            game_window.show_message("🚀 Новая игра начата! Удачи!", game_window.colors['success'])
        
        # Регистрируем функцию очистки при выходе
        atexit.register(cleanup, game)
        
        # Главный игровой цикл
        running = True
        while running:
            running = game_window.handle_events()
            game_window.update()
            game_window.render()
            
        # Корректный выход
        pygame.quit()
        sys.exit()
        
    except Exception as e:
        print(f"❌ Ошибка при запуске игры: {e}")
        import traceback
        traceback.print_exc()
        
        # Сохраняем при ошибке
        if game:
            game.save_on_exit()
        pygame.quit()
        sys.exit(1)

if __name__ == "__main__":
    main()