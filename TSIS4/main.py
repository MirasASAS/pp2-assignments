import pygame
import sys
from game import SnakeGame, W, H, load_settings, save_settings, CELL
from db import init_db, get_or_create_player, save_session, get_leaderboard, get_personal_best

WHITE  = (255, 255, 255)
BLACK  = (0,   0,   0)
GRAY   = (180, 180, 180)
DARK   = (30,  30,  30)
GREEN  = (0,   200, 80)
RED    = (220, 50,  50)
YELLOW = (255, 220, 0)
CYAN   = (0,   200, 200)

MENU     = "menu"
USERNAME = "username"
PLAYING  = "playing"
GAMEOVER = "gameover"
LEADER   = "leaderboard"
SETTINGS = "settings"


def make_fonts():
    return {
        "title": pygame.font.SysFont("Arial", 48, bold=True),
        "sub":   pygame.font.SysFont("Arial", 26),
        "btn":   pygame.font.SysFont("Arial", 20),
        "small": pygame.font.SysFont("Arial", 16),
    }


def draw_btn(screen, font, text, rect, color=DARK, hover=False):
    col = tuple(min(c+40,255) for c in color) if hover else color
    pygame.draw.rect(screen, col, rect, border_radius=8)
    pygame.draw.rect(screen, WHITE, rect, 2, border_radius=8)
    lbl = font.render(text, True, WHITE)
    screen.blit(lbl, (rect.centerx - lbl.get_width()//2,
                      rect.centery - lbl.get_height()//2))


def draw_center(screen, font, text, y, color=WHITE):
    lbl = font.render(text, True, color)
    screen.blit(lbl, (W//2 - lbl.get_width()//2, y))


def menu_screen(screen, fonts, mp):
    screen.fill(DARK)
    draw_center(screen, fonts["title"], "SNAKE", 80, YELLOW)
    btns = {
        "play":        pygame.Rect(W//2-100, 200, 200, 50),
        "leaderboard": pygame.Rect(W//2-100, 270, 200, 50),
        "settings":    pygame.Rect(W//2-100, 340, 200, 50),
        "quit":        pygame.Rect(W//2-100, 410, 200, 50),
    }
    labels = {"play":"Play","leaderboard":"Leaderboard",
              "settings":"Settings","quit":"Quit"}
    for k, r in btns.items():
        draw_btn(screen, fonts["btn"], labels[k], r, hover=r.collidepoint(mp))
    return btns


def username_screen(screen, fonts, buf):
    screen.fill(DARK)
    draw_center(screen, fonts["title"], "Enter Name", 140, YELLOW)
    box = pygame.Rect(W//2-150, 230, 300, 50)
    pygame.draw.rect(screen, WHITE, box, border_radius=8)
    lbl = fonts["sub"].render(buf+"|", True, BLACK)
    screen.blit(lbl, (box.x+10, box.y+10))
    draw_center(screen, fonts["small"], "Press Enter to start", 310, GRAY)


def gameover_screen(screen, fonts, score, level, personal_best, mp):
    screen.fill(DARK)
    draw_center(screen, fonts["title"], "GAME OVER", 90, RED)
    draw_center(screen, fonts["sub"], f"Score:        {score}", 190, WHITE)
    draw_center(screen, fonts["sub"], f"Level:        {level}", 230, WHITE)
    draw_center(screen, fonts["sub"], f"Personal Best: {personal_best}", 270, YELLOW)
    btns = {
        "retry": pygame.Rect(W//2-220, 360, 180, 50),
        "menu":  pygame.Rect(W//2+40,  360, 180, 50),
    }
    draw_btn(screen, fonts["btn"], "Retry",     btns["retry"],
             hover=btns["retry"].collidepoint(mp))
    draw_btn(screen, fonts["btn"], "Main Menu", btns["menu"],
             hover=btns["menu"].collidepoint(mp))
    return btns


def leaderboard_screen(screen, fonts, rows, mp):
    screen.fill(DARK)
    draw_center(screen, fonts["title"], "LEADERBOARD", 40, YELLOW)
    hdr = f"{'#':<4}{'Name':<18}{'Score':<10}{'Level':<8}{'Date'}"
    lbl = fonts["small"].render(hdr, True, GRAY)
    screen.blit(lbl, (40, 110))
    pygame.draw.line(screen, GRAY, (40,130),(W-40,130),1)
    for i, row in enumerate(rows):
        name, score, level, date = row
        date_short = date[:10] if date else ""
        line = f"{i+1:<4}{name:<18}{score:<10}{level:<8}{date_short}"
        col  = YELLOW if i == 0 else WHITE
        lbl  = fonts["small"].render(line, True, col)
        screen.blit(lbl, (40, 140 + i*28))
    back = pygame.Rect(W//2-100, H-80, 200, 50)
    draw_btn(screen, fonts["btn"], "Back", back, hover=back.collidepoint(mp))
    return {"back": back}


def settings_screen(screen, fonts, settings, mp):
    screen.fill(DARK)
    draw_center(screen, fonts["title"], "Settings", 40, YELLOW)

    grid_btn  = pygame.Rect(W//2-100, 160, 200, 45)
    sound_btn = pygame.Rect(W//2-100, 225, 200, 45)

    grid_col  = GREEN if settings["grid"]  else DARK
    sound_col = GREEN if settings["sound"] else DARK
    draw_btn(screen, fonts["btn"],
             "Grid: ON" if settings["grid"] else "Grid: OFF",
             grid_btn, color=grid_col, hover=grid_btn.collidepoint(mp))
    draw_btn(screen, fonts["btn"],
             "Sound: ON" if settings["sound"] else "Sound: OFF",
             sound_btn, color=sound_col, hover=sound_btn.collidepoint(mp))

    lbl = fonts["sub"].render("Snake Color:", True, WHITE)
    screen.blit(lbl, (40, 300))

    color_opts = {
        "Green":  [0,200,80],
        "Blue":   [0,120,255],
        "Red":    [220,50,50],
        "White":  [255,255,255],
    }
    color_rects = {}
    for i, (name, col) in enumerate(color_opts.items()):
        r = pygame.Rect(40 + i*130, 335, 120, 40)
        color_rects[name] = (r, col)
        border = YELLOW if settings["snake_color"] == col else WHITE
        pygame.draw.rect(screen, col, r, border_radius=6)
        pygame.draw.rect(screen, border, r, 3, border_radius=6)
        cl = fonts["small"].render(name, True, BLACK)
        screen.blit(cl, (r.centerx-cl.get_width()//2,
                         r.centery-cl.get_height()//2))

    save_back = pygame.Rect(W//2-100, H-90, 200, 50)
    draw_btn(screen, fonts["btn"], "Save & Back", save_back,
             hover=save_back.collidepoint(mp))

    return {"grid": grid_btn, "sound": sound_btn,
            "colors": color_rects, "save_back": save_back}


def main():
    pygame.init()
    screen = pygame.display.set_mode((W, H))
    pygame.display.set_caption("TSIS 4 — Snake")
    clock  = pygame.time.Clock()
    fonts  = make_fonts()

    try:
        init_db()
        db_ok = True
    except Exception as e:
        print(f"DB not available: {e}")
        db_ok = False

    settings     = load_settings()
    state        = MENU
    name_buf     = ""
    username     = ""
    player_id    = None
    personal_best= 0
    game         = None
    buttons      = {}
    tick_acc     = 0

    while True:
        clock.tick(60)
        mp     = pygame.mouse.get_pos()
        events = pygame.event.get()

        for event in events:
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()

            if state == MENU:
                if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
                    if buttons.get("play") and buttons["play"].collidepoint(mp):
                        state    = USERNAME
                        name_buf = ""
                    elif buttons.get("leaderboard") and buttons["leaderboard"].collidepoint(mp):
                        state = LEADER
                    elif buttons.get("settings") and buttons["settings"].collidepoint(mp):
                        state = SETTINGS
                    elif buttons.get("quit") and buttons["quit"].collidepoint(mp):
                        pygame.quit()
                        sys.exit()

            elif state == USERNAME:
                if event.type == pygame.KEYDOWN:
                    if event.key == pygame.K_RETURN and name_buf.strip():
                        username = name_buf.strip()
                        if db_ok:
                            try:
                                player_id     = get_or_create_player(username)
                                personal_best = get_personal_best(player_id)
                            except Exception:
                                player_id     = None
                                personal_best = 0
                        game  = SnakeGame(username, personal_best, settings)
                        state = PLAYING
                        tick_acc = 0
                    elif event.key == pygame.K_BACKSPACE:
                        name_buf = name_buf[:-1]
                    elif event.unicode and len(name_buf) < 16:
                        name_buf += event.unicode

            elif state == PLAYING:
                if event.type == pygame.KEYDOWN:
                    game.handle_key(event.key)

            elif state == GAMEOVER:
                if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
                    if buttons.get("retry") and buttons["retry"].collidepoint(mp):
                        game     = SnakeGame(username, personal_best, settings)
                        state    = PLAYING
                        tick_acc = 0
                    elif buttons.get("menu") and buttons["menu"].collidepoint(mp):
                        state = MENU

            elif state == LEADER:
                if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
                    if buttons.get("back") and buttons["back"].collidepoint(mp):
                        state = MENU

            elif state == SETTINGS:
                if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
                    if buttons.get("grid") and buttons["grid"].collidepoint(mp):
                        settings["grid"] = not settings["grid"]
                    if buttons.get("sound") and buttons["sound"].collidepoint(mp):
                        settings["sound"] = not settings["sound"]
                    for name, (r, col) in (buttons.get("colors") or {}).items():
                        if r.collidepoint(mp):
                            settings["snake_color"] = col
                    if buttons.get("save_back") and buttons["save_back"].collidepoint(mp):
                        save_settings(settings)
                        state = MENU

        if state == PLAYING and game:
            tick_acc += 1
            if tick_acc >= max(1, 60 // game.speed):
                game.update()
                tick_acc = 0
            if not game.alive:
                if db_ok and player_id:
                    try:
                        save_session(player_id, game.score, game.level)
                        personal_best = get_personal_best(player_id)
                    except Exception:
                        pass
                state = GAMEOVER

        if state == MENU:
            buttons = menu_screen(screen, fonts, mp)
        elif state == USERNAME:
            username_screen(screen, fonts, name_buf)
            buttons = {}
        elif state == PLAYING and game:
            game.draw(screen)
            buttons = {}
        elif state == GAMEOVER and game:
            buttons = gameover_screen(screen, fonts,
                                      game.score, game.level,
                                      personal_best, mp)
        elif state == LEADER:
            rows = []
            if db_ok:
                try:
                    rows = get_leaderboard()
                except Exception:
                    pass
            buttons = leaderboard_screen(screen, fonts, rows, mp)
        elif state == SETTINGS:
            buttons = settings_screen(screen, fonts, settings, mp)

        pygame.display.flip()


if __name__ == "__main__":
    main()