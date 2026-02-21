#!/usr/bin/env python3
"""Generate sprite.png for Plumber Runner — original "Pippo" plumber character.

Produces a sprite sheet with 8 frames in a single row, each 28x36 pixels.
Frame layout: idle, run0, run1, run2, run3, jump_up, fall, land

All pixel art is original — NOT derived from any Nintendo or copyrighted IP.
"""

from PIL import Image, ImageDraw

FRAME_W = 28
FRAME_H = 36
FRAMES = 8  # idle, run0-3, jump_up, fall, land

# Color palette — matches the in-game "Pippo" the Plumber
COLORS = {
    'cap':      (198, 40, 40),    # deep red cap
    'cap_hi':   (239, 83, 80),    # cap highlight
    'cap_sh':   (142, 0, 0),      # cap shadow/brim
    'badge':    (253, 216, 53),   # yellow hexagonal badge
    'skin':     (255, 204, 170),  # warm light skin
    'skin_sh':  (212, 149, 106),  # skin shadow
    'stache':   (62, 39, 35),     # dark brown mustache
    'eyes':     (26, 26, 26),     # near-black eyes
    'eye_w':    (255, 255, 255),  # eye whites
    'nose':     (232, 160, 112),  # round nose
    'shirt':    (198, 40, 40),    # red shirt (matches cap)
    'shirt_hi': (239, 83, 80),    # shirt highlight
    'overall':  (26, 58, 110),    # deep navy overalls
    'over_hi':  (46, 94, 160),    # overalls highlight
    'over_sh':  (13, 31, 60),     # overalls shadow
    'strap':    (26, 58, 110),    # overall strap
    'button':   (253, 216, 53),   # yellow buttons
    'glove':    (238, 238, 238),  # off-white work gloves
    'glove_sh': (189, 189, 189),  # glove shadow
    'boots':    (78, 52, 46),     # dark brown work boots
    'boots_h':  (121, 85, 72),    # boot highlight
    'mouth':    (93, 20, 20),     # mouth (dark)
    'trans':    (0, 0, 0, 0),
}

def px(draw, fx, x, y, w, h, color_name):
    """Draw a pixel rect at (fx*FRAME_W + x, y) with size (w, h)."""
    c = COLORS[color_name]
    ox = fx * FRAME_W
    draw.rectangle([ox + x, y, ox + x + w - 1, y + h - 1], fill=c)

def draw_cap(draw, fx, cap_y, style='normal'):
    """Draw the red cap with brim and hex badge."""
    if style == 'normal':
        px(draw, fx, 5, cap_y, 18, 3, 'cap')
        px(draw, fx, 7, cap_y - 2, 14, 3, 'cap')
        px(draw, fx, 9, cap_y - 3, 8, 2, 'cap_hi')
        px(draw, fx, 3, cap_y + 3, 22, 2, 'cap_sh')
        px(draw, fx, 12, cap_y - 1, 4, 2, 'badge')
    elif style == 'wind_up':
        px(draw, fx, 5, cap_y, 18, 3, 'cap')
        px(draw, fx, 7, cap_y - 3, 14, 3, 'cap')
        px(draw, fx, 9, cap_y - 4, 8, 2, 'cap_hi')
        px(draw, fx, 3, cap_y + 3, 22, 2, 'cap_sh')
        px(draw, fx, 12, cap_y - 2, 4, 2, 'badge')
    elif style == 'wind_back':
        px(draw, fx, 7, cap_y, 18, 3, 'cap')
        px(draw, fx, 9, cap_y - 2, 14, 3, 'cap')
        px(draw, fx, 11, cap_y - 3, 8, 2, 'cap_hi')
        px(draw, fx, 5, cap_y + 3, 20, 2, 'cap_sh')
        px(draw, fx, 14, cap_y - 1, 4, 2, 'badge')
    elif style == 'squash':
        px(draw, fx, 3, cap_y, 22, 2, 'cap')
        px(draw, fx, 5, cap_y - 2, 16, 3, 'cap')
        px(draw, fx, 7, cap_y - 2, 8, 1, 'cap_hi')
        px(draw, fx, 2, cap_y + 2, 24, 2, 'cap_sh')
        px(draw, fx, 12, cap_y - 1, 4, 2, 'badge')

