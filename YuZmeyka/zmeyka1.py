import pygame
import random
import sys

# Инициализация Pygame
pygame.init()

# Константы
CELL_SIZE = 30
GRID_WIDTH = 20
GRID_HEIGHT = 20
SCREEN_WIDTH = CELL_SIZE * GRID_WIDTH
SCREEN_HEIGHT = CELL_SIZE * GRID_HEIGHT
FPS = 10  # 2 клетки в секунду при 5 FPS, но для плавности управления ставим 10
MAX_APPLES = (GRID_WIDTH * GRID_HEIGHT) // 2

# Цвета
BLACK = (0, 0, 0)
WHITE = (255, 255, 255)
RED = (255, 0, 0)
GREEN = (0, 255, 0)
DARK_GREEN = (0, 200, 0)
GRAY = (100, 100, 100)

class Snake:
    def __init__(self):
        self.reset()
        
    def reset(self):
        self.length = 3
        self.positions = [(GRID_WIDTH // 2, GRID_HEIGHT // 2)]
        self.direction = random.choice([(0, 1), (0, -1), (1, 0), (-1, 0)])
        self.score = 0
        self.grow_pending = 0
        
    def get_head_position(self):
        return self.positions[0]
    
    def update(self):
        head = self.get_head_position()
        x, y = self.direction
        new_x = (head[0] + x) % GRID_WIDTH
        new_y = (head[1] + y) % GRID_HEIGHT
        new_position = (new_x, new_y)
        
        # Проверка на столкновение с хвостом
        if new_position in self.positions[1:]:
            return False
        
        self.positions.insert(0, new_position)
        
        if self.grow_pending > 0:
            self.grow_pending -= 1
        else:
            self.positions.pop()
            
        return True
    
    def grow(self):
        self.grow_pending += 1
        self.length += 1
        self.score += 1
    
    def change_direction(self, direction):
        # Запрет противоположного направления
        if (direction[0] * -1, direction[1] * -1) != self.direction:
            self.direction = direction

class Game:
    def __init__(self):
        self.screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
        pygame.display.set_caption("Змейка")
        self.clock = pygame.time.Clock()
        self.font = pygame.font.SysFont('Arial', 25)
        self.big_font = pygame.font.SysFont('Arial', 50)
        self.snake = Snake()
        self.apple = self.generate_apple()
        self.game_over = False
        
    def generate_apple(self):
        positions = self.snake.positions
        apple = None
        while apple is None or apple in positions:
            apple = (random.randint(0, GRID_WIDTH - 1), 
                    random.randint(0, GRID_HEIGHT - 1))
        return apple
    
    def draw_grid(self):
        for x in range(0, SCREEN_WIDTH, CELL_SIZE):
            pygame.draw.line(self.screen, GRAY, (x, 0), (x, SCREEN_HEIGHT))
        for y in range(0, SCREEN_HEIGHT, CELL_SIZE):
            pygame.draw.line(self.screen, GRAY, (0, y), (SCREEN_WIDTH, y))
    
    def draw_border(self):
        pygame.draw.rect(self.screen, RED, (0, 0, SCREEN_WIDTH, SCREEN_HEIGHT), 2)
    
    def draw_snake(self):
        for i, p in enumerate(self.snake.positions):
            color = GREEN if i == 0 else DARK_GREEN
            rect = pygame.Rect((p[0] * CELL_SIZE, p[1] * CELL_SIZE), (CELL_SIZE, CELL_SIZE))
            pygame.draw.rect(self.screen, color, rect)
            pygame.draw.rect(self.screen, BLACK, rect, 1)
    
    def draw_apple(self):
        rect = pygame.Rect((self.apple[0] * CELL_SIZE, self.apple[1] * CELL_SIZE), 
                          (CELL_SIZE, CELL_SIZE))
        pygame.draw.rect(self.screen, RED, rect)
    
    def draw_score(self):
        score_text = self.font.render(f'Яблок: {self.snake.score}/{MAX_APPLES}', True, WHITE)
        self.screen.blit(score_text, (5, 5))
    
    def draw_game_over(self):
        overlay = pygame.Surface((SCREEN_WIDTH, SCREEN_HEIGHT))
        overlay.set_alpha(180)
        overlay.fill(BLACK)
        self.screen.blit(overlay, (0, 0))
        
        text = self.big_font.render('ВЫ МЕРТВЫ', True, RED)
        restart = self.font.render('Нажми R для перезапуска', True, WHITE)
        
        self.screen.blit(text, (SCREEN_WIDTH // 2 - text.get_width() // 2, 
                               SCREEN_HEIGHT // 2 - 50))
        self.screen.blit(restart, (SCREEN_WIDTH // 2 - restart.get_width() // 2, 
                                  SCREEN_HEIGHT // 2 + 20))
    
    def check_win(self):
        return self.snake.score >= MAX_APPLES
    
    def handle_events(self):
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()
            elif event.type == pygame.KEYDOWN:
                if self.game_over and event.key == pygame.K_r:
                    self.snake.reset()
                    self.apple = self.generate_apple()
                    self.game_over = False
                elif not self.game_over:
                    if event.key == pygame.K_UP:
                        self.snake.change_direction((0, -1))
                    elif event.key == pygame.K_DOWN:
                        self.snake.change_direction((0, 1))
                    elif event.key == pygame.K_LEFT:
                        self.snake.change_direction((-1, 0))
                    elif event.key == pygame.K_RIGHT:
                        self.snake.change_direction((1, 0))
    
    def update(self):
        if not self.game_over:
            if not self.snake.update():
                self.game_over = True
                return
            
            # Проверка съедания яблока
            if self.snake.get_head_position() == self.apple:
                self.snake.grow()
                if self.check_win():
                    self.game_over = True
                    return
                self.apple = self.generate_apple()
    
    def run(self):
        while True:
            self.handle_events()
            self.update()
            
            self.screen.fill(BLACK)
            self.draw_grid()
            self.draw_border()
            self.draw_snake()
            self.draw_apple()
            self.draw_score()
            
            if self.game_over:
                self.draw_game_over()
            
            pygame.display.flip()
            self.clock.tick(FPS)

if __name__ == "__main__":
    game = Game()
    game.run()