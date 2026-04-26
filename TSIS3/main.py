import pygame
import sys
from racer import Game, WIDTH, HEIGHT
from persistence import load_leaderboard, add_score, load_settings, save_settings
from ui import (main_menu_screen, leaderboard_screen, settings_screen,
                gameover_screen, username_screen)

WHITE  = (255, 255, 255)
BLACK  = (0,   0,   0)
YELLOW = (255, 220, 0)

SCREEN_MENU      = "menu"
SCREEN_USERNAME  = "username"
SCREEN_GAME      = "game"
SCREEN_GAMEOVER  = "gameover"
SCREEN_LEADERBOARD = "leaderboard"
SCREEN_SETTINGS  = "settings"


def make_fonts():
    return {
        "title": pygame.font.SysFont("Arial", 52, bold=True),
        "sub":   pygame.font.SysFont("Arial", 28),
        "btn":   pygame.font.SysFont("Arial", 22),
        "small": pygame.font.SysFont("Arial", 18),
    }


def main():
    pygame.init()
    screen  = pygame.display.set_mode((WIDTH, HEIGHT))
    pygame.display.set_caption("TSIS 3 — Racer")
    clock   = pygame.time.Clock()
    fonts   = make_fonts()

    settings   = load_settings()
    screen_st  = SCREEN_MENU
    game       = None
    username   = ""
    name_buf   = ""
    buttons    = {}

    while True:
        clock.tick(60)
        mouse_pos = pygame.mouse.get_pos()
        events    = pygame.event.get()

        for event in events:
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()

            if screen_st == SCREEN_MENU:
                if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
                    if buttons.get("play") and buttons["play"].collidepoint(mouse_pos):
                        screen_st = SCREEN_USERNAME
                        name_buf  = ""
                    elif buttons.get("leaderboard") and buttons["leaderboard"].collidepoint(mouse_pos):
                        screen_st = SCREEN_LEADERBOARD
                    elif buttons.get("settings") and buttons["settings"].collidepoint(mouse_pos):
                        screen_st = SCREEN_SETTINGS
                    elif buttons.get("quit") and buttons["quit"].collidepoint(mouse_pos):
                        pygame.quit()
                        sys.exit()

            elif screen_st == SCREEN_USERNAME:
                if event.type == pygame.KEYDOWN:
                    if event.key == pygame.K_RETURN and name_buf.strip():
                        username  = name_buf.strip()
                        game      = Game(username, settings)
                        screen_st = SCREEN_GAME
                    elif event.key == pygame.K_BACKSPACE:
                        name_buf = name_buf[:-1]
                    elif event.unicode and len(name_buf) < 16:
                        name_buf += event.unicode

            elif screen_st == SCREEN_GAME:
                if event.type == pygame.KEYDOWN:
                    if event.key == pygame.K_LEFT:
                        game.player.move_x = -5
                    elif event.key == pygame.K_RIGHT:
                        game.player.move_x = 5
                if event.type == pygame.KEYUP:
                    if event.key in (pygame.K_LEFT, pygame.K_RIGHT):
                        game.player.move_x = 0

            elif screen_st == SCREEN_GAMEOVER:
                if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
                    if buttons.get("retry") and buttons["retry"].collidepoint(mouse_pos):
                        game      = Game(username, settings)
                        screen_st = SCREEN_GAME
                    elif buttons.get("menu") and buttons["menu"].collidepoint(mouse_pos):
                        screen_st = SCREEN_MENU

            elif screen_st == SCREEN_LEADERBOARD:
                if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
                    if buttons.get("back") and buttons["back"].collidepoint(mouse_pos):
                        screen_st = SCREEN_MENU

            elif screen_st == SCREEN_SETTINGS:
                if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
                    if buttons.get("sound") and buttons["sound"].collidepoint(mouse_pos):
                        settings["sound"] = not settings["sound"]
                        save_settings(settings)
                    for name, r in (buttons.get("colors") or {}).items():
                        if r.collidepoint(mouse_pos):
                            settings["car_color"] = buttons["car_colors"][name]
                            save_settings(settings)
                    for d, r in (buttons.get("diffs") or {}).items():
                        if r.collidepoint(mouse_pos):
                            settings["difficulty"] = d
                            save_settings(settings)
                    if buttons.get("back") and buttons["back"].collidepoint(mouse_pos):
                        screen_st = SCREEN_MENU

        if screen_st == SCREEN_MENU:
            buttons = main_menu_screen(screen, fonts, mouse_pos)

        elif screen_st == SCREEN_USERNAME:
            username_screen(screen, fonts, name_buf)
            buttons = {}

        elif screen_st == SCREEN_GAME:
            if game:
                game.update()
                game.draw(screen)
                if not game.player.alive:
                    add_score(username, game.player.score,
                              game.player.distance)
                    screen_st = SCREEN_GAMEOVER
            buttons = {}

        elif screen_st == SCREEN_GAMEOVER:
            if game:
                buttons = gameover_screen(screen, fonts,
                                          game.player.score,
                                          game.player.distance,
                                          game.player.coins,
                                          mouse_pos)

        elif screen_st == SCREEN_LEADERBOARD:
            entries = load_leaderboard()
            buttons = leaderboard_screen(screen, fonts, entries, mouse_pos)

        elif screen_st == SCREEN_SETTINGS:
            buttons = settings_screen(screen, fonts, settings, mouse_pos)

        pygame.display.flip()


if __name__ == "__main__":
    main()