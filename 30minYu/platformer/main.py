# main.py
import pygame
import sys
from game import Game

def main():
    # Инициализация Pygame
    pygame.init()
    
    # Создание экземпляра игры
    game = Game()
    
    # Главный игровой цикл
    running = True
    while running:
        running = game.run()
    
    # Корректный выход
    pygame.quit()
    sys.exit()

if __name__ == "__main__":
    main()