#!/usr/bin/env python3
"""Generate sprite.png for Plumber Runner — original "Bolt" explorer character.

Produces a sprite sheet with 8 frames in a single row, each 28x36 pixels.
Frame layout: idle, run0, run1, run2, run3, jump_up, fall, land

All pixel art is original — NOT derived from any Nintendo or copyrighted IP.
"""

from PIL import Image, ImageDraw

FRAME_W = 28
FRAME_H = 36
FRAMES = 8  # idle, run0-3, jump_up, fall, land

# Color palette — matches the in-game "Bolt" explorer
COLORS = {
    'hair':     (45, 27, 105),
    'hair_hi':  (91, 63, 191),
    'skin':     (240, 192, 144),
    'skin_sh':  (200, 144, 96),
    'visor':    (0, 229, 255),
    'visor_d':  (0, 151, 167),
    'jacket':   (216, 67, 21),
    'jack_hi':  (255, 112, 67),
    'jack_sh':  (191, 54, 12),
    'cargo':    (55, 71, 79),
    'cargo_l':  (96, 125, 139),
    'boots':    (78, 52, 46),
    'boots_h':  (109, 76, 65),
    'buckle':   (255, 214, 0),
    'mouth':    (230, 74, 25),
    'pack':     (84, 110, 122),
    'pack_lt':  (120, 144, 156),
    'vent':     (255, 109, 0),
    'eye_white':(255, 255, 255),
    'trans':    (0, 0, 0, 0),
}

def px(draw, fx, x, y, w, h, color_name):
    """Draw a pixel rect at (fx*FRAME_W + x, y) with size (w, h)."""
    c = COLORS[color_name]
    ox = fx * FRAME_W
    draw.rectangle([ox + x, y, ox + x + w - 1, y + h - 1], fill=c)

def draw_head(draw, fx, head_y, hair_style='normal'):
    """Draw the head (hair + face + visor) at given Y offset."""
    # Hair base
    px(draw, fx, 8, head_y, 14, 4, 'hair')
    # Hair spikes
    if hair_style == 'normal':
        px(draw, fx, 8, head_y - 3, 3, 3, 'hair')
        px(draw, fx, 13, head_y - 4, 3, 4, 'hair')
        px(draw, fx, 18, head_y - 2, 3, 2, 'hair')
        px(draw, fx, 10, head_y - 2, 2, 2, 'hair_hi')
        px(draw, fx, 15, head_y - 3, 2, 3, 'hair_hi')
    elif hair_style == 'wind_up':
        px(draw, fx, 8, head_y - 5, 3, 5, 'hair')
        px(draw, fx, 13, head_y - 6, 3, 6, 'hair')
        px(draw, fx, 18, head_y - 4, 3, 4, 'hair')
        px(draw, fx, 10, head_y - 4, 2, 4, 'hair_hi')
        px(draw, fx, 15, head_y - 5, 2, 5, 'hair_hi')
    elif hair_style == 'flat':
        px(draw, fx, 8, head_y - 1, 3, 1, 'hair')
        px(draw, fx, 13, head_y - 2, 3, 2, 'hair')
        px(draw, fx, 18, head_y - 1, 3, 1, 'hair')
        px(draw, fx, 10, head_y - 1, 2, 1, 'hair_hi')
        px(draw, fx, 15, head_y - 1, 2, 1, 'hair_hi')
    elif hair_style == 'squash':
        px(draw, fx, 6, head_y - 1, 4, 1, 'hair')
        px(draw, fx, 12, head_y - 2, 4, 2, 'hair')
        px(draw, fx, 18, head_y - 1, 4, 1, 'hair')
        px(draw, fx, 10, head_y - 1, 2, 1, 'hair_hi')

    # Face
    px(draw, fx, 8, head_y + 4, 14, 6, 'skin')
    px(draw, fx, 8, head_y + 4, 2, 6, 'skin_sh')  # shadow

    # Visor
    px(draw, fx, 10, head_y + 5, 10, 3, 'visor_d')
    px(draw, fx, 11, head_y + 5, 8, 2, 'visor')

    return head_y + 10  # return Y after head