def draw_head(draw, fx, head_y, cap_style='normal'):
    """Draw the head (cap + face + eyes + nose + mustache)."""
    # Cap
    draw_cap(draw, fx, head_y - 3, cap_style)
    # Face
    px(draw, fx, 6, head_y + 2, 16, 11, 'skin')
    px(draw, fx, 6, head_y + 9, 3, 4, 'skin_sh')
    # Eyes
    px(draw, fx, 8, head_y + 4, 3, 3, 'eye_w')
    px(draw, fx, 17, head_y + 4, 3, 3, 'eye_w')
    px(draw, fx, 9, head_y + 5, 2, 2, 'eyes')
    px(draw, fx, 18, head_y + 5, 2, 2, 'eyes')
    # Nose
    px(draw, fx, 12, head_y + 6, 5, 4, 'nose')
    px(draw, fx, 13, head_y + 5, 3, 1, 'nose')
    # Mustache
    px(draw, fx, 8, head_y + 9, 12, 2, 'stache')
    px(draw, fx, 7, head_y + 9, 2, 1, 'stache')
    px(draw, fx, 19, head_y + 9, 2, 1, 'stache')
    return head_y + 13  # Y after head


def draw_body_idle(draw, fx):
    """Idle stance — relaxed, arms at sides."""
    head_y = 3
    body_top = draw_head(draw, fx, head_y, 'normal')

    # Mouth
    px(draw, fx, 12, head_y + 11, 4, 1, 'mouth')

    # Shirt (collar area)
    px(draw, fx, 7, body_top, 14, 3, 'shirt')
    px(draw, fx, 7, body_top, 4, 2, 'shirt_hi')

    # Overalls
    px(draw, fx, 6, body_top + 2, 16, 8, 'overall')
    px(draw, fx, 6, body_top + 2, 3, 6, 'over_hi')
    px(draw, fx, 19, body_top + 4, 3, 4, 'over_sh')
    # Straps
    px(draw, fx, 8, body_top, 3, 3, 'strap')
    px(draw, fx, 17, body_top, 3, 3, 'strap')
    px(draw, fx, 9, body_top, 1, 1, 'button')
    px(draw, fx, 18, body_top, 1, 1, 'button')

    # Arms (shirt sleeves + gloves)
    px(draw, fx, 2, body_top + 1, 4, 5, 'shirt')
    px(draw, fx, 2, body_top + 6, 4, 3, 'glove')
    px(draw, fx, 22, body_top + 1, 4, 5, 'shirt')
    px(draw, fx, 22, body_top + 6, 4, 3, 'glove')

    # Legs (overalls)
    legs_y = body_top + 10
    px(draw, fx, 7, legs_y, 6, 8, 'overall')
    px(draw, fx, 9, legs_y + 2, 2, 2, 'over_hi')
    px(draw, fx, 15, legs_y, 6, 8, 'overall')
    px(draw, fx, 17, legs_y + 2, 2, 2, 'over_hi')

    # Boots
    px(draw, fx, 5, legs_y + 8, 8, 4, 'boots')
    px(draw, fx, 6, legs_y + 8, 3, 1, 'boots_h')
    px(draw, fx, 15, legs_y + 8, 8, 4, 'boots')
    px(draw, fx, 16, legs_y + 8, 3, 1, 'boots_h')


