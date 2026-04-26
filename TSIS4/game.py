import pygame
import random
import json
import os

CELL       = 20
COLS       = 30
ROWS       = 28
W          = COLS * CELL
H          = ROWS * CELL + 60

WHITE      = (255, 255, 255)
BLACK      = (0,   0,   0)
GRAY       = (180, 180, 180)
DARK       = (30,  30,  30)
GREEN      = (0,   200, 80)
RED        = (220, 50,  50)
DARK_RED   = (140, 0,   0)
YELLOW     = (255, 220, 0)
ORANGE     = (255, 140, 0)
BLUE       = (0,   120, 255)
PURPLE     = (160, 0,   200)
CYAN       = (0,   200, 200)

SETTINGS_FILE = "settings.json"
DEFAULT_SETTINGS = {
    "snake_color": [0, 200, 80],
    "grid":        True,
    "sound":       False,
}

UP    = (0, -1)
DOWN  = (0,  1)
LEFT  = (-1, 0)
RIGHT = (1,  0)

PU_SPEED  = "speed_boost"
PU_SLOW   = "slow_motion"
PU_SHIELD = "shield"
PU_TIMEOUT = 8000


def load_settings():
    if not os.path.exists(SETTINGS_FILE):
        return DEFAULT_SETTINGS.copy()
    with open(SETTINGS_FILE) as f:
        data = json.load(f)
    for k, v in DEFAULT_SETTINGS.items():
        data.setdefault(k, v)
    return data


def save_settings(s):
    with open(SETTINGS_FILE, "w") as f:
        json.dump(s, f, indent=2)


def random_cell(excluded=None):
    excluded = excluded or set()
    while True:
        c = (random.randint(0, COLS-1), random.randint(0, ROWS-1))
        if c not in excluded:
            return c


