import pygame
import sys
import math
from datetime import datetime
from tools import (
    PENCIL, LINE, RECTANGLE, CIRCLE, SQUARE,
    RTRIANGLE, ETRIANGLE, RHOMBUS, ERASER, FILL, TEXT,
    BRUSH_SIZES, flood_fill
)

WIDTH, HEIGHT = 1100, 700
TOOLBAR_H     = 60
CANVAS_TOP    = TOOLBAR_H
WHITE         = (255, 255, 255)
BLACK         = (0,   0,   0)
GRAY          = (200, 200, 200)
DARK          = (50,  50,  50)
HIGHLIGHT     = (100, 149, 237)

COLORS = [
    (0,0,0),(255,255,255),(255,0,0),(0,255,0),(0,0,255),
    (255,255,0),(255,165,0),(128,0,128),(0,255,255),(165,42,42),
    (255,192,203),(128,128,128),
]

TOOLS = [
    PENCIL, LINE, RECTANGLE, CIRCLE, SQUARE,
    RTRIANGLE, ETRIANGLE, RHOMBUS, ERASER, FILL, TEXT,
]

TOOL_LABELS = {
    PENCIL:"Pencil", LINE:"Line", RECTANGLE:"Rect",
    CIRCLE:"Circle", SQUARE:"Square", RTRIANGLE:"RTri",
    ETRIANGLE:"ETri", RHOMBUS:"Rhomb", ERASER:"Erase",
    FILL:"Fill", TEXT:"Text",
}


def draw_equilateral_triangle(surface, color, start, end, width):
    x1, y1 = start
    x2, y2 = end
    dx, dy  = x2 - x1, y2 - y1
    length  = math.hypot(dx, dy)
    if length == 0:
        return
    height_t = math.sqrt(3) / 2 * length
    mx = (x1 + x2) / 2
    my = (y1 + y2) / 2
    perp_x = -dy / length
    perp_y =  dx / length
    apex = (int(mx + perp_x * height_t), int(my + perp_y * height_t))
    pts  = [start, end, apex]
    pygame.draw.polygon(surface, color, pts, width)


def draw_rhombus(surface, color, start, end, width):
    x1, y1 = start
    x2, y2 = end
    cx = (x1 + x2) // 2
    cy = (y1 + y2) // 2
    pts = [(cx, y1), (x2, cy), (cx, y2), (x1, cy)]
    pygame.draw.polygon(surface, color, pts, width)


def draw_right_triangle(surface, color, start, end, width):
    x1, y1 = start
    x2, y2 = end
    pts = [start, (x1, y2), end]
    pygame.draw.polygon(surface, color, pts, width)