def draw_body_run(draw, fx, phase):
    """Run cycle — 4 phases with bob, arm swing, leg stride."""
    # Body bob: stride phases (0,2) bob up, contact phases (1,3) sit down
    bob = -1 if phase in (0, 2) else 1
    head_y = 3 + bob
    body_top = draw_head(draw, fx, head_y, 'normal')

    # Determined mouth
    px(draw, fx, 12, head_y + 11, 5, 1, 'mouth')

    # Shirt
    px(draw, fx, 7, body_top, 14, 3, 'shirt')
    px(draw, fx, 7, body_top, 4, 2, 'shirt_hi')

    # Overalls
    px(draw, fx, 6, body_top + 2, 16, 8, 'overall')
    px(draw, fx, 6, body_top + 2, 3, 6, 'over_hi')
    px(draw, fx, 19, body_top + 4, 3, 4, 'over_sh')
    # Straps
    px(draw, fx, 8, body_top, 3, 3, 'strap')
    px(draw, fx, 17, body_top, 3, 3, 'strap')
    px(draw, fx, 9, body_top, 1, 1, 'button')
    px(draw, fx, 18, body_top, 1, 1, 'button')

    # Fixed base for legs/boots (no bob — feet stay on ground)
    legs_y = 24  # fixed Y so boots always at y=32

    if phase == 0:
        # Left arm far forward-down, right arm far back-up
        px(draw, fx, 0, 14, 5, 6, 'shirt')
        px(draw, fx, 0, 20, 4, 3, 'glove')
        px(draw, fx, 23, 11, 4, 5, 'shirt')
        px(draw, fx, 24, 10, 3, 2, 'glove')
        # Left leg forward (extended), right back
        px(draw, fx, 3, legs_y, 7, 8, 'overall')
        px(draw, fx, 5, legs_y + 2, 2, 2, 'over_hi')
        px(draw, fx, 17, legs_y + 2, 5, 6, 'overall')
        px(draw, fx, 1, legs_y + 8, 9, 4, 'boots')
        px(draw, fx, 2, legs_y + 8, 3, 1, 'boots_h')
        px(draw, fx, 17, legs_y + 8, 7, 4, 'boots')
    elif phase == 1:
        # Arms mid-swing
        px(draw, fx, 1, 16, 5, 4, 'shirt')
        px(draw, fx, 1, 20, 4, 2, 'glove')
        px(draw, fx, 22, 16, 5, 4, 'shirt')
        px(draw, fx, 22, 20, 4, 2, 'glove')
        # Legs passing — together
        px(draw, fx, 8, legs_y, 5, 8, 'overall')
        px(draw, fx, 10, legs_y + 2, 2, 2, 'over_hi')
        px(draw, fx, 14, legs_y, 5, 8, 'overall')
        px(draw, fx, 16, legs_y + 2, 2, 2, 'over_hi')
        px(draw, fx, 6, legs_y + 8, 7, 4, 'boots')
        px(draw, fx, 7, legs_y + 8, 3, 1, 'boots_h')
        px(draw, fx, 14, legs_y + 8, 7, 4, 'boots')
        px(draw, fx, 15, legs_y + 8, 3, 1, 'boots_h')
    elif phase == 2:
        # Right arm far forward-down, left arm far back-up (mirror)
        px(draw, fx, 23, 14, 5, 6, 'shirt')
        px(draw, fx, 24, 20, 4, 3, 'glove')
        px(draw, fx, 1, 11, 4, 5, 'shirt')
        px(draw, fx, 1, 10, 3, 2, 'glove')
        # Right leg forward, left back
        px(draw, fx, 16, legs_y, 7, 8, 'overall')
        px(draw, fx, 18, legs_y + 2, 2, 2, 'over_hi')
        px(draw, fx, 6, legs_y + 2, 5, 6, 'overall')
        px(draw, fx, 16, legs_y + 8, 9, 4, 'boots')
        px(draw, fx, 17, legs_y + 8, 3, 1, 'boots_h')
        px(draw, fx, 4, legs_y + 8, 7, 4, 'boots')
    else:  # phase 3
        # Arms mid-swing returning
        px(draw, fx, 22, 16, 5, 4, 'shirt')
        px(draw, fx, 22, 20, 4, 2, 'glove')
        px(draw, fx, 1, 16, 5, 4, 'shirt')
        px(draw, fx, 1, 20, 4, 2, 'glove')
        # Legs close
        px(draw, fx, 7, legs_y, 6, 8, 'overall')
        px(draw, fx, 9, legs_y + 2, 2, 2, 'over_hi')
        px(draw, fx, 15, legs_y, 6, 8, 'overall')
        px(draw, fx, 17, legs_y + 2, 2, 2, 'over_hi')
        px(draw, fx, 5, legs_y + 8, 8, 4, 'boots')
        px(draw, fx, 6, legs_y + 8, 3, 1, 'boots_h')
        px(draw, fx, 15, legs_y + 8, 8, 4, 'boots')
        px(draw, fx, 16, legs_y + 8, 3, 1, 'boots_h')


def draw_body_jump_up(draw, fx):
    """Jump up — fist raised, legs tucked, determined look."""
    head_y = 2
    body_top = draw_head(draw, fx, head_y, 'wind_up')

    # Determined open mouth
    px(draw, fx, 12, head_y + 10, 4, 2, 'mouth')

    # Shirt
    px(draw, fx, 7, body_top, 14, 3, 'shirt')
    px(draw, fx, 7, body_top, 4, 2, 'shirt_hi')

    # Overalls
    px(draw, fx, 6, body_top + 2, 16, 8, 'overall')
    px(draw, fx, 6, body_top + 2, 3, 6, 'over_hi')
    px(draw, fx, 19, body_top + 4, 3, 4, 'over_sh')
    # Straps
    px(draw, fx, 8, body_top, 3, 3, 'strap')
    px(draw, fx, 17, body_top, 3, 3, 'strap')
    px(draw, fx, 9, body_top, 1, 1, 'button')
    px(draw, fx, 18, body_top, 1, 1, 'button')

    # Right arm raised fist
    px(draw, fx, 22, body_top - 3, 4, 6, 'shirt')
    px(draw, fx, 23, body_top - 5, 4, 3, 'shirt')
    px(draw, fx, 23, body_top - 7, 4, 3, 'glove')
    # Left arm down behind
    px(draw, fx, 1, body_top + 1, 5, 5, 'shirt')
    px(draw, fx, 1, body_top + 6, 4, 2, 'glove')

    # Legs tucked
    legs_y = body_top + 10
    px(draw, fx, 7, legs_y, 6, 5, 'overall')
    px(draw, fx, 15, legs_y, 6, 5, 'overall')
    px(draw, fx, 6, legs_y + 5, 7, 4, 'boots')
    px(draw, fx, 7, legs_y + 5, 3, 1, 'boots_h')
    px(draw, fx, 15, legs_y + 5, 7, 4, 'boots')
    px(draw, fx, 16, legs_y + 5, 3, 1, 'boots_h')


