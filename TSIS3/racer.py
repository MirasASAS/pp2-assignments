import pygame
import random
import math

WHITE  = (255, 255, 255)
BLACK  = (0,   0,   0)
GRAY   = (180, 180, 180)
DARK   = (30,  30,  30)
GREEN  = (0,   200, 80)
RED    = (220, 50,  50)
YELLOW = (255, 220, 0)
ORANGE = (255, 140, 0)
ROAD_COLOR  = (60,  60,  60)
LANE_COLOR  = (255, 255, 100)

WIDTH, HEIGHT = 800, 650
ROAD_LEFT  = 150
ROAD_RIGHT = 650
ROAD_W     = ROAD_RIGHT - ROAD_LEFT
LANES      = 4
LANE_W     = ROAD_W // LANES

DIFFICULTY_SETTINGS = {
    "easy":   {"traffic_interval": 120, "obstacle_interval": 180, "base_speed": 4},
    "normal": {"traffic_interval": 80,  "obstacle_interval": 120, "base_speed": 5},
    "hard":   {"traffic_interval": 50,  "obstacle_interval": 80,  "base_speed": 7},
}

POWERUP_COLORS = {"nitro": ORANGE, "shield": (0, 180, 255), "repair": GREEN}
TRAFFIC_COLORS = [RED, (180,0,180), (0,160,160), (200,200,0)]


def lane_x(lane):
    return ROAD_LEFT + lane * LANE_W + LANE_W // 2


