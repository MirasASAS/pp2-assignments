import pygame
import sys
import math

pygame.init()

WIDTH, HEIGHT = 1000, 680
TOOLBAR_H  = 60
CANVAS_TOP = TOOLBAR_H
CANVAS_H   = HEIGHT - TOOLBAR_H

screen = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("Paint")
clock = pygame.time.Clock()

PALETTE = [
    (0,   0,   0),
    (255, 255, 255),
    (220, 50,  50),
    (50,  180, 50),
    (50,  100, 220),
    (255, 220, 0),
    (255, 140, 0),
    (180, 0,   180),
    (0,   200, 200),
    (139, 69,  19),
    (255, 182, 193),
    (128, 128, 128),
]

TOOLBAR_BG = (40, 40, 40)
TOOL_BG    = (60, 60, 60)
TOOL_SEL   = (100, 150, 255)
WHITE      = (255, 255, 255)
GRAY       = (180, 180, 180)

font      = pygame.font.SysFont("Arial", 13, bold=True)
font_tiny = pygame.font.SysFont("Arial", 11)

TOOL_PEN       = "pen"
TOOL_RECTANGLE = "rectangle"
TOOL_CIRCLE    = "circle"
TOOL_ERASER    = "eraser"
TOOL_SQUARE    = "square"
TOOL_RTRIANGLE = "rtriangle"
TOOL_ETRIANGLE = "etriangle"
TOOL_RHOMBUS   = "rhombus"

TOOLS = [TOOL_PEN, TOOL_RECTANGLE, TOOL_CIRCLE, TOOL_ERASER,
         TOOL_SQUARE, TOOL_RTRIANGLE, TOOL_ETRIANGLE, TOOL_RHOMBUS]

TOOL_LABELS = {
    TOOL_PEN:       "Pen",
    TOOL_RECTANGLE: "Rect",
    TOOL_CIRCLE:    "Circle",
    TOOL_ERASER:    "Eraser",
    TOOL_SQUARE:    "Square",
    TOOL_RTRIANGLE: "R.Tri",
    TOOL_ETRIANGLE: "E.Tri",
    TOOL_RHOMBUS:   "Rhombus",
}

BRUSH_SIZES = [3, 6, 12, 20]

SHAPE_TOOLS = {TOOL_RECTANGLE, TOOL_CIRCLE, TOOL_SQUARE,
               TOOL_RTRIANGLE, TOOL_ETRIANGLE, TOOL_RHOMBUS}


def calc_square(start, end):
    side = min(abs(end[0] - start[0]), abs(end[1] - start[1]))
    sx = start[0] + (side if end[0] > start[0] else -side)
    sy = start[1] + (side if end[1] > start[1] else -side)
    x = min(start[0], sx)
    y = min(start[1], sy)
    return x, y, side, side


def calc_rtriangle(start, end):
    x0, y0 = start
    x1, y1 = end
    return [(x0, y0), (x0, y1), (x1, y1)]


def calc_etriangle(start, end):
    x0, y0 = start
    x1, y1 = end
    base = x1 - x0
    height = abs(base) * math.sqrt(3) / 2
    top_y = y1 - height if y1 > y0 else y1 + height
    mx = (x0 + x1) / 2
    return [(x0, y1), (x1, y1), (mx, top_y)]


def calc_rhombus(start, end):
    x0, y0 = start
    x1, y1 = end
    cx = (x0 + x1) / 2
    cy = (y0 + y1) / 2
    return [(cx, y0), (x1, cy), (cx, y1), (x0, cy)]


