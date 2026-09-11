import random
import sys

import pygame


WIDTH = 600
HEIGHT = 600
GRID_SIZE = 20
GRID_COUNT = WIDTH // GRID_SIZE

BLACK = (10, 10, 18)
WHITE = (245, 245, 245)
GREEN = (76, 217, 100)
RED = (255, 76, 76)
BLUE = (96, 165, 250)
DARK = (25, 25, 35)

pygame.init()
pygame.display.set_caption("Demo Snake")
window = pygame.display.set_mode((WIDTH, HEIGHT))
clock = pygame.time.Clock()
font = pygame.font.SysFont("malgun gothic", 26)
small_font = pygame.font.SysFont("malgun gothic", 18)


def reset_game():
    snake = [
        [GRID_COUNT // 2, GRID_COUNT // 2],
        [GRID_COUNT // 2 - 1, GRID_COUNT // 2],
        [GRID_COUNT // 2 - 2, GRID_COUNT // 2],
    ]
    direction = (1, 0)
    next_direction = (1, 0)
    food = generate_food(snake)
    score = 0
    speed = 9
    game_over = False
    return snake, direction, next_direction, food, score, speed, game_over


def generate_food(snake):
    while True:
        x = random.randint(0, GRID_COUNT - 1)
        y = random.randint(0, GRID_COUNT - 1)
        if [x, y] not in snake:
            return [x, y]


def draw_grid():
    for x in range(0, WIDTH, GRID_SIZE):
        pygame.draw.line(window, (40, 40, 52), (x, 0), (x, HEIGHT))
    for y in range(0, HEIGHT, GRID_SIZE):
        pygame.draw.line(window, (40, 40, 52), (0, y), (WIDTH, y))


def draw_cell(x, y, color):
    rect = pygame.Rect(x * GRID_SIZE, y * GRID_SIZE, GRID_SIZE, GRID_SIZE)
    pygame.draw.rect(window, color, rect, border_radius=4)


def draw_snake(snake):
    for index, segment in enumerate(snake):
        color = GREEN if index == 0 else (92, 184, 92)
        draw_cell(segment[0], segment[1], color)


def draw_food(food):
    x, y = food
    draw_cell(x, y, RED)


def draw_score(score):
    text = font.render(f"점수: {score}", True, WHITE)
    window.blit(text, (18, 12))


def draw_game_over(score):
    overlay = pygame.Surface((WIDTH, HEIGHT), pygame.SRCALPHA)
    overlay.fill((0, 0, 0, 150))
    window.blit(overlay, (0, 0))

    title = font.render("게임 오버", True, WHITE)
    subtitle = small_font.render(f"최종 점수: {score}", True, WHITE)
    restart = small_font.render("R 키로 다시 시작 / ESC로 종료", True, BLUE)

    window.blit(title, (WIDTH // 2 - title.get_width() // 2, HEIGHT // 2 - 40))
    window.blit(subtitle, (WIDTH // 2 - subtitle.get_width() // 2, HEIGHT // 2 + 10))
    window.blit(restart, (WIDTH // 2 - restart.get_width() // 2, HEIGHT // 2 + 60))


def handle_input(event, direction, next_direction):
    if event.type == pygame.KEYDOWN:
        if event.key in (pygame.K_UP, pygame.K_w) and direction != (0, 1):
            next_direction = (0, -1)
        elif event.key in (pygame.K_DOWN, pygame.K_s) and direction != (0, -1):
            next_direction = (0, 1)
        elif event.key in (pygame.K_LEFT, pygame.K_a) and direction != (1, 0):
            next_direction = (-1, 0)
        elif event.key in (pygame.K_RIGHT, pygame.K_d) and direction != (-1, 0):
            next_direction = (1, 0)
    return direction, next_direction


def move_snake(snake, direction, next_direction, food, score, speed):
    direction = next_direction
    head_x = snake[0][0] + direction[0]
    head_y = snake[0][1] + direction[1]

    if (
        head_x < 0
        or head_y < 0
        or head_x >= GRID_COUNT
        or head_y >= GRID_COUNT
        or [head_x, head_y] in snake[:-1]
    ):
        return snake, direction, next_direction, food, score, speed, True

    snake.insert(0, [head_x, head_y])

    if [head_x, head_y] == food:
        score += 10
        speed = min(18, speed + 1)
        food = generate_food(snake)
    else:
        snake.pop()

    return snake, direction, next_direction, food, score, speed, False


snake, direction, next_direction, food, score, speed, game_over = reset_game()

running = True
while running:
    clock.tick(speed)

    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False
        elif event.type == pygame.KEYDOWN:
            if event.key == pygame.K_ESCAPE:
                running = False
            elif event.key == pygame.K_r and game_over:
                snake, direction, next_direction, food, score, speed, game_over = reset_game()
            else:
                direction, next_direction = handle_input(event, direction, next_direction)

    if not game_over:
        snake, direction, next_direction, food, score, speed, game_over = move_snake(
            snake, direction, next_direction, food, score, speed
        )

    window.fill(BLACK)
    draw_grid()
    draw_food(food)
    draw_snake(snake)
    draw_score(score)

    if game_over:
        draw_game_over(score)

    pygame.display.flip()

pygame.quit()
sys.exit()