def draw_body_idle(draw, fx):
    """Idle stance — relaxed, arms at sides."""
    head_y = 4
    body_top = draw_head(draw, fx, head_y, 'normal')

    # Mouth
    px(draw, fx, 14, head_y + 8, 4, 1, 'mouth')

    # Jacket (torso)
    px(draw, fx, 6, body_top, 16, 10, 'jacket')
    px(draw, fx, 7, body_top, 2, 10, 'jack_hi')  # highlight
    px(draw, fx, 19, body_top, 3, 10, 'jack_sh')  # shadow

    # Buckle
    px(draw, fx, 12, body_top + 8, 4, 2, 'buckle')

    # Jetpack on back
    px(draw, fx, 3, body_top + 1, 4, 7, 'pack')
    px(draw, fx, 4, body_top + 2, 2, 3, 'pack_lt')

    # Arms at sides
    px(draw, fx, 3, body_top + 2, 3, 6, 'jacket')
    px(draw, fx, 22, body_top + 2, 3, 6, 'jacket')
    # Hands
    px(draw, fx, 3, body_top + 7, 3, 2, 'skin')
    px(draw, fx, 22, body_top + 7, 3, 2, 'skin')

    # Cargo pants
    legs_y = body_top + 10
    px(draw, fx, 8, legs_y, 6, 8, 'cargo')
    px(draw, fx, 10, legs_y + 2, 2, 2, 'cargo_l')
    px(draw, fx, 14, legs_y, 6, 8, 'cargo')
    px(draw, fx, 16, legs_y + 2, 2, 2, 'cargo_l')

    # Boots
    px(draw, fx, 6, legs_y + 8, 8, 4, 'boots')
    px(draw, fx, 7, legs_y + 8, 3, 1, 'boots_h')
    px(draw, fx, 14, legs_y + 8, 8, 4, 'boots')
    px(draw, fx, 15, legs_y + 8, 3, 1, 'boots_h')


def draw_body_run(draw, fx, phase):
    """Run cycle — 4 phases with alternating arms/legs."""
    head_y = 3 + (1 if phase in (0, 2) else 0)  # bob
    body_top = draw_head(draw, fx, head_y, 'normal')

    # Determined mouth
    px(draw, fx, 14, head_y + 8, 4, 1, 'mouth')

    # Jacket
    px(draw, fx, 6, body_top, 16, 10, 'jacket')
    px(draw, fx, 7, body_top, 2, 10, 'jack_hi')
    px(draw, fx, 19, body_top, 3, 10, 'jack_sh')
    px(draw, fx, 12, body_top + 8, 4, 2, 'buckle')

    # Jetpack
    px(draw, fx, 3, body_top + 1, 4, 7, 'pack')
    px(draw, fx, 4, body_top + 2, 2, 3, 'pack_lt')

    legs_y = body_top + 10

    if phase == 0:
        # Left arm forward, right back
        px(draw, fx, 22, body_top + 1, 4, 5, 'jacket')
        px(draw, fx, 23, body_top + 5, 3, 2, 'skin')
        px(draw, fx, 2, body_top + 4, 4, 5, 'jacket')
        px(draw, fx, 2, body_top + 8, 3, 2, 'skin')
        # Left leg forward, right back
        px(draw, fx, 6, legs_y, 6, 8, 'cargo')
        px(draw, fx, 8, legs_y + 2, 2, 2, 'cargo_l')
        px(draw, fx, 16, legs_y + 2, 5, 6, 'cargo')
        px(draw, fx, 4, legs_y + 8, 8, 4, 'boots')
        px(draw, fx, 5, legs_y + 8, 3, 1, 'boots_h')
        px(draw, fx, 16, legs_y + 8, 6, 4, 'boots')
    elif phase == 1:
        # Arms neutral, legs together (contact)
        px(draw, fx, 3, body_top + 2, 3, 6, 'jacket')
        px(draw, fx, 22, body_top + 2, 3, 6, 'jacket')
        px(draw, fx, 3, body_top + 7, 3, 2, 'skin')
        px(draw, fx, 22, body_top + 7, 3, 2, 'skin')
        px(draw, fx, 9, legs_y, 5, 8, 'cargo')
        px(draw, fx, 11, legs_y + 2, 2, 2, 'cargo_l')
        px(draw, fx, 14, legs_y, 5, 8, 'cargo')
        px(draw, fx, 8, legs_y + 8, 6, 4, 'boots')
        px(draw, fx, 9, legs_y + 8, 3, 1, 'boots_h')
        px(draw, fx, 14, legs_y + 8, 6, 4, 'boots')
    elif phase == 2:
        # Right arm forward, left back (mirror of phase 0)
        px(draw, fx, 2, body_top + 1, 4, 5, 'jacket')
        px(draw, fx, 2, body_top + 5, 3, 2, 'skin')
        px(draw, fx, 22, body_top + 4, 4, 5, 'jacket')
        px(draw, fx, 23, body_top + 8, 3, 2, 'skin')
        # Right leg forward, left back
        px(draw, fx, 14, legs_y, 6, 8, 'cargo')
        px(draw, fx, 16, legs_y + 2, 2, 2, 'cargo_l')
        px(draw, fx, 6, legs_y + 2, 5, 6, 'cargo')
        px(draw, fx, 14, legs_y + 8, 8, 4, 'boots')
        px(draw, fx, 15, legs_y + 8, 3, 1, 'boots_h')
        px(draw, fx, 6, legs_y + 8, 6, 4, 'boots')
    else:  # phase 3
        # Arms half, legs close
        px(draw, fx, 3, body_top + 3, 3, 5, 'jacket')
        px(draw, fx, 3, body_top + 7, 3, 2, 'skin')
        px(draw, fx, 22, body_top + 3, 3, 5, 'jacket')
        px(draw, fx, 22, body_top + 7, 3, 2, 'skin')
        px(draw, fx, 8, legs_y, 6, 8, 'cargo')
        px(draw, fx, 10, legs_y + 2, 2, 2, 'cargo_l')
        px(draw, fx, 14, legs_y, 6, 8, 'cargo')
        px(draw, fx, 16, legs_y + 2, 2, 2, 'cargo_l')
        px(draw, fx, 7, legs_y + 8, 7, 4, 'boots')
        px(draw, fx, 8, legs_y + 8, 3, 1, 'boots_h')
        px(draw, fx, 14, legs_y + 8, 7, 4, 'boots')
        px(draw, fx, 15, legs_y + 8, 3, 1, 'boots_h')