def draw_shape_preview(surface, tool, start, end, color, brush_size, offset_y=0):
    pts_offset = lambda pts: [(int(p[0]), int(p[1]) + offset_y) for p in pts]

    if tool == TOOL_RECTANGLE:
        x = min(start[0], end[0])
        y = min(start[1], end[1]) + offset_y
        w = abs(end[0] - start[0])
        h = abs(end[1] - start[1])
        if w > 0 and h > 0:
            pygame.draw.rect(surface, color, (x, y, w, h), brush_size)

    elif tool == TOOL_SQUARE:
        x, y, w, h = calc_square(start, end)
        y += offset_y
        if w > 0:
            pygame.draw.rect(surface, color, (x, y, w, h), brush_size)

    elif tool == TOOL_CIRCLE:
        cx = (start[0] + end[0]) // 2
        cy = int((start[1] + end[1]) / 2) + offset_y
        radius = max(1, int(math.hypot(end[0] - start[0], end[1] - start[1]) // 2))
        pygame.draw.circle(surface, color, (cx, cy), radius, brush_size)

    elif tool == TOOL_RTRIANGLE:
        pts = pts_offset(calc_rtriangle(start, end))
        if len(set(pts)) == 3:
            pygame.draw.polygon(surface, color, pts, brush_size)

    elif tool == TOOL_ETRIANGLE:
        pts = pts_offset(calc_etriangle(start, end))
        if len(set(pts)) == 3:
            pygame.draw.polygon(surface, color, pts, brush_size)

    elif tool == TOOL_RHOMBUS:
        pts = pts_offset(calc_rhombus(start, end))
        pygame.draw.polygon(surface, color, pts, brush_size)


def draw_shape_to_canvas(canvas, tool, start, end, color, brush_size):
    if tool == TOOL_RECTANGLE:
        x = min(start[0], end[0])
        y = min(start[1], end[1])
        w = abs(end[0] - start[0])
        h = abs(end[1] - start[1])
        if w > 0 and h > 0:
            pygame.draw.rect(canvas, color, (x, y, w, h), brush_size)

    elif tool == TOOL_SQUARE:
        x, y, w, h = calc_square(start, end)
        if w > 0:
            pygame.draw.rect(canvas, color, (x, y, w, h), brush_size)

    elif tool == TOOL_CIRCLE:
        cx = (start[0] + end[0]) // 2
        cy = (start[1] + end[1]) // 2
        radius = max(1, int(math.hypot(end[0] - start[0], end[1] - start[1]) // 2))
        pygame.draw.circle(canvas, color, (cx, cy), radius, brush_size)

    elif tool == TOOL_RTRIANGLE:
        pts = [(int(p[0]), int(p[1])) for p in calc_rtriangle(start, end)]
        if len(set(pts)) == 3:
            pygame.draw.polygon(canvas, color, pts, brush_size)

    elif tool == TOOL_ETRIANGLE:
        pts = [(int(p[0]), int(p[1])) for p in calc_etriangle(start, end)]
        if len(set(pts)) == 3:
            pygame.draw.polygon(canvas, color, pts, brush_size)

    elif tool == TOOL_RHOMBUS:
        pts = [(int(p[0]), int(p[1])) for p in calc_rhombus(start, end)]
        pygame.draw.polygon(canvas, color, pts, brush_size)


def draw_toolbar(surface, tool, color, brush_size, tool_rects, color_rects, size_rects):
    pygame.draw.rect(surface, TOOLBAR_BG, (0, 0, WIDTH, TOOLBAR_H))

    for t, rect in tool_rects.items():
        bg = TOOL_SEL if t == tool else TOOL_BG
        pygame.draw.rect(surface, bg, rect, border_radius=5)
        pygame.draw.rect(surface, GRAY, rect, 1, border_radius=5)
        label = font.render(TOOL_LABELS[t], True, WHITE)
        surface.blit(label, (rect.x + rect.width // 2 - label.get_width() // 2,
                              rect.y + rect.height // 2 - label.get_height() // 2))

    for c, rect in color_rects.items():
        pygame.draw.rect(surface, c, rect, border_radius=4)
        if c == color:
            pygame.draw.rect(surface, WHITE, rect, 3, border_radius=4)
        else:
            pygame.draw.rect(surface, (80, 80, 80), rect, 1, border_radius=4)

    for sz, rect in size_rects.items():
        bg = TOOL_SEL if sz == brush_size else TOOL_BG
        pygame.draw.rect(surface, bg, rect, border_radius=4)
        r = min(sz // 2 + 1, rect.width // 2 - 2)
        draw_c = color if color != (40, 40, 40) else WHITE
        pygame.draw.circle(surface, draw_c, rect.center, r)

    clear_rect = pygame.Rect(WIDTH - 70, 10, 60, 38)
    pygame.draw.rect(surface, (180, 50, 50), clear_rect, border_radius=5)
    cl = font.render("Clear", True, WHITE)
    surface.blit(cl, (clear_rect.x + clear_rect.width // 2 - cl.get_width() // 2,
                       clear_rect.y + clear_rect.height // 2 - cl.get_height() // 2))
    return clear_rect


def build_layout():
    tool_rects  = {}
    color_rects = {}
    size_rects  = {}

    for i, t in enumerate(TOOLS):
        tool_rects[t] = pygame.Rect(5 + i * 74, 8, 70, 42)

    palette_x = 5 + len(TOOLS) * 74 + 10
    for i, c in enumerate(PALETTE):
        color_rects[c] = pygame.Rect(palette_x + i * 34, 10, 30, 38)

    size_x = palette_x + len(PALETTE) * 34 + 6
    for i, sz in enumerate(BRUSH_SIZES):
        size_rects[sz] = pygame.Rect(size_x + i * 34, 10, 30, 38)

    return tool_rects, color_rects, size_rects


def main():
    canvas = pygame.Surface((WIDTH, CANVAS_H))
    canvas.fill(WHITE)

    tool       = TOOL_PEN
    color      = (0, 0, 0)
    brush_size = 6
    drawing    = False
    start_pos  = None
    prev_pos   = None

    tool_rects, color_rects, size_rects = build_layout()

    while True:
        clock.tick(60)

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit(); sys.exit()

            if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
                mx, my = event.pos

                if my < TOOLBAR_H:
                    for t, rect in tool_rects.items():
                        if rect.collidepoint(mx, my):
                            tool = t
                    for c, rect in color_rects.items():
                        if rect.collidepoint(mx, my):
                            color = c
                    for sz, rect in size_rects.items():
                        if rect.collidepoint(mx, my):
                            brush_size = sz
                    clear_rect = pygame.Rect(WIDTH - 70, 10, 60, 38)
                    if clear_rect.collidepoint(mx, my):
                        canvas.fill(WHITE)
                else:
                    drawing   = True
                    canvas_y  = my - CANVAS_TOP
                    start_pos = (mx, canvas_y)
                    prev_pos  = (mx, canvas_y)
                    if tool in (TOOL_PEN, TOOL_ERASER):
                        draw_color = WHITE if tool == TOOL_ERASER else color
                        sz = brush_size * 3 if tool == TOOL_ERASER else brush_size
                        pygame.draw.circle(canvas, draw_color, (mx, canvas_y), sz)

            if event.type == pygame.MOUSEMOTION and drawing:
                mx, my = event.pos
                if my >= CANVAS_TOP:
                    canvas_y = my - CANVAS_TOP
                    if tool == TOOL_PEN and prev_pos:
                        pygame.draw.line(canvas, color, prev_pos,
                                         (mx, canvas_y), brush_size * 2)
                        prev_pos = (mx, canvas_y)
                    elif tool == TOOL_ERASER and prev_pos:
                        pygame.draw.line(canvas, WHITE, prev_pos,
                                         (mx, canvas_y), brush_size * 6)
                        prev_pos = (mx, canvas_y)

            if event.type == pygame.MOUSEBUTTONUP and event.button == 1:
                if drawing and start_pos:
                    mx, my = event.pos
                    canvas_y = max(0, my - CANVAS_TOP)
                    end_pos  = (mx, canvas_y)
                    if tool in SHAPE_TOOLS:
                        draw_shape_to_canvas(canvas, tool, start_pos, end_pos,
                                             color, brush_size)
                drawing   = False
                start_pos = None
                prev_pos  = None

        screen.fill((40, 40, 40))
        screen.blit(canvas, (0, CANVAS_TOP))

        if drawing and tool in SHAPE_TOOLS and start_pos:
            mx, my = pygame.mouse.get_pos()
            canvas_y = max(0, my - CANVAS_TOP)
            end_pos  = (mx, canvas_y)
            draw_shape_preview(screen, tool, start_pos, end_pos,
                               color, brush_size, offset_y=CANVAS_TOP)

        draw_toolbar(screen, tool, color, brush_size,
                     tool_rects, color_rects, size_rects)
        pygame.display.flip()


if __name__ == "__main__":
    main()