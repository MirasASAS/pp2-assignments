import pygame
import random
import sys

pygame.init()

WIDTH, HEIGHT = 600, 800
screen = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("Racer Game")
clock = pygame.time.Clock()
FPS = 60

WHITE      = (255, 255, 255)
BLACK      = (0,   0,   0)
GRAY       = (50,  50,  50)
DARK_GRAY  = (30,  30,  30)
YELLOW     = (255, 220, 0)
RED        = (220, 50,  50)
BLUE       = (50,  100, 220)
GREEN      = (50,  200, 50)
ORANGE     = (255, 165, 0)

ROAD_LEFT  = 100
ROAD_RIGHT = 500
LANE_WIDTH = (ROAD_RIGHT - ROAD_LEFT) // 3

font_large  = pygame.font.SysFont("Arial", 48, bold=True)
font_medium = pygame.font.SysFont("Arial", 32)
font_small  = pygame.font.SysFont("Arial", 22)

class PlayerCar:
    def __init__(self):
        self.width  = 50
        self.height = 90
        self.x = WIDTH // 2 - self.width // 2
        self.y = HEIGHT - 130
        self.speed = 6
        self.color = BLUE

    def draw(self, surface):
        pygame.draw.rect(surface, self.color,
                         (self.x, self.y, self.width, self.height), border_radius=8)
        pygame.draw.rect(surface, (180, 220, 255),
                         (self.x + 8, self.y + 10, self.width - 16, 22), border_radius=4)
        for wx, wy in [(self.x - 8, self.y + 10),
                       (self.x + self.width - 4, self.y + 10),
                       (self.x - 8, self.y + self.height - 30),
                       (self.x + self.width - 4, self.y + self.height - 30)]:
            pygame.draw.rect(surface, BLACK, (wx, wy, 12, 20), border_radius=3)

    def move(self, keys):
        if keys[pygame.K_LEFT]  and self.x > ROAD_LEFT:
            self.x -= self.speed
        if keys[pygame.K_RIGHT] and self.x + self.width < ROAD_RIGHT:
            self.x += self.speed
        if keys[pygame.K_UP]   and self.y > 0:
            self.y -= self.speed
        if keys[pygame.K_DOWN] and self.y + self.height < HEIGHT:
            self.y += self.speed

    def get_rect(self):
        return pygame.Rect(self.x, self.y, self.width, self.height)

class EnemyCar:
    def __init__(self, speed):
        self.width  = 50
        self.height = 90
        lane = random.randint(0, 2)
        self.x = ROAD_LEFT + lane * LANE_WIDTH + (LANE_WIDTH - self.width) // 2
        self.y = -self.height
        self.speed = speed
        self.color = random.choice([RED, ORANGE, GREEN])

    def draw(self, surface):
        pygame.draw.rect(surface, self.color,
                         (self.x, self.y, self.width, self.height), border_radius=8)
        pygame.draw.rect(surface, (180, 220, 180),
                         (self.x + 8, self.y + 10, self.width - 16, 22), border_radius=4)
        for wx, wy in [(self.x - 8, self.y + 10),
                       (self.x + self.width - 4, self.y + 10),
                       (self.x - 8, self.y + self.height - 30),
                       (self.x + self.width - 4, self.y + self.height - 30)]:
            pygame.draw.rect(surface, BLACK, (wx, wy, 12, 20), border_radius=3)

    def update(self):
        self.y += self.speed

    def get_rect(self):
        return pygame.Rect(self.x + 5, self.y + 5, self.width - 10, self.height - 10)

    def is_off_screen(self):
        return self.y > HEIGHT

class Coin:
    def __init__(self, speed):
        self.radius = 14
        lane = random.randint(0, 2)
        self.x = ROAD_LEFT + lane * LANE_WIDTH + LANE_WIDTH // 2
        self.y = -self.radius
        self.speed = speed

    def draw(self, surface):
        pygame.draw.circle(surface, YELLOW, (self.x, self.y), self.radius)
        pygame.draw.circle(surface, (200, 160, 0), (self.x, self.y), self.radius, 2)
        pygame.draw.circle(surface, WHITE, (self.x - 4, self.y - 4), 4)

    def update(self):
        self.y += self.speed

    def get_rect(self):
        return pygame.Rect(self.x - self.radius, self.y - self.radius,
                           self.radius * 2, self.radius * 2)

    def is_off_screen(self):
        return self.y > HEIGHT