def draw_body_jump_up(draw, fx):
    """Jump up — arms raised, legs tucked, hair streaming up."""
    head_y = 2
    body_top = draw_head(draw, fx, head_y, 'wind_up')

    # Excited mouth
    px(draw, fx, 14, head_y + 8, 3, 2, 'mouth')

    # Jacket
    px(draw, fx, 6, body_top, 16, 10, 'jacket')
    px(draw, fx, 7, body_top, 2, 10, 'jack_hi')
    px(draw, fx, 19, body_top, 3, 10, 'jack_sh')
    px(draw, fx, 12, body_top + 8, 4, 2, 'buckle')

    # Jetpack with thrust
    px(draw, fx, 3, body_top + 1, 4, 7, 'pack')
    px(draw, fx, 4, body_top + 2, 2, 3, 'pack_lt')
    px(draw, fx, 3, body_top + 8, 4, 3, 'vent')  # thrust glow

    # Arms raised up
    px(draw, fx, 2, body_top - 3, 4, 6, 'jacket')
    px(draw, fx, 2, body_top - 4, 3, 2, 'skin')
    px(draw, fx, 22, body_top - 3, 4, 6, 'jacket')
    px(draw, fx, 23, body_top - 4, 3, 2, 'skin')

    # Legs tucked up
    legs_y = body_top + 10
    px(draw, fx, 8, legs_y, 5, 6, 'cargo')
    px(draw, fx, 15, legs_y, 5, 6, 'cargo')
    px(draw, fx, 8, legs_y + 6, 5, 3, 'boots')
    px(draw, fx, 15, legs_y + 6, 5, 3, 'boots')


