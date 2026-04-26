PENCIL    = "pencil"
LINE      = "line"
RECTANGLE = "rectangle"
CIRCLE    = "circle"
SQUARE    = "square"
RTRIANGLE = "right_triangle"
ETRIANGLE = "equilateral_triangle"
RHOMBUS   = "rhombus"
ERASER    = "eraser"
FILL      = "fill"
TEXT      = "text"

BRUSH_SIZES = {1: 2, 2: 5, 3: 10}


def flood_fill(surface, x, y, new_color):
    width, height = surface.get_size()
    if x < 0 or y < 0 or x >= width or y >= height:
        return

    target_color = surface.get_at((x, y))[:3]
    new_color_3  = new_color[:3]

    if target_color == new_color_3:
        return

    stack   = [(x, y)]
    visited = set()

    while stack:
        cx, cy = stack.pop()
        if (cx, cy) in visited:
            continue
        if cx < 0 or cy < 0 or cx >= width or cy >= height:
            continue
        if surface.get_at((cx, cy))[:3] != target_color:
            continue

        surface.set_at((cx, cy), new_color_3)
        visited.add((cx, cy))

        stack.append((cx + 1, cy))
        stack.append((cx - 1, cy))
        stack.append((cx, cy + 1))
        stack.append((cx, cy - 1))