class RoadLine:
    def __init__(self, x, y):
        self.x = x
        self.y = y
        self.width  = 10
        self.height = 50
        self.speed  = 8

    def update(self):
        self.y += self.speed
        if self.y > HEIGHT:
            self.y = -self.height

    def draw(self, surface):
        pygame.draw.rect(surface, WHITE,
                         (self.x - self.width // 2, self.y, self.width, self.height))

def spawn_lines():
    lines = []
    for lane in range(1, 3):
        x = ROAD_LEFT + lane * LANE_WIDTH
        for row in range(6):
            lines.append(RoadLine(x, row * (HEIGHT // 5)))
    return lines

def draw_road(surface):
    pygame.draw.rect(surface, GRAY, (ROAD_LEFT, 0, ROAD_RIGHT - ROAD_LEFT, HEIGHT))
    pygame.draw.rect(surface, YELLOW, (ROAD_LEFT, 0, 6, HEIGHT))
    pygame.draw.rect(surface, YELLOW, (ROAD_RIGHT - 6, 0, 6, HEIGHT))

def draw_hud(surface, score, coins, speed_level):
    score_surf = font_small.render(f"Score: {score}", True, WHITE)
    surface.blit(score_surf, (10, 10))

    level_surf = font_small.render(f"Speed: {speed_level}", True, WHITE)
    surface.blit(level_surf, (10, 36))

    coin_surf = font_medium.render(f"Coins: {coins}", True, YELLOW)
    surface.blit(coin_surf, (WIDTH - coin_surf.get_width() - 15, 10))

def show_screen(surface, title, subtitle):
    overlay = pygame.Surface((WIDTH, HEIGHT), pygame.SRCALPHA)
    overlay.fill((0, 0, 0, 180))
    surface.blit(overlay, (0, 0))
    t = font_large.render(title, True, YELLOW)
    s = font_small.render(subtitle, True, WHITE)
    surface.blit(t, (WIDTH // 2 - t.get_width() // 2, HEIGHT // 2 - 60))
    surface.blit(s, (WIDTH // 2 - s.get_width() // 2, HEIGHT // 2 + 10))
    pygame.display.flip()

def main():
    player      = PlayerCar()
    enemies     = []
    coins       = []
    road_lines  = spawn_lines()

    score       = 0
    coin_count  = 0
    speed_level = 1
    enemy_speed = 5
    enemy_timer = 0
    coin_timer  = 0
    frame       = 0
    running     = True
    game_over   = False

    screen.fill(DARK_GRAY)
    show_screen(screen, "RACER", "Press SPACE to start  |  Arrow keys to move")
    waiting = True
    while waiting:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit(); sys.exit()
            if event.type == pygame.KEYDOWN and event.key == pygame.K_SPACE:
                waiting = False

    while running:
        clock.tick(FPS)
        frame += 1

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit(); sys.exit()
            if event.type == pygame.KEYDOWN:
                if game_over and event.key == pygame.K_SPACE:
                    main()
                    return

        if not game_over:
            keys = pygame.key.get_pressed()
            player.move(keys)

            score += 1
            if score % 300 == 0:
                speed_level += 1
                enemy_speed = 5 + speed_level

            enemy_timer += 1
            if enemy_timer >= 90:
                enemies.append(EnemyCar(enemy_speed))
                enemy_timer = 0

            coin_timer += 1
            if coin_timer >= 120:
                coins.append(Coin(enemy_speed - 1))
                coin_timer = 0

            for line in road_lines:
                line.update()

            for enemy in enemies[:]:
                enemy.update()
                if enemy.is_off_screen():
                    enemies.remove(enemy)
                elif player.get_rect().colliderect(enemy.get_rect()):
                    game_over = True

            for coin in coins[:]:
                coin.update()
                if coin.is_off_screen():
                    coins.remove(coin)
                elif player.get_rect().colliderect(coin.get_rect()):
                    coin_count += 1
                    coins.remove(coin)

        screen.fill(DARK_GRAY)
        draw_road(screen)

        for line in road_lines:
            line.draw(screen)
        for enemy in enemies:
            enemy.draw(screen)
        for coin in coins:
            coin.draw(screen)

        player.draw(screen)
        draw_hud(screen, score, coin_count, speed_level)

        if game_over:
            show_screen(screen, "GAME OVER",
                        f"Score: {score}  |  Coins: {coin_count}  |  SPACE to restart")

        pygame.display.flip()

if __name__ == "__main__":
    main()