def draw_body_fall(draw, fx):
    """Falling — arms spread, legs dangling, worried face."""
    head_y = 4
    body_top = draw_head(draw, fx, head_y, 'flat')

    # Worried O mouth
    px(draw, fx, 15, head_y + 7, 3, 3, 'mouth')
    px(draw, fx, 16, head_y + 8, 1, 1, 'skin')  # O hole

    # Jacket
    px(draw, fx, 6, body_top, 16, 10, 'jacket')
    px(draw, fx, 7, body_top, 2, 10, 'jack_hi')
    px(draw, fx, 19, body_top, 3, 10, 'jack_sh')
    px(draw, fx, 12, body_top + 8, 4, 2, 'buckle')

    # Jetpack (no thrust)
    px(draw, fx, 3, body_top + 1, 4, 7, 'pack')
    px(draw, fx, 4, body_top + 2, 2, 3, 'pack_lt')

    # Arms spread wide
    px(draw, fx, 0, body_top + 2, 6, 4, 'jacket')
    px(draw, fx, 0, body_top + 5, 3, 2, 'skin')
    px(draw, fx, 22, body_top + 2, 6, 4, 'jacket')
    px(draw, fx, 25, body_top + 5, 3, 2, 'skin')

    # Legs dangling apart
    legs_y = body_top + 10
    px(draw, fx, 6, legs_y, 6, 8, 'cargo')
    px(draw, fx, 8, legs_y + 2, 2, 2, 'cargo_l')
    px(draw, fx, 16, legs_y, 6, 8, 'cargo')
    px(draw, fx, 18, legs_y + 2, 2, 2, 'cargo_l')
    px(draw, fx, 5, legs_y + 8, 7, 4, 'boots')
    px(draw, fx, 6, legs_y + 8, 3, 1, 'boots_h')
    px(draw, fx, 16, legs_y + 8, 7, 4, 'boots')
    px(draw, fx, 17, legs_y + 8, 3, 1, 'boots_h')


def draw_body_land(draw, fx):
    """Landing squash — compressed body, wide stance."""
    head_y = 6  # lower due to squash
    body_top = draw_head(draw, fx, head_y, 'squash')

    # Strained mouth
    px(draw, fx, 13, head_y + 8, 5, 1, 'mouth')

    # Squashed jacket (wider, shorter)
    px(draw, fx, 4, body_top, 20, 8, 'jacket')
    px(draw, fx, 5, body_top, 2, 8, 'jack_hi')
    px(draw, fx, 21, body_top, 3, 8, 'jack_sh')
    px(draw, fx, 12, body_top + 6, 4, 2, 'buckle')

    # Jetpack
    px(draw, fx, 1, body_top + 1, 4, 6, 'pack')
    px(draw, fx, 2, body_top + 2, 2, 3, 'pack_lt')

    # Arms bracing
    px(draw, fx, 1, body_top + 2, 3, 5, 'jacket')
    px(draw, fx, 1, body_top + 6, 3, 2, 'skin')
    px(draw, fx, 24, body_top + 2, 3, 5, 'jacket')
    px(draw, fx, 24, body_top + 6, 3, 2, 'skin')

    # Wide stance legs
    legs_y = body_top + 8
    px(draw, fx, 4, legs_y, 7, 6, 'cargo')
    px(draw, fx, 6, legs_y + 1, 2, 2, 'cargo_l')
    px(draw, fx, 17, legs_y, 7, 6, 'cargo')
    px(draw, fx, 19, legs_y + 1, 2, 2, 'cargo_l')

    # Wide boots
    px(draw, fx, 2, legs_y + 6, 9, 4, 'boots')
    px(draw, fx, 3, legs_y + 6, 3, 1, 'boots_h')
    px(draw, fx, 17, legs_y + 6, 9, 4, 'boots')
    px(draw, fx, 18, legs_y + 6, 3, 1, 'boots_h')


def main():
    img = Image.new('RGBA', (FRAME_W * FRAMES, FRAME_H), (0, 0, 0, 0))
    draw = ImageDraw.Draw(img)

    # Frame 0: idle
    draw_body_idle(draw, 0)

    # Frames 1-4: run cycle (4 phases)
    for phase in range(4):
        draw_body_run(draw, 1 + phase, phase)

    # Frame 5: jump_up
    draw_body_jump_up(draw, 5)

    # Frame 6: fall
    draw_body_fall(draw, 6)

    # Frame 7: land
    draw_body_land(draw, 7)

    out_path = '/home/clarliao/games/plumber-runner/assets/sprite.png'
    img.save(out_path)
    print(f'Saved sprite sheet: {out_path}')
    print(f'Size: {img.size[0]}x{img.size[1]} ({FRAMES} frames, {FRAME_W}x{FRAME_H} each)')


if __name__ == '__main__':
    main()
