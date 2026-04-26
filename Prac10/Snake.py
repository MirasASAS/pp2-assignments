import pygame
import random
import sys

pygame.init()

CELL      = 20
COLS      = 30
ROWS      = 30
WIDTH     = COLS * CELL
HEIGHT    = ROWS * CELL + 60
HUD_H     = 60

screen = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("Snake")
clock = pygame.time.Clock()

BLACK      = (0,   0,   0)
BG         = (15,  15,  15)
GRID_COLOR = (25,  25,  25)
GREEN      = (50,  205, 50)
DARK_GREEN = (34,  139, 34)
RED        = (220, 50,  50)
YELLOW     = (255, 220, 0)
WHITE      = (255, 255, 255)
GRAY       = (120, 120, 120)
ORANGE     = (255, 140, 0)
HUD_BG     = (20,  20,  20)

UP    = (0, -1)
DOWN  = (0,  1)
LEFT  = (-1, 0)
RIGHT = (1,  0)

font_large  = pygame.font.SysFont("Arial", 48, bold=True)
font_medium = pygame.font.SysFont("Arial", 28, bold=True)
font_small  = pygame.font.SysFont("Arial", 20)

LEVELS = [
    (0,   8),
    (30,  10),
    (60,  13),
    (100, 16),
    (150, 20),
    (210, 25),
]

def get_level_and_speed(score):
    level = 1
    speed = LEVELS[0][1]
    for i, (threshold, spd) in enumerate(LEVELS):
        if score >= threshold:
            level = i + 1
            speed = spd
    return level, speed

def random_food(snake_body):

    while True:
        pos = (random.randint(1, COLS - 2),
               random.randint(1, ROWS - 2))
        if pos not in snake_body:
            return pos

def draw_grid(surface):
    for x in range(0, WIDTH, CELL):
        pygame.draw.line(surface, GRID_COLOR, (x, HUD_H), (x, HEIGHT))
    for y in range(HUD_H, HEIGHT, CELL):
        pygame.draw.line(surface, GRID_COLOR, (0, y), (WIDTH, y))

def draw_walls(surface):
    pygame.draw.rect(surface, GRAY, (0, HUD_H, WIDTH, CELL))
    pygame.draw.rect(surface, GRAY, (0, HEIGHT - CELL, WIDTH, CELL))
    pygame.draw.rect(surface, GRAY, (0, HUD_H, CELL, HEIGHT - HUD_H))
    pygame.draw.rect(surface, GRAY, (WIDTH - CELL, HUD_H, CELL, HEIGHT - HUD_H))

def draw_snake(surface, body):
    for i, (cx, cy) in enumerate(body):
        x = cx * CELL
        y = cy * CELL + HUD_H
        color = GREEN if i == 0 else DARK_GREEN
        pygame.draw.rect(surface, color, (x + 1, y + 1, CELL - 2, CELL - 2),
                         border_radius=4)
        if i == 0:
            pygame.draw.circle(surface, WHITE, (x + 5, y + 6), 3)
            pygame.draw.circle(surface, WHITE, (x + 15, y + 6), 3)
            pygame.draw.circle(surface, BLACK, (x + 6, y + 7), 1)
            pygame.draw.circle(surface, BLACK, (x + 16, y + 7), 1)

def draw_food(surface, food):
    fx = food[0] * CELL + CELL // 2
    fy = food[1] * CELL + HUD_H + CELL // 2
    pygame.draw.circle(surface, RED, (fx, fy), CELL // 2 - 2)
    pygame.draw.circle(surface, (255, 120, 120), (fx - 3, fy - 3), 3)

def draw_hud(surface, score, level, speed):
    pygame.draw.rect(surface, HUD_BG, (0, 0, WIDTH, HUD_H))
    score_surf = font_medium.render(f"Score: {score}", True, YELLOW)
    level_surf = font_medium.render(f"Level: {level}", True, ORANGE)
    speed_surf = font_small.render(f"Speed: {speed} FPS", True, GRAY)
    surface.blit(score_surf, (10, 10))
    surface.blit(level_surf, (WIDTH // 2 - level_surf.get_width() // 2, 10))
    surface.blit(speed_surf, (WIDTH - speed_surf.get_width() - 10, 20))

def show_screen(surface, title, lines):
    overlay = pygame.Surface((WIDTH, HEIGHT), pygame.SRCALPHA)
    overlay.fill((0, 0, 0, 190))
    surface.blit(overlay, (0, 0))
    t = font_large.render(title, True, YELLOW)
    surface.blit(t, (WIDTH // 2 - t.get_width() // 2, HEIGHT // 2 - 80))
    for i, line in enumerate(lines):
        s = font_small.render(line, True, WHITE)
        surface.blit(s, (WIDTH // 2 - s.get_width() // 2, HEIGHT // 2 + i * 30))
    pygame.display.flip()

def main():
    start_x, start_y = COLS // 2, ROWS // 2
    snake  = [(start_x, start_y), (start_x - 1, start_y), (start_x - 2, start_y)]
    direction  = RIGHT
    next_dir   = RIGHT
    food       = random_food(snake)
    score      = 0
    game_over  = False
    paused     = False

    screen.fill(BG)
    show_screen(screen, "SNAKE",
                ["Arrow keys to move", "P = pause", "SPACE to start"])
    waiting = True
    while waiting:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit(); sys.exit()
            if event.type == pygame.KEYDOWN and event.key == pygame.K_SPACE:
                waiting = False

    while True:
        level, speed = get_level_and_speed(score)
        clock.tick(speed)

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit(); sys.exit()
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_p:
                    paused = not paused
                if game_over and event.key == pygame.K_SPACE:
                    main()
                    return
                if event.key == pygame.K_UP    and direction != DOWN:
                    next_dir = UP
                if event.key == pygame.K_DOWN  and direction != UP:
                    next_dir = DOWN
                if event.key == pygame.K_LEFT  and direction != RIGHT:
                    next_dir = LEFT
                if event.key == pygame.K_RIGHT and direction != LEFT:
                    next_dir = RIGHT

        if paused or game_over:
            if paused:
                show_screen(screen, "PAUSED", ["Press P to continue"])
            continue

        direction = next_dir

        head_x, head_y = snake[0]
        new_head = (head_x + direction[0], head_y + direction[1])

        if (new_head[0] <= 0 or new_head[0] >= COLS - 1 or
                new_head[1] <= 0 or new_head[1] >= ROWS - 1):
            game_over = True

        if new_head in snake:
            game_over = True

        if not game_over:
            snake.insert(0, new_head)

            if new_head == food:
                score += 10
                food = random_food(snake)
            else:
                snake.pop()

        screen.fill(BG)
        draw_grid(screen)
        draw_walls(screen)
        draw_food(screen, food)
        draw_snake(screen, snake)
        draw_hud(screen, score, level, speed)

        if game_over:
            show_screen(screen, "GAME OVER",
                        [f"Score: {score}  |  Level: {level}",
                         "Press SPACE to restart"])

        pygame.display.flip()

if __name__ == "__main__":
    main()