def draw_body_fall(draw, fx):
    """Falling — arms spread, legs dangling, worried face."""
    head_y = 4
    body_top = draw_head(draw, fx, head_y, 'wind_back')

    # Worried O mouth
    px(draw, fx, 12, head_y + 11, 4, 2, 'mouth')
    px(draw, fx, 13, head_y + 11, 2, 1, 'skin')

    # Shirt
    px(draw, fx, 7, body_top, 14, 3, 'shirt')

    # Overalls
    px(draw, fx, 6, body_top + 2, 16, 7, 'overall')
    px(draw, fx, 6, body_top + 2, 3, 5, 'over_hi')
    px(draw, fx, 19, body_top + 4, 3, 3, 'over_sh')
    # Straps
    px(draw, fx, 8, body_top, 3, 3, 'strap')
    px(draw, fx, 17, body_top, 3, 3, 'strap')
    px(draw, fx, 9, body_top, 1, 1, 'button')
    px(draw, fx, 18, body_top, 1, 1, 'button')

    # Arms spread wide
    px(draw, fx, 0, body_top, 6, 4, 'shirt')
    px(draw, fx, 0, body_top - 1, 4, 3, 'shirt')
    px(draw, fx, 0, body_top - 2, 3, 2, 'glove')
    px(draw, fx, 22, body_top + 1, 6, 4, 'shirt')
    px(draw, fx, 25, body_top - 1, 3, 3, 'shirt')
    px(draw, fx, 25, body_top - 2, 3, 2, 'glove')

    # Legs dangling
    legs_y = body_top + 9
    px(draw, fx, 6, legs_y, 6, 7, 'overall')
    px(draw, fx, 8, legs_y + 2, 2, 2, 'over_hi')
    px(draw, fx, 16, legs_y, 6, 7, 'overall')
    px(draw, fx, 18, legs_y + 2, 2, 2, 'over_hi')
    px(draw, fx, 5, legs_y + 7, 8, 4, 'boots')
    px(draw, fx, 6, legs_y + 7, 3, 1, 'boots_h')
    px(draw, fx, 15, legs_y + 7, 8, 4, 'boots')
    px(draw, fx, 16, legs_y + 7, 3, 1, 'boots_h')


def draw_body_land(draw, fx):
    """Landing squash — compressed body, wide stance."""
    head_y = 6
    body_top = draw_head(draw, fx, head_y, 'squash')

    # Strained mouth
    px(draw, fx, 11, head_y + 11, 6, 1, 'mouth')

    # Shirt squashed
    px(draw, fx, 3, body_top, 22, 2, 'shirt')

    # Overalls squashed wide
    px(draw, fx, 2, body_top + 2, 24, 5, 'overall')
    px(draw, fx, 2, body_top + 2, 4, 3, 'over_hi')
    px(draw, fx, 22, body_top + 3, 4, 3, 'over_sh')
    # Straps
    px(draw, fx, 7, body_top, 3, 3, 'strap')
    px(draw, fx, 18, body_top, 3, 3, 'strap')
    px(draw, fx, 8, body_top, 1, 1, 'button')
    px(draw, fx, 19, body_top, 1, 1, 'button')

    # Arms bracing
    px(draw, fx, 0, body_top + 1, 4, 4, 'shirt')
    px(draw, fx, 0, body_top + 5, 3, 2, 'glove')
    px(draw, fx, 24, body_top + 1, 4, 4, 'shirt')
    px(draw, fx, 25, body_top + 5, 3, 2, 'glove')

    # Wide stance legs
    legs_y = body_top + 7
    px(draw, fx, 2, legs_y, 8, 5, 'overall')
    px(draw, fx, 4, legs_y + 1, 2, 2, 'over_hi')
    px(draw, fx, 18, legs_y, 8, 5, 'overall')
    px(draw, fx, 20, legs_y + 1, 2, 2, 'over_hi')

    # Wide boots
    px(draw, fx, 0, legs_y + 5, 10, 4, 'boots')
    px(draw, fx, 1, legs_y + 5, 3, 1, 'boots_h')
    px(draw, fx, 18, legs_y + 5, 10, 4, 'boots')
    px(draw, fx, 19, legs_y + 5, 3, 1, 'boots_h')


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
