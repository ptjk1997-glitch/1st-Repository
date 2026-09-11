import pygame
import random
import sys

# 게임 설정
WIDTH, HEIGHT = 600, 600
CELL_SIZE = 20
GRID_WIDTH = WIDTH // CELL_SIZE
GRID_HEIGHT = HEIGHT // CELL_SIZE
FPS = 10

# 색상 정의
BLACK = (0, 0, 0)
WHITE = (255, 255, 255)
GREEN = (0, 255, 0)
RED = (255, 0, 0)
DARK_GREEN = (0, 180, 0)
GRAY = (40, 40, 40)
BLUE = (0, 100, 255)


class SnakeGame:
    def __init__(self):
        pygame.init()
        pygame.display.set_caption("MySnake")
        self.screen = pygame.display.set_mode((WIDTH, HEIGHT))
        self.clock = pygame.time.Clock()
        self.font = pygame.font.SysFont("malgungothic", 24)
        self.small_font = pygame.font.SysFont("malgungothic", 18)

        self.reset_game()

    def reset_game(self):
        self.direction = (1, 0)
        self.next_direction = (1, 0)
        self.snake = [(GRID_WIDTH // 2, GRID_HEIGHT // 2),
                      (GRID_WIDTH // 2 - 1, GRID_HEIGHT // 2),
                      (GRID_WIDTH // 2 - 2, GRID_HEIGHT // 2)]
        self.food = self.spawn_food()
        self.score = 0
        self.game_over = False

    def spawn_food(self):
        while True:
            food = (random.randint(0, GRID_WIDTH - 1), random.randint(0, GRID_HEIGHT - 1))
            if food not in self.snake:
                return food

    def handle_events(self):
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                return False
            if event.type == pygame.KEYDOWN:
                if event.key in (pygame.K_UP, pygame.K_w):
                    self.next_direction = (0, -1)
                elif event.key in (pygame.K_DOWN, pygame.K_s):
                    self.next_direction = (0, 1)
                elif event.key in (pygame.K_LEFT, pygame.K_a):
                    self.next_direction = (-1, 0)
                elif event.key in (pygame.K_RIGHT, pygame.K_d):
                    self.next_direction = (1, 0)
                elif event.key == pygame.K_r and self.game_over:
                    self.reset_game()

        # 반대 방향으로 즉시 뒤집히는 입력은 무시
        if (self.next_direction[0] * -1, self.next_direction[1] * -1) != self.direction:
            self.direction = self.next_direction

        return True

    def update(self):
        if self.game_over:
            return

        head_x, head_y = self.snake[0]
        dx, dy = self.direction
        new_head = (head_x + dx, head_y + dy)

        # 벽 충돌 체크
        if new_head[0] < 0 or new_head[0] >= GRID_WIDTH or new_head[1] < 0 or new_head[1] >= GRID_HEIGHT:
            self.game_over = True
            return

        # 자기 몸에 충돌
        if new_head in self.snake:
            self.game_over = True
            return

        self.snake.insert(0, new_head)

        # 음식 먹기
        if new_head == self.food:
            self.score += 1
            self.food = self.spawn_food()
        else:
            self.snake.pop()

    def draw(self):
        self.screen.fill(BLACK)
        self.draw_grid()
        self.draw_food()
        self.draw_snake()
        self.draw_score()

        if self.game_over:
            self.draw_game_over()

        pygame.display.flip()

    def draw_grid(self):
        for x in range(0, WIDTH, CELL_SIZE):
            pygame.draw.line(self.screen, GRAY, (x, 0), (x, HEIGHT))
        for y in range(0, HEIGHT, CELL_SIZE):
            pygame.draw.line(self.screen, GRAY, (0, y), (WIDTH, y))

    def draw_snake(self):
        for index, segment in enumerate(self.snake):
            x, y = segment[0] * CELL_SIZE, segment[1] * CELL_SIZE
            color = DARK_GREEN if index == 0 else GREEN
            pygame.draw.rect(self.screen, color, (x + 1, y + 1, CELL_SIZE - 2, CELL_SIZE - 2))

    def draw_food(self):
        x, y = self.food[0] * CELL_SIZE, self.food[1] * CELL_SIZE
        pygame.draw.rect(self.screen, RED, (x + 2, y + 2, CELL_SIZE - 4, CELL_SIZE - 4))

    def draw_score(self):
        score_text = self.font.render(f"점수: {self.score}", True, WHITE)
        self.screen.blit(score_text, (10, 10))

    def draw_game_over(self):
        overlay = pygame.Surface((WIDTH, HEIGHT), pygame.SRCALPHA)
        overlay.fill((0, 0, 0, 150))
        self.screen.blit(overlay, (0, 0))

        text = self.font.render("게임 오버", True, WHITE)
        sub_text = self.small_font.render("다시 시작: R", True, WHITE)

        text_rect = text.get_rect(center=(WIDTH // 2, HEIGHT // 2 - 20))
        sub_rect = sub_text.get_rect(center=(WIDTH // 2, HEIGHT // 2 + 20))

        self.screen.blit(text, text_rect)
        self.screen.blit(sub_text, sub_rect)

    def run(self):
        running = True
        while running:
            running = self.handle_events()
            self.update()
            self.draw()
            self.clock.tick(FPS)

        pygame.quit()
        sys.exit()


if __name__ == "__main__":
    game = SnakeGame()
    game.run()