def draw_shape(surface, tool, color, start, end, brush):
    x1, y1 = start
    x2, y2 = end
    if tool == RECTANGLE:
        rect = pygame.Rect(min(x1,x2), min(y1,y2), abs(x2-x1), abs(y2-y1))
        pygame.draw.rect(surface, color, rect, brush)
    elif tool == CIRCLE:
        cx = (x1 + x2) // 2
        cy = (y1 + y2) // 2
        r  = int(math.hypot(x2-x1, y2-y1) // 2)
        pygame.draw.circle(surface, color, (cx, cy), r, brush)
    elif tool == SQUARE:
        side = min(abs(x2-x1), abs(y2-y1))
        sx = x1 if x2 > x1 else x1 - side
        sy = y1 if y2 > y1 else y1 - side
        pygame.draw.rect(surface, color, pygame.Rect(sx, sy, side, side), brush)
    elif tool == RTRIANGLE:
        draw_right_triangle(surface, color, start, end, brush)
    elif tool == ETRIANGLE:
        draw_equilateral_triangle(surface, color, start, end, brush)
    elif tool == RHOMBUS:
        draw_rhombus(surface, color, start, end, brush)
    elif tool == LINE:
        pygame.draw.line(surface, color, start, end, brush)


def main():
    pygame.init()
    screen  = pygame.display.set_mode((WIDTH, HEIGHT))
    pygame.display.set_caption("TSIS 2 — Paint")

    canvas  = pygame.Surface((WIDTH, HEIGHT - CANVAS_TOP))
    canvas.fill(WHITE)

    font_small = pygame.font.SysFont("Arial", 13)
    font_text  = pygame.font.SysFont("Arial", 24)

    current_tool  = PENCIL
    current_color = BLACK
    brush_level   = 1
    drawing       = False
    start_pos     = None
    prev_pos      = None
    preview_surf  = None

    text_mode     = False
    text_pos      = None
    text_buffer   = ""

    clock = pygame.time.Clock()

    def brush_size():
        return BRUSH_SIZES[brush_level]

    tool_btn_w = 52
    tool_btn_h = 28
    tool_rects = {}
    for i, t in enumerate(TOOLS):
        x = 5 + i * (tool_btn_w + 3)
        tool_rects[t] = pygame.Rect(x, 4, tool_btn_w, tool_btn_h)

    size_rects = {}
    bx_start = 5 + len(TOOLS) * (tool_btn_w + 3) + 10
    for lvl in (1, 2, 3):
        size_rects[lvl] = pygame.Rect(bx_start + (lvl-1)*34, 4, 30, tool_btn_h)

    swatch_size = 22
    color_rects = []
    for i, c in enumerate(COLORS):
        color_rects.append((pygame.Rect(5 + i*(swatch_size+3), 35, swatch_size, swatch_size), c))

    def draw_toolbar():
        pygame.draw.rect(screen, GRAY, (0, 0, WIDTH, TOOLBAR_H))
        for t, r in tool_rects.items():
            col = HIGHLIGHT if t == current_tool else DARK
            pygame.draw.rect(screen, col, r, border_radius=4)
            lbl = font_small.render(TOOL_LABELS[t], True, WHITE)
            screen.blit(lbl, (r.x + 3, r.y + 7))
        labels = {1:"S", 2:"M", 3:"L"}
        for lvl, r in size_rects.items():
            col = HIGHLIGHT if lvl == brush_level else DARK
            pygame.draw.rect(screen, col, r, border_radius=4)
            lbl = font_small.render(labels[lvl], True, WHITE)
            screen.blit(lbl, (r.x + 10, r.y + 7))
        for r, c in color_rects:
            pygame.draw.rect(screen, c, r)
            if c == current_color:
                pygame.draw.rect(screen, HIGHLIGHT, r, 3)
            else:
                pygame.draw.rect(screen, DARK, r, 1)
        px = 5 + len(COLORS)*(swatch_size+3) + 10
        pygame.draw.rect(screen, current_color, pygame.Rect(px, 35, 40, swatch_size))
        pygame.draw.rect(screen, DARK, pygame.Rect(px, 35, 40, swatch_size), 2)

    running = True
    while running:
        clock.tick(60)

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False

            elif event.type == pygame.KEYDOWN:
                if text_mode:
                    if event.key == pygame.K_RETURN:
                        if text_buffer:
                            surf = font_text.render(text_buffer, True, current_color)
                            canvas.blit(surf, (text_pos[0], text_pos[1] - CANVAS_TOP))
                        text_mode   = False
                        text_buffer = ""
                        text_pos    = None
                    elif event.key == pygame.K_ESCAPE:
                        text_mode   = False
                        text_buffer = ""
                        text_pos    = None
                    elif event.key == pygame.K_BACKSPACE:
                        text_buffer = text_buffer[:-1]
                    else:
                        if event.unicode:
                            text_buffer += event.unicode
                else:
                    if event.key == pygame.K_1:
                        brush_level = 1
                    elif event.key == pygame.K_2:
                        brush_level = 2
                    elif event.key == pygame.K_3:
                        brush_level = 3
                    elif event.key == pygame.K_s and (pygame.key.get_mods() & pygame.KMOD_CTRL):
                        ts       = datetime.now().strftime("%Y%m%d_%H%M%S")
                        filename = f"canvas_{ts}.png"
                        pygame.image.save(canvas, filename)
                        pygame.display.set_caption(f"Saved: {filename}")

            elif event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
                mx, my = event.pos
                if my < TOOLBAR_H:
                    for t, r in tool_rects.items():
                        if r.collidepoint(mx, my):
                            current_tool = t
                            text_mode = False
                    for lvl, r in size_rects.items():
                        if r.collidepoint(mx, my):
                            brush_level = lvl
                    for r, c in color_rects:
                        if r.collidepoint(mx, my):
                            current_color = c
                    continue

                cy_pos = my - CANVAS_TOP
                if cy_pos < 0:
                    continue

                if current_tool == FILL:
                    flood_fill(canvas, mx, cy_pos, current_color)
                elif current_tool == TEXT:
                    text_mode   = True
                    text_pos    = (mx, my)
                    text_buffer = ""
                else:
                    drawing   = True
                    start_pos = (mx, cy_pos)
                    prev_pos  = (mx, cy_pos)
                    preview_surf = canvas.copy()

            elif event.type == pygame.MOUSEMOTION:
                if not drawing:
                    continue
                mx, my   = event.pos
                cy_pos   = my - CANVAS_TOP
                cur_pos  = (mx, cy_pos)

                if current_tool == PENCIL:
                    if prev_pos:
                        pygame.draw.line(canvas, current_color,
                                         prev_pos, cur_pos, brush_size())
                    prev_pos = cur_pos
                elif current_tool == ERASER:
                    r = brush_size() * 3
                    pygame.draw.circle(canvas, WHITE, cur_pos, r)
                    prev_pos = cur_pos
                elif current_tool in (LINE, RECTANGLE, CIRCLE,
                                      SQUARE, RTRIANGLE, ETRIANGLE, RHOMBUS):
                    preview_surf = canvas.copy()

            elif event.type == pygame.MOUSEBUTTONUP and event.button == 1:
                if not drawing:
                    continue
                mx, my  = event.pos
                cy_pos  = my - CANVAS_TOP
                end_pos = (mx, cy_pos)

                if current_tool in (LINE, RECTANGLE, CIRCLE,
                                    SQUARE, RTRIANGLE, ETRIANGLE, RHOMBUS):
                    draw_shape(canvas, current_tool, current_color,
                               start_pos, end_pos, brush_size())

                drawing      = False
                start_pos    = None
                prev_pos     = None
                preview_surf = None

        screen.fill(GRAY)

        if drawing and preview_surf and current_tool in (
                LINE, RECTANGLE, CIRCLE, SQUARE, RTRIANGLE, ETRIANGLE, RHOMBUS):
            tmp = preview_surf.copy()
            mx2, my2 = pygame.mouse.get_pos()
            draw_shape(tmp, current_tool, current_color,
                       start_pos, (mx2, my2 - CANVAS_TOP), brush_size())
            screen.blit(tmp, (0, CANVAS_TOP))
        else:
            screen.blit(canvas, (0, CANVAS_TOP))

        if text_mode and text_pos:
            preview = font_text.render(text_buffer + "|", True, current_color)
            screen.blit(preview, (text_pos[0], text_pos[1]))

        draw_toolbar()

        hint = font_small.render("1/2/3=brush size  Ctrl+S=save", True, DARK)
        screen.blit(hint, (5, HEIGHT - 18))

        pygame.display.flip()

    pygame.quit()
    sys.exit()


if __name__ == "__main__":
    main()