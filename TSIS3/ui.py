import pygame

WHITE  = (255, 255, 255)
BLACK  = (0,   0,   0)
GRAY   = (180, 180, 180)
DARK   = (30,  30,  30)
GREEN  = (0,   200, 80)
RED    = (220, 50,  50)
YELLOW = (255, 220, 0)
BLUE   = (0,   120, 255)


def draw_button(screen, font, text, rect, color=DARK, text_color=WHITE, hover=False):
    col = tuple(min(c + 40, 255) for c in color) if hover else color
    pygame.draw.rect(screen, col, rect, border_radius=8)
    pygame.draw.rect(screen, WHITE, rect, 2, border_radius=8)
    lbl = font.render(text, True, text_color)
    screen.blit(lbl, (rect.centerx - lbl.get_width()//2,
                      rect.centery - lbl.get_height()//2))


def draw_text_center(screen, font, text, y, color=WHITE):
    lbl = font.render(text, True, color)
    screen.blit(lbl, (screen.get_width()//2 - lbl.get_width()//2, y))


def main_menu_screen(screen, fonts, mouse_pos):
    screen.fill(DARK)
    draw_text_center(screen, fonts["title"], "RACER", 80, YELLOW)
    draw_text_center(screen, fonts["sub"],   "Advanced Driving", 150, GRAY)

    buttons = {
        "play":        pygame.Rect(300, 230, 200, 50),
        "leaderboard": pygame.Rect(300, 300, 200, 50),
        "settings":    pygame.Rect(300, 370, 200, 50),
        "quit":        pygame.Rect(300, 440, 200, 50),
    }
    labels = {"play":"Play", "leaderboard":"Leaderboard",
              "settings":"Settings", "quit":"Quit"}
    for key, rect in buttons.items():
        draw_button(screen, fonts["btn"], labels[key], rect,
                    hover=rect.collidepoint(mouse_pos))
    return buttons


def leaderboard_screen(screen, fonts, entries, mouse_pos):
    screen.fill(DARK)
    draw_text_center(screen, fonts["title"], "TOP 10", 40, YELLOW)
    headers = f"{'#':<4} {'Name':<16} {'Score':<10} {'Distance'}"
    lbl = fonts["small"].render(headers, True, GRAY)
    screen.blit(lbl, (80, 110))
    pygame.draw.line(screen, GRAY, (80, 130), (720, 130), 1)

    for i, e in enumerate(entries[:10]):
        row = f"{i+1:<4} {e['name']:<16} {e['score']:<10} {int(e['distance'])} m"
        col = YELLOW if i == 0 else WHITE
        lbl = fonts["small"].render(row, True, col)
        screen.blit(lbl, (80, 140 + i * 30))

    back = pygame.Rect(300, 560, 200, 50)
    draw_button(screen, fonts["btn"], "Back", back,
                hover=back.collidepoint(mouse_pos))
    return {"back": back}


def settings_screen(screen, fonts, settings, mouse_pos):
    screen.fill(DARK)
    draw_text_center(screen, fonts["title"], "Settings", 40, YELLOW)

    sound_rect = pygame.Rect(300, 140, 200, 45)
    color_rects = {}
    car_colors = {
        "Blue":   [0, 120, 255],
        "Red":    [220, 50, 50],
        "Green":  [0, 200, 80],
        "Yellow": [255, 220, 0],
    }
    diff_rects = {}
    diffs = ["easy", "normal", "hard"]

    lbl = fonts["sub"].render("Sound:", True, WHITE)
    screen.blit(lbl, (80, 150))
    sound_text = "ON" if settings["sound"] else "OFF"
    sound_col  = GREEN if settings["sound"] else RED
    draw_button(screen, fonts["btn"], sound_text, sound_rect,
                color=sound_col, hover=sound_rect.collidepoint(mouse_pos))

    lbl = fonts["sub"].render("Car Color:", True, WHITE)
    screen.blit(lbl, (80, 220))
    for i, (name, col) in enumerate(car_colors.items()):
        r = pygame.Rect(80 + i * 110, 255, 100, 40)
        color_rects[name] = r
        border = YELLOW if settings["car_color"] == col else WHITE
        pygame.draw.rect(screen, col, r, border_radius=6)
        pygame.draw.rect(screen, border, r, 3, border_radius=6)
        cl = fonts["small"].render(name, True, BLACK)
        screen.blit(cl, (r.centerx - cl.get_width()//2,
                         r.centery - cl.get_height()//2))

    lbl = fonts["sub"].render("Difficulty:", True, WHITE)
    screen.blit(lbl, (80, 320))
    for i, d in enumerate(diffs):
        r = pygame.Rect(80 + i * 130, 355, 120, 40)
        diff_rects[d] = r
        active = settings["difficulty"] == d
        draw_button(screen, fonts["btn"], d.capitalize(), r,
                    color=GREEN if active else DARK,
                    hover=r.collidepoint(mouse_pos))

    back = pygame.Rect(300, 500, 200, 50)
    draw_button(screen, fonts["btn"], "Back", back,
                hover=back.collidepoint(mouse_pos))

    return {"sound": sound_rect, "colors": color_rects,
            "diffs": diff_rects, "back": back,
            "car_colors": car_colors}


def gameover_screen(screen, fonts, score, distance, coins, mouse_pos):
    screen.fill(DARK)
    draw_text_center(screen, fonts["title"], "GAME OVER", 100, RED)
    draw_text_center(screen, fonts["sub"], f"Score:    {score}", 200, WHITE)
    draw_text_center(screen, fonts["sub"], f"Distance: {int(distance)} m", 245, WHITE)
    draw_text_center(screen, fonts["sub"], f"Coins:    {coins}", 290, YELLOW)

    retry = pygame.Rect(200, 390, 180, 50)
    menu  = pygame.Rect(420, 390, 180, 50)
    draw_button(screen, fonts["btn"], "Retry",     retry,
                hover=retry.collidepoint(mouse_pos))
    draw_button(screen, fonts["btn"], "Main Menu", menu,
                hover=menu.collidepoint(mouse_pos))
    return {"retry": retry, "menu": menu}


def username_screen(screen, fonts, name_buf):
    screen.fill(DARK)
    draw_text_center(screen, fonts["title"], "Enter Your Name", 160, YELLOW)
    box = pygame.Rect(200, 260, 400, 55)
    pygame.draw.rect(screen, WHITE, box, border_radius=8)
    pygame.draw.rect(screen, YELLOW, box, 2, border_radius=8)
    lbl = fonts["sub"].render(name_buf + "|", True, BLACK)
    screen.blit(lbl, (box.x + 10, box.y + 12))
    draw_text_center(screen, fonts["small"], "Press Enter to start", 340, GRAY)