import pygame
import sys

pygame.init()

WIDTH, HEIGHT = 900, 650
TOOLBAR_H     = 60
CANVAS_TOP    = TOOLBAR_H
CANVAS_H      = HEIGHT - TOOLBAR_H

screen = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("Paint")
clock  = pygame.time.Clock()

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

font = pygame.font.SysFont("Arial", 16, bold=True)

TOOL_PEN       = "pen"
TOOL_RECTANGLE = "rectangle"
TOOL_CIRCLE    = "circle"
TOOL_ERASER    = "eraser"
TOOLS = [TOOL_PEN, TOOL_RECTANGLE, TOOL_CIRCLE, TOOL_ERASER]
TOOL_LABELS = {"pen": "Pen", "rectangle": "Rect", "circle": "Circle", "eraser": "Eraser"}

BRUSH_SIZES = [3, 6, 12, 20]

def draw_toolbar(surface, tool, color, brush_size, tool_rects,
                 color_rects, size_rects):
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
        cx = rect.centerx
        cy = rect.centery
        radius = min(sz // 2 + 1, rect.width // 2 - 2)
        pygame.draw.circle(surface, color if color != (40, 40, 40) else WHITE, (cx, cy), radius)

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
        tool_rects[t] = pygame.Rect(10 + i * 70, 10, 65, 38)

    for i, c in enumerate(PALETTE):
        color_rects[c] = pygame.Rect(310 + i * 36, 10, 32, 38)

    for i, sz in enumerate(BRUSH_SIZES):
        size_rects[sz] = pygame.Rect(740 + i * 36, 10, 32, 38)

    return tool_rects, color_rects, size_rects

def main():
    canvas = pygame.Surface((WIDTH, CANVAS_H))
    canvas.fill(WHITE)

    tool        = TOOL_PEN
    color       = (0, 0, 0)
    brush_size  = 6
    drawing     = False
    start_pos   = None
    prev_pos    = None

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

                    if tool == TOOL_RECTANGLE:
                        x = min(start_pos[0], end_pos[0])
                        y = min(start_pos[1], end_pos[1])
                        w = abs(end_pos[0] - start_pos[0])
                        h = abs(end_pos[1] - start_pos[1])
                        pygame.draw.rect(canvas, color, (x, y, w, h), brush_size)

                    elif tool == TOOL_CIRCLE:
                        cx = (start_pos[0] + end_pos[0]) // 2
                        cy = (start_pos[1] + end_pos[1]) // 2
                        radius = max(1, int(((end_pos[0] - start_pos[0]) ** 2 +
                                             (end_pos[1] - start_pos[1]) ** 2) ** 0.5 // 2))
                        pygame.draw.circle(canvas, color, (cx, cy), radius, brush_size)

                drawing   = False
                start_pos = None
                prev_pos  = None

        screen.fill((40, 40, 40))
        screen.blit(canvas, (0, CANVAS_TOP))

        if drawing and tool in (TOOL_RECTANGLE, TOOL_CIRCLE):
            mx, my = pygame.mouse.get_pos()
            canvas_y = max(0, my - CANVAS_TOP)
            end_pos  = (mx, canvas_y)

            if tool == TOOL_RECTANGLE and start_pos:
                x = min(start_pos[0], end_pos[0])
                y = min(start_pos[1], end_pos[1]) + CANVAS_TOP
                w = abs(end_pos[0] - start_pos[0])
                h = abs(end_pos[1] - start_pos[1])
                pygame.draw.rect(screen, color, (x, y, w, h), brush_size)

            elif tool == TOOL_CIRCLE and start_pos:
                cx = (start_pos[0] + end_pos[0]) // 2
                cy = (start_pos[1] + end_pos[1]) // 2 + CANVAS_TOP
                radius = max(1, int(((end_pos[0] - start_pos[0]) ** 2 +
                                     (end_pos[1] - start_pos[1]) ** 2) ** 0.5 // 2))
                pygame.draw.circle(screen, color, (cx, cy), radius, brush_size)

        draw_toolbar(screen, tool, color, brush_size,
                     tool_rects, color_rects, size_rects)
        pygame.display.flip()

if __name__ == "__main__":
    main()