class Food:
    def __init__(self, pos, kind="normal"):
        self.pos   = pos
        self.kind  = kind
        self.spawn = pygame.time.get_ticks()
        if kind == "normal":
            self.points  = 1
            self.color   = RED
            self.timeout = None
        elif kind == "bonus":
            self.points  = 3
            self.color   = ORANGE
            self.timeout = 6000
        elif kind == "poison":
            self.points  = 0
            self.color   = DARK_RED
            self.timeout = None

    def expired(self):
        if self.timeout is None:
            return False
        return pygame.time.get_ticks() - self.spawn > self.timeout

    def draw(self, screen, offset_y):
        x = self.pos[0] * CELL + CELL // 2
        y = self.pos[1] * CELL + CELL // 2 + offset_y
        pygame.draw.circle(screen, self.color, (x, y), CELL // 2 - 2)
        if self.kind == "poison":
            pygame.draw.circle(screen, WHITE, (x, y), CELL // 4)


class PowerUp:
    def __init__(self, pos, kind):
        self.pos   = pos
        self.kind  = kind
        self.spawn = pygame.time.get_ticks()
        self.color = {PU_SPEED: CYAN, PU_SLOW: PURPLE, PU_SHIELD: YELLOW}[kind]
        self.label = {PU_SPEED: "S", PU_SLOW: "M", PU_SHIELD: "SH"}[kind]

    def expired(self):
        return pygame.time.get_ticks() - self.spawn > PU_TIMEOUT

    def draw(self, screen, offset_y, font):
        x = self.pos[0] * CELL
        y = self.pos[1] * CELL + offset_y
        pygame.draw.rect(screen, self.color,
                         pygame.Rect(x+2, y+2, CELL-4, CELL-4),
                         border_radius=4)
        lbl = font.render(self.label, True, BLACK)
        screen.blit(lbl, (x + CELL//2 - lbl.get_width()//2,
                          y + CELL//2 - lbl.get_height()//2))


class SnakeGame:
    OFFSET_Y = 60

    def __init__(self, username, personal_best, settings):
        self.username      = username
        self.personal_best = personal_best
        self.settings      = settings
        self.snake_color   = tuple(settings["snake_color"])

        self.snake    = [(COLS//2, ROWS//2)]
        self.dir      = RIGHT
        self.next_dir = RIGHT
        self.score    = 0
        self.level    = 1
        self.food_eaten = 0
        self.alive    = True
        self.shield   = False

        self.base_speed   = 8
        self.speed        = self.base_speed
        self.pu_active    = None
        self.pu_end_time  = 0

        self.obstacles = set()
        self.foods     = []
        self.powerup   = None

        self.font      = pygame.font.SysFont("Arial", 16)
        self.font_big  = pygame.font.SysFont("Arial", 22, bold=True)

        self._spawn_food("normal")
        self._spawn_food("bonus")
        self._spawn_poison()

    def _occupied(self):
        return set(self.snake) | self.obstacles | \
               {f.pos for f in self.foods} | \
               ({self.powerup.pos} if self.powerup else set())

    def _spawn_food(self, kind):
        pos = random_cell(self._occupied())
        self.foods.append(Food(pos, kind))

    def _spawn_poison(self):
        pos = random_cell(self._occupied())
        self.foods.append(Food(pos, "poison"))

    def _spawn_powerup(self):
        if self.powerup is None:
            kind = random.choice([PU_SPEED, PU_SLOW, PU_SHIELD])
            pos  = random_cell(self._occupied())
            self.powerup = PowerUp(pos, kind)

    def _spawn_obstacles(self):
        count = 3 + (self.level - 3) * 2
        occ   = set(self.snake) | {f.pos for f in self.foods}
        for _ in range(count):
            pos = random_cell(occ | self.obstacles)
            self.obstacles.add(pos)
            occ.add(pos)

    def _level_up(self):
        self.level     += 1
        self.base_speed = min(8 + self.level * 2, 25)
        if self.pu_active is None:
            self.speed = self.base_speed
        if self.level >= 3:
            self._spawn_obstacles()
        self._spawn_food("normal")
        self._spawn_food("bonus")
        self._spawn_poison()
        if random.random() < 0.6:
            self._spawn_powerup()

    def handle_key(self, key):
        if key == pygame.K_UP    and self.dir != DOWN:
            self.next_dir = UP
        elif key == pygame.K_DOWN  and self.dir != UP:
            self.next_dir = DOWN
        elif key == pygame.K_LEFT  and self.dir != RIGHT:
            self.next_dir = LEFT
        elif key == pygame.K_RIGHT and self.dir != LEFT:
            self.next_dir = RIGHT

    def update(self):
        if not self.alive:
            return

        now = pygame.time.get_ticks()
        if self.pu_active and now > self.pu_end_time:
            self.pu_active = None
            self.speed     = self.base_speed

        self.dir  = self.next_dir
        head      = (self.snake[0][0] + self.dir[0],
                     self.snake[0][1] + self.dir[1])

        wall_hit = (head[0] < 0 or head[0] >= COLS or
                    head[1] < 0 or head[1] >= ROWS)
        self_hit = head in self.snake[1:]
        obs_hit  = head in self.obstacles

        if wall_hit or self_hit or obs_hit:
            if self.shield:
                self.shield = False
                head = self.snake[0]
            else:
                self.alive = False
                return

        self.snake.insert(0, head)
        grew = False

        for food in self.foods[:]:
            if food.pos == head:
                if food.kind == "poison":
                    for _ in range(2):
                        if len(self.snake) > 1:
                            self.snake.pop()
                    if len(self.snake) <= 1:
                        self.alive = False
                        return
                else:
                    self.score     += food.points * self.level
                    self.food_eaten += 1
                    grew = True
                    if food.kind == "normal":
                        self._spawn_food("normal")
                    else:
                        self._spawn_food("bonus")
                self.foods.remove(food)
                if food.kind == "poison":
                    self._spawn_poison()
                break

        if self.powerup and self.powerup.pos == head:
            self._apply_powerup(self.powerup.kind)
            self.powerup = None

        if not grew:
            self.snake.pop()

        for food in self.foods[:]:
            if food.expired():
                self.foods.remove(food)
                self._spawn_food(food.kind if food.kind != "poison" else "bonus")

        if self.powerup and self.powerup.expired():
            self.powerup = None

        if self.food_eaten > 0 and self.food_eaten % 5 == 0:
            self.food_eaten = 0
            self._level_up()

    def _apply_powerup(self, kind):
        now = pygame.time.get_ticks()
        self.pu_active  = kind
        self.pu_end_time = now + 5000
        if kind == PU_SPEED:
            self.speed = self.base_speed + 6
        elif kind == PU_SLOW:
            self.speed = max(2, self.base_speed - 4)
        elif kind == PU_SHIELD:
            self.shield    = True
            self.pu_active = None

    def draw(self, screen):
        screen.fill(DARK)
        oy = self.OFFSET_Y

        if self.settings["grid"]:
            for x in range(0, W, CELL):
                pygame.draw.line(screen, (50,50,50), (x, oy), (x, oy+ROWS*CELL))
            for y in range(0, ROWS*CELL+1, CELL):
                pygame.draw.line(screen, (50,50,50), (0, oy+y), (W, oy+y))

        for obs in self.obstacles:
            pygame.draw.rect(screen, GRAY,
                             pygame.Rect(obs[0]*CELL+1, obs[1]*CELL+oy+1,
                                         CELL-2, CELL-2))

        for food in self.foods:
            food.draw(screen, oy)

        if self.powerup:
            self.powerup.draw(screen, oy, self.font)

        for i, seg in enumerate(self.snake):
            col = WHITE if i == 0 else self.snake_color
            if self.shield and i == 0:
                col = YELLOW
            pygame.draw.rect(screen, col,
                             pygame.Rect(seg[0]*CELL+1, seg[1]*CELL+oy+1,
                                         CELL-2, CELL-2),
                             border_radius=3)

        self._draw_hud(screen)

    def _draw_hud(self, screen):
        pygame.draw.rect(screen, (20,20,20), (0, 0, W, self.OFFSET_Y))
        items = [
            f"Score: {self.score}",
            f"Level: {self.level}",
            f"Best:  {self.personal_best}",
            f"User:  {self.username}",
        ]
        for i, txt in enumerate(items):
            lbl = self.font_big.render(txt, True, WHITE)
            screen.blit(lbl, (10 + i * 150, 10))

        if self.pu_active:
            rem = max(0, (self.pu_end_time - pygame.time.get_ticks()) // 1000)
            lbl = self.font.render(f"Power-up: {self.pu_active} ({rem}s)",
                                   True, CYAN)
            screen.blit(lbl, (10, 36))
        if self.shield:
            lbl = self.font.render("SHIELD ON", True, YELLOW)
            screen.blit(lbl, (300, 36))