class Player:
    W, H = 40, 70

    def __init__(self, car_color):
        self.lane     = 1
        self.x        = lane_x(1)
        self.y        = HEIGHT - 120
        self.color    = tuple(car_color)
        self.speed    = 5
        self.shield   = False
        self.nitro    = False
        self.nitro_t  = 0
        self.coins    = 0
        self.score    = 0
        self.distance = 0
        self.alive    = True
        self.move_x   = 0

    def update(self):
        self.x += self.move_x
        self.x  = max(ROAD_LEFT + self.W//2,
                      min(ROAD_RIGHT - self.W//2, self.x))
        if self.nitro:
            self.nitro_t -= 1
            if self.nitro_t <= 0:
                self.nitro  = False
                self.speed  = max(self.speed - 3, 5)

        self.distance += (self.speed / 60)

    def get_rect(self):
        return pygame.Rect(self.x - self.W//2, self.y - self.H//2,
                           self.W, self.H)

    def draw(self, screen):
        r = self.get_rect()
        pygame.draw.rect(screen, self.color, r, border_radius=6)
        pygame.draw.rect(screen, WHITE, r, 2, border_radius=6)
        if self.shield:
            pygame.draw.ellipse(screen, (0,180,255),
                                r.inflate(14, 14), 3)

    def activate_nitro(self):
        if not self.nitro:
            self.nitro   = True
            self.nitro_t = 60 * 4
            self.speed  += 3

    def activate_shield(self):
        self.shield = True

    def hit(self):
        if self.shield:
            self.shield = False
            return False
        self.alive = False
        return True


class TrafficCar:
    W, H = 38, 65

    def __init__(self, lane, speed, color):
        self.lane  = lane
        self.x     = lane_x(lane)
        self.y     = -self.H
        self.speed = speed
        self.color = color

    def update(self):
        self.y += self.speed

    def get_rect(self):
        return pygame.Rect(self.x - self.W//2, self.y - self.H//2,
                           self.W, self.H)

    def draw(self, screen):
        r = self.get_rect()
        pygame.draw.rect(screen, self.color, r, border_radius=6)
        pygame.draw.rect(screen, BLACK, r, 2, border_radius=6)

    def off_screen(self):
        return self.y > HEIGHT + self.H


class Obstacle:
    W, H = 44, 24

    def __init__(self, lane, speed, kind):
        self.lane  = lane
        self.x     = lane_x(lane)
        self.y     = -self.H
        self.speed = speed
        self.kind  = kind
        self.color = (80,80,80) if kind == "barrier" else \
                     (30,30,180) if kind == "oil" else (100,60,20)

    def update(self):
        self.y += self.speed

    def get_rect(self):
        return pygame.Rect(self.x - self.W//2, self.y - self.H//2,
                           self.W, self.H)

    def draw(self, screen):
        r = self.get_rect()
        pygame.draw.rect(screen, self.color, r, border_radius=4)
        lbl = pygame.font.SysFont("Arial", 11).render(self.kind, True, WHITE)
        screen.blit(lbl, (r.x+2, r.y+4))

    def off_screen(self):
        return self.y > HEIGHT + self.H


class PowerUp:
    SIZE = 30
    TIMEOUT = 300

    def __init__(self, lane, kind):
        self.lane  = lane
        self.x     = lane_x(lane)
        self.y     = -self.SIZE
        self.speed = 5
        self.kind  = kind
        self.color = POWERUP_COLORS[kind]
        self.timer = self.TIMEOUT

    def update(self):
        self.y     += self.speed
        self.timer -= 1

    def get_rect(self):
        s = self.SIZE
        return pygame.Rect(self.x - s//2, self.y - s//2, s, s)

    def draw(self, screen):
        pygame.draw.rect(screen, self.color, self.get_rect(), border_radius=6)
        lbl = pygame.font.SysFont("Arial", 11, bold=True).render(
            self.kind[0].upper(), True, BLACK)
        r = self.get_rect()
        screen.blit(lbl, (r.centerx - lbl.get_width()//2,
                          r.centery - lbl.get_height()//2))

    def expired(self):
        return self.timer <= 0 or self.y > HEIGHT + self.SIZE


class Coin:
    R = 10

    def __init__(self, lane, value=1, speed=5):
        self.lane  = lane
        self.x     = lane_x(lane)
        self.y     = -self.R
        self.speed = speed
        self.value = value
        self.color = YELLOW if value == 1 else ORANGE if value == 2 else WHITE

    def update(self):
        self.y += self.speed

    def get_rect(self):
        return pygame.Rect(self.x - self.R, self.y - self.R,
                           self.R*2, self.R*2)

    def draw(self, screen):
        pygame.draw.circle(screen, self.color, (self.x, int(self.y)), self.R)
        pygame.draw.circle(screen, BLACK, (self.x, int(self.y)), self.R, 1)

    def off_screen(self):
        return self.y > HEIGHT + self.R


class NitroStrip:
    H = 18

    def __init__(self, speed):
        self.y     = -self.H
        self.speed = speed

    def update(self):
        self.y += self.speed

    def draw(self, screen):
        rect = pygame.Rect(ROAD_LEFT, int(self.y), ROAD_W, self.H)
        pygame.draw.rect(screen, ORANGE, rect)
        lbl = pygame.font.SysFont("Arial", 11).render("NITRO STRIP", True, BLACK)
        screen.blit(lbl, (rect.centerx - lbl.get_width()//2,
                           rect.y + 2))

    def get_rect(self):
        return pygame.Rect(ROAD_LEFT, int(self.y), ROAD_W, self.H)

    def off_screen(self):
        return self.y > HEIGHT


class Game:
    def __init__(self, username, settings):
        self.username   = username
        self.settings   = settings
        diff            = settings.get("difficulty", "normal")
        ds              = DIFFICULTY_SETTINGS[diff]
        self.base_speed = ds["base_speed"]
        self.traffic_iv = ds["traffic_interval"]
        self.obstacle_iv= ds["obstacle_interval"]

        self.player     = Player(settings["car_color"])
        self.player.speed = self.base_speed

        self.traffic    = []
        self.obstacles  = []
        self.powerups   = []
        self.coins      = []
        self.nitro_strips = []

        self.scroll_y   = 0
        self.tick       = 0
        self.coin_tick  = 0
        self.pu_tick    = 0
        self.nitro_tick = 0
        self.active_pu  = None
        self.pu_timer   = 0

        self.font       = pygame.font.SysFont("Arial", 18)
        self.font_big   = pygame.font.SysFont("Arial", 24, bold=True)

    def _safe_lane(self, exclude_lane=None):
        lanes = [l for l in range(LANES) if l != exclude_lane]
        return random.choice(lanes)

    def spawn_traffic(self):
        lane  = random.randint(0, LANES-1)
        speed = self.base_speed + random.uniform(0, 2) + self.player.distance * 0.01
        color = random.choice(TRAFFIC_COLORS)
        self.traffic.append(TrafficCar(lane, speed, color))

    def spawn_obstacle(self):
        lane  = self._safe_lane(self.player.lane)
        kind  = random.choice(["barrier", "oil", "pothole"])
        speed = self.base_speed
        self.obstacles.append(Obstacle(lane, speed, kind))

    def spawn_coin(self):
        lane  = random.randint(0, LANES-1)
        value = random.choices([1, 2, 5], weights=[70, 20, 10])[0]
        self.coins.append(Coin(lane, value, self.base_speed))

    def spawn_powerup(self):
        if not self.powerups:
            kind = random.choice(["nitro", "shield", "repair"])
            lane = random.randint(0, LANES-1)
            self.powerups.append(PowerUp(lane, kind))

    def update(self):
        if not self.player.alive:
            return

        self.tick      += 1
        self.coin_tick += 1
        self.pu_tick   += 1
        self.nitro_tick+= 1

        iv_scale = max(0.5, 1 - self.player.distance * 0.001)
        if self.tick % max(20, int(self.traffic_iv * iv_scale)) == 0:
            self.spawn_traffic()
        if self.tick % max(40, int(self.obstacle_iv * iv_scale)) == 0:
            self.spawn_obstacle()
        if self.coin_tick % 40 == 0:
            self.spawn_coin()
        if self.pu_tick % 300 == 0:
            self.spawn_powerup()
        if self.nitro_tick % 500 == 0:
            self.nitro_strips.append(NitroStrip(self.base_speed))

        self.player.update()
        pr = self.player.get_rect()

        for t in self.traffic[:]:
            t.update()
            if t.get_rect().colliderect(pr):
                self.player.hit()
            if t.off_screen():
                self.traffic.remove(t)

        for o in self.obstacles[:]:
            o.update()
            if o.get_rect().colliderect(pr):
                self.player.hit()
            if o.off_screen():
                self.obstacles.remove(o)

        for c in self.coins[:]:
            c.update()
            if c.get_rect().colliderect(pr):
                self.player.coins += c.value
                self.player.score += c.value * 10
                self.coins.remove(c)
            elif c.off_screen():
                self.coins.remove(c)

        for p in self.powerups[:]:
            p.update()
            if p.get_rect().colliderect(pr):
                self._apply_powerup(p.kind)
                self.powerups.remove(p)
            elif p.expired():
                self.powerups.remove(p)

        for ns in self.nitro_strips[:]:
            ns.update()
            if ns.get_rect().colliderect(pr):
                self.player.activate_nitro()
                self.nitro_strips.remove(ns)
            elif ns.off_screen():
                self.nitro_strips.remove(ns)

        self.player.score = (self.player.coins * 10 +
                             int(self.player.distance) * 2)
        self.scroll_y = (self.scroll_y + self.base_speed) % 80

    def _apply_powerup(self, kind):
        if kind == "nitro":
            self.player.activate_nitro()
        elif kind == "shield":
            self.player.activate_shield()
        elif kind == "repair":
            self.player.alive = True
            self.player.shield = False

    def draw(self, screen):
        screen.fill((40, 40, 40))
        pygame.draw.rect(screen, ROAD_COLOR,
                         (ROAD_LEFT, 0, ROAD_W, HEIGHT))
        for l in range(1, LANES):
            x = ROAD_LEFT + l * LANE_W
            for y in range(-80 + self.scroll_y, HEIGHT, 80):
                pygame.draw.rect(screen, LANE_COLOR, (x-2, y, 4, 40))

        for ns in self.nitro_strips:
            ns.draw(screen)
        for c in self.coins:
            c.draw(screen)
        for p in self.powerups:
            p.draw(screen)
        for o in self.obstacles:
            o.draw(screen)
        for t in self.traffic:
            t.draw(screen)
        self.player.draw(screen)

        self._draw_hud(screen)

    def _draw_hud(self, screen):
        py = self.player
        lines = [
            f"Score:    {py.score}",
            f"Coins:    {py.coins}",
            f"Distance: {int(py.distance)} m",
            f"Speed:    {'NITRO' if py.nitro else 'normal'}",
            f"Shield:   {'ON' if py.shield else 'off'}",
        ]
        for i, line in enumerate(lines):
            lbl = self.font.render(line, True, WHITE)
            screen.blit(lbl, (10, 10 + i * 24))

        if self.powerups:
            p = self.powerups[0]
            t = max(0, p.timer)
            lbl = self.font.render(
                f"Power-up: {p.kind}  ({t//60}s)", True, p.color)
            screen.blit(lbl, (ROAD_RIGHT + 10, 10))

        lbl = self.font_big.render(self.username, True, YELLOW)
        screen.blit(lbl, (ROAD_RIGHT + 10, HEIGHT - 40))