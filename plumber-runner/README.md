# Plumber Runner

A retro-style side-scrolling runner game playable in the browser (desktop & mobile).

## How to Play

The screen scrolls automatically to the right. Your character runs forward on their own — your only control is **jumping**.

- **Short tap** for a small jump, **long press** for a high jump — two distinct jump heights with clear feel difference
- **Must release before jumping again** — holding the button/screen after landing will NOT auto-repeat the jump; you must lift your finger (or release the key) and press again
- You can **stand on top of pipes** — pipe tops are platforms!
- **Side collisions push you back** instead of killing you instantly
- You die when you get **crushed/squeezed** between obstacles:
  - Pushed off the left edge of the screen by a pipe
  - Squeezed between a bottom pipe and a ceiling pipe
  - Pinned between a ceiling pipe and the ground
- Your score increases each time you clear a pipe
- The game speeds up over time!
- **HUD** shows survival time, current difficulty level (Lv.1~Lv.5), and progress bar

## Difficulty Growth Rules

Difficulty scales **smoothly** over survival time across 5 levels. All transitions use smooth-step interpolation (no sudden jumps).

| Level | Name | Starts at | Speed | Pipe Spacing | Max Pipe Height | Pair Chance | Brick Replace |
|-------|------|-----------|-------|-------------|-----------------|-------------|---------------|
| Lv.1 | EASY | 0s | 1.0x | 280–380 px | 150 px | 35% | 15% |
| Lv.2 | NORMAL | 30s | 1.25x | 250–340 px | 170 px | 40% | 18% |
| Lv.3 | HARD | 75s | 1.55x | 220–300 px | 195 px | 47% | 22% |
| Lv.4 | EXPERT | 140s | 1.85x | 195–270 px | 220 px | 52% | 25% |
| Lv.5 | INSANE | 240s | 2.15x | 175–245 px | 240 px | 55% | 28% |

**What changes with difficulty:**
- **Scroll speed**: Multiplied by the level's speed factor (on top of gradual per-frame acceleration)
- **Pipe spacing**: Horizontal gap between obstacles shrinks, making runs denser
- **Pipe height cap**: Later levels unlock taller bottom/ceiling pipes that require more precise jumping
- **Pair frequency**: More top+bottom pipe combinations appear, creating tighter squeeze corridors
- **Passable gap**: The vertical gap in pipe pairs narrows smoothly from ~96 px to ~66 px
- **Brick replace**: Higher difficulty means more pipes are replaced by standalone brick groups (15% → 28%)

The difficulty curve is designed so:
- **0–30s**: Gentle warm-up, easy spacing, low pipes only
- **30–75s**: Speed picks up, taller pipes appear, more pairs
- **75–140s**: Demanding — tight gaps, fast scroll, tall obstacles
- **140–240s**: Expert territory — requires precise jump timing
- **240s+**: Maximum difficulty reached, stays constant

## Jump Mechanics

The jump system uses a **short-tap / long-press** design:

| Input | Behavior | Use case |
|-------|----------|----------|
| Short tap | Small jump (low initial velocity, no hold boost) | Hop over short pipes, stay low under ceiling pipes |
| Long press | High jump (hold adds upward acceleration over 16 frames) | Clear tall pipes, reach pipe tops for platforming |

The two jumps feel distinctly different: a quick tap gives a compact hop, while holding the button significantly extends jump height. This lets players make precise, deliberate choices about jump commitment.

## Staircase Pipe Rule

Tall bottom pipes (>= 140 px) are always preceded by 1–2 shorter "stepping-stone" pipes:

- Pipes **140–199 px** tall get **1 step** placed before them
- Pipes **200+ px** tall get **2 steps** placed before them
- Step heights are proportional to the target pipe (roughly 1/2 or 1/3 height)
- Steps serve as platforms the player can land on to build height before the tall obstacle

This prevents unfair situations where a single ultra-tall pipe appears with no way to react. Players can use the stepping pipes as launchpads or simply as visual warning that a tall obstacle is coming.

## Obstacle Types

| Type | Description |
|------|-------------|
| Bottom pipe | Rises from the ground — you can jump over **or stand on top** |
| Ceiling pipe | Hangs from the top — duck under or time your jump carefully |
| Pipe pair | Bottom + ceiling pipe together — navigate through the gap |
| Breakable brick | Stepping-stone brick placed before pipes — **stand on it or smash it from below** for bonus points! |
| Special brick | Purple brick with mushroom icon — break it from below to spawn a **mushroom power-up** |
| Mushroom | Red mushroom item — collect it to gain **double jump** ability for 25 seconds |
| Standalone brick group | 1–3 brick obstacle cluster that **replaces a pipe** entirely — a lighter challenge with breakable targets |

## Breakable Brick Rules — Stepping Stones & Standalone Obstacles

Breakable bricks appear in two modes: as **stepping stones** placed in front of pipes, and as **standalone obstacle groups** that replace an entire pipe spawn.

### Standalone Brick Obstacles (Pipe Replacement)

On each pipe spawn, there is a chance the pipe is replaced entirely by a standalone brick group:

- **Replace chance** scales with difficulty: 15% (EASY) → 28% (INSANE), interpolated smoothly
- When triggered, **no pipe is generated** — instead, 1–3 bricks form a small obstacle cluster
- Bricks are arranged in height tiers (all respect the **minimum height rule**: brick top ≥ 2× player height above ground = 72 px):
  - **Low** (72–95 px above ground) — clearable with a jump
  - **Mid** (100–130 px above ground) — needs a medium-hold jump
  - **High** (135–165 px above ground) — requires a full jump
- Bricks are spaced 35–55 px apart horizontally, creating a compact formation
- Standalone bricks follow the same break/stand/score rules as stepping-stone bricks
- Overlap prevention ensures bricks never clip into existing pipes or other bricks
- The formation is always passable — heights match the player's jump capabilities

### Stepping Stone Placement (Pipe-Attached)

- Bricks spawn **40–140 px to the left** of a bottom pipe (never on top of or touching a pipe)
- **Tall pipes** (≥ 140 px) **always** get stepping-stone bricks; shorter pipes have a 30% chance
- **Very tall pipes** (≥ 180 px) get **2 stepping stones** at different heights; others get 1
- Lower bricks are placed ~72–92 px above ground (respects minimum height rule: ≥ 2× player height)
- Higher bricks (second stone) are placed at 40–65% of the pipe's height for bridging
- Bricks and pipes maintain a minimum gap (no overlapping or flush contact)

### How to Break

- Jump so your character's **head hits the bottom** of a brick
- You must be **moving upward** (rising during a jump) — falling into a brick won't break it
- On contact, the brick shatters and disappears

### Breaking Effects

1. **Debris animation**: 6 fragments scatter outward with realistic gravity — each piece has a random velocity, size (3–8 px), and color sampled from the brick palette
2. **Score popup**: A floating `+5` text rises from the break point and fades out
3. **Time bonus popup**: A green `+5s` text floats up from the brick, indicating the survival timer increase
4. **Physics feedback**: Your upward velocity is immediately reversed and dampened (×0.4 bounce-down), giving a satisfying "bonk" feel
5. **Score**: Each brick broken awards **+5 points**
6. **Time bonus**: Each brick broken adds **+5 seconds** to the survival timer — the bonus is applied **immediately** after the brick breaks (same frame), and the HUD clock and game-over Time reflect the total including all bonuses. In debug mode (`?debug=1`), each brick break logs the accumulated bonus time to the console.

### Brick Properties

| Property | Value |
|----------|-------|
| Size | 32×24 pixels |
| Spawn chance | 100% for tall pipes (≥ 140 px), 30% for shorter pipes |
| Count | 2 bricks for very tall pipes (≥ 180 px), 1 otherwise |
| Horizontal distance | 40–140 px in front of the pipe |
| Break condition | Player rising (`vy < 0`) + head overlaps brick bottom |
| Score | +5 per brick |
| Time bonus | +5 seconds per brick |
| Fragments | 6 debris pieces with gravity physics |
| Fragment lifetime | 40–60 frames |

## Special Bricks, Mushrooms & Double Jump

### Special Bricks

**25% of all spawned bricks** (both stepping-stone and standalone) are randomly upgraded to **special bricks**. Special bricks are visually distinct:

- **Purple/magical color scheme** instead of brown/terracotta
- **Animated gold sparkles** that shimmer
- **Mushroom icon** in the center

Special bricks follow the same break rules as normal bricks (hit from below while rising). Breaking a special brick:
1. Awards the same **+5 score** and **+5s time bonus** as a normal brick
2. **Spawns a mushroom item** at the brick's position

### Mushroom Power-Up

When a special brick is broken, a **red mushroom** pops out and moves through the world:

- Mushroom spawns centered on the broken brick, **direction biased toward the player** for reachability
- If the spawn position overlaps another unbroken brick, the mushroom is pushed above it
- Mushroom moves **horizontally** at 1.8 px/frame
- Affected by **gravity** (0.4 px/frame²) — falls and lands on ground/pipe surfaces
- **Bounces off pipe walls AND unbroken bricks** (reverses horizontal direction on side collision, lands on top surfaces)
- **Scrolls with the world** like all other objects
- **Unstuck logic**: if a mushroom remains embedded in a solid for 30+ frames, it teleports to ground level
- Removed when off-screen

**Collecting:** Walk into or near the mushroom to pick it up. On pickup:
- The **double jump** ability activates for **25 seconds**
- A `MUSHROOM!` popup appears
- Picking up another mushroom while the timer is active **resets the timer** to 25 seconds

### Mushroom Pickup Detection

The pickup system uses a **two-layer approach** to prevent missed pickups at high game speeds:

1. **Enlarged overlap check** — the player hitbox is expanded by `MUSHROOM_PICKUP_MARGIN` (6 px) on each side when testing mushroom collision. This provides a generous "grab radius" that compensates for frame-to-frame position jumps.

2. **Swept pickup (continuous detection)** — each frame, the relative displacement between the mushroom and player is computed. A Minkowski-expanded swept AABB test is run along this path. If the player and mushroom paths crossed at any point during the frame (even if they don't overlap at frame boundaries), the pickup triggers.

Together, these two methods ensure that mushrooms can be reliably collected even at the highest scroll speeds and during fast air movement.

| Constant | Default | Purpose |
|----------|---------|---------|
| `MUSHROOM_PICKUP_MARGIN` | `6` | Pixel expansion on each side for enlarged pickup zone |

#### Debug Features (`?debug=1`)

- **Red outline**: mushroom hitbox (actual collision box)
- **Pink dashed outline**: expanded pickup zone (with `MUSHROOM_PICKUP_MARGIN`)
- **Yellow arrow**: mushroom velocity direction
- **`MUSHROOM PICKUP`** (red text, top-left): flashes for ~2s when a mushroom is collected
- **Bottom status line**: shows `mush:N` (number of active mushrooms)
- **Console logs**: spawn position, collection events, unstuck teleports

### Double Jump Rules

| Condition | Behavior |
|-----------|----------|
| No mushroom collected | Normal single jump only |
| Mushroom active | Can perform **1 additional air jump** per airborne session |
| After landing | Air jump count resets — can air jump again next time |
| Timer expires | Returns to normal single jump |

**How it works:**
- After collecting a mushroom, a **25-second countdown** begins
- While airborne, pressing jump again (after releasing from the first jump) triggers an **air jump** with **~60% the height** of a ground jump (60% initial velocity and 55% hold frames)
- Only **1 air jump per airborne session** — landing resets the counter
- Variable jump hold works on air jumps too (short tap = small air jump, long press = higher air jump), but the maximum height is capped at ~60% of the ground jump

**HUD indicator:**
- `MUSHROOM: ON [Xs]` — mushroom active, on ground or air jump already used
- `DOUBLE JUMP READY [Xs]` — mushroom active, air jump available (shown while airborne)
- Hidden when mushroom is not active

| Constant | Value | Purpose |
|----------|-------|---------|
| `SPECIAL_BRICK_CHANCE` | `0.25` | Chance a brick spawns as a special brick |
| `MUSHROOM_SPEED` | `1.8` | Mushroom horizontal speed (px/frame) |
| `MUSHROOM_GRAVITY` | `0.4` | Mushroom gravity (px/frame²) |
| `DOUBLE_JUMP_DURATION` | `25` | Seconds of double jump ability after eating mushroom |
| `MAX_AIR_JUMPS` | `1` | Maximum air jumps per airborne session |
| `AIR_JUMP_INITIAL` | `-4.2` | Air jump initial velocity (60% of ground jump) |
| `AIR_JUMP_HOLD_MAX_T` | `8` | Air jump hold frames (55% of ground jump) |

### What Cannot Be Broken

- **Ground** — always solid
- **Pipes** (bottom and ceiling) — always solid, act as platforms or obstacles
- Only the dedicated **breakable brick** obstacles can be destroyed

### Brick Interaction

- You can **stand on top** of intact bricks (they act as platforms from above)
- Bricks are placed before pipes as launch platforms — use them to reach tall pipe tops
- Bricks scroll with the world at the same speed as pipes
- Broken bricks are removed immediately — fragments are cosmetic only

## Player Character — "Bolt" the Explorer

The player character is a fully **original pixel art creation** named "Bolt" — a spiky-haired explorer with a cyan visor and mini jetpack. The character is rendered procedurally on the HTML5 Canvas using filled rectangles (no sprite sheets or external images).

**Design features:**
- Deep indigo spiky hair with highlights
- Cyan tech visor (not goggles) with glint effects
- Burnt orange explorer jacket with shading
- Grey-blue jetpack on back with animated thrust glow
- Dark cargo pants with pocket details
- Utility belt with yellow buckle

**This character is 100% original and is NOT derived from any Nintendo, Super Mario, or other copyrighted IP.** No external sprite sheets, images, or third-party assets are used.

## Animation States

The player character has a 5-state animation machine that drives distinct visual poses based on physics:

| State | Trigger | Visual |
|-------|---------|--------|
| `idle` | Title screen / pre-game | Relaxed stance with subtle breathing bob animation |
| `run` | On ground, not landing | 4-frame run cycle — arms and legs alternate, hair bounces |
| `jump_up` | Airborne with upward velocity (`vy < -0.5`) | Arms raised, legs tucked, hair streaming up, jetpack thrust glow |
| `fall` | Airborne with downward velocity (`vy >= -0.5`) | Arms spread for balance, legs dangling, worried expression |
| `land` | Just touched ground after being airborne | 6-frame squash impact pose with dual dust puffs |

Transitions happen automatically every frame in `updateAnimState()`:
- **Idle → Run**: game starts → state becomes `run`
- **Ground → Air**: jump sets `onGround = false` → state becomes `jump_up`
- **Rising → Falling**: when `vy` crosses the threshold → state becomes `fall`
- **Air → Ground**: landing detected via `wasOnGround` flag → state becomes `land` for 6 frames
- **Land → Run**: after land timer expires → state becomes `run`

## Player Default Position

The player's default horizontal position is set to **40% of the canvas width** (320 px on an 800 px canvas). This places the character near the center of the screen rather than far left, giving players better reaction time and a clearer view of upcoming obstacles. The position resets to 40% on each game restart. After being pushed back by obstacles, the player recovers to the default X position using **lerp-based smooth tracking** (12% per frame with 0.5 px minimum speed), providing a noticeably fast return without jarring teleportation.

## Minimum Brick Height Rule

All breakable bricks must have their **top surface at least 2× the player's height above the ground** (72 px minimum, since the player is 36 px tall). This prevents bricks from spawning too close to ground level, ensuring they always appear as elevated obstacles that require a jump to interact with.

| Constant | Value | Purpose |
|----------|-------|---------|
| `BRICK_MIN_HEIGHT_ABOVE_GROUND` | `72` (2 × 36) | Minimum distance from ground to brick top surface |

This rule applies to both stepping-stone bricks (placed before pipes) and standalone brick groups (pipe replacements).

## Controls

| Platform | Action |
|----------|--------|
| Desktop  | `Space` or `Arrow Up` — tap for small jump, hold for high jump |
| Mobile   | Touch anywhere — tap for small jump, hold for high jump |

## Collision System — Swept AABB (Continuous Collision Detection)

The game uses **Swept AABB** (axis-aligned bounding box) continuous collision detection to prevent tunneling at any speed. This replaces the previous sub-stepping approach which could still miss thin obstacles at extreme velocities.

### How It Works

Instead of moving the player and then checking for overlap (discrete collision), Swept AABB computes the **exact time of first contact** between the player's moving hitbox and each obstacle's AABB along the movement vector. This is mathematically exact and cannot miss any collision regardless of speed.

#### Per-Frame Update Order

1. **Compute desired velocity** — gravity, jump initiation, variable jump hold
2. **Swept resolve** — `resolveSweptMovement(vy, scrollDX)`:
   - Fold scroll-induced horizontal motion into the player's relative velocity vs obstacles
   - Gather all solid AABBs (ground, pipes lip/body, ceiling pipes, bricks)
   - Depenetrate any pre-existing overlaps (safety net)
   - Iterate up to `SWEEP_MAX_ITERATIONS` (4):
     - Call `sweptAABB()` against every obstacle to find earliest collision time `t ∈ [0, 1]`
     - Move player to contact point (`t - ε`)
     - Resolve collision normal: zero the normal-axis velocity, keep tangent velocity
     - Special handling: brick hit from below → break brick, bounce player down
     - Consume used time fraction, repeat with remaining movement
   - Convert from obstacle-rest-frame back to world coordinates
3. **Move obstacles** — apply scroll displacement to pipe/brick positions
4. **Post-move checks** — standing support loss, crush detection, off-screen death
5. **Cleanup** — remove off-screen obstacles, spawn new ones, recover player X position

#### Key Functions

| Function | Purpose |
|----------|---------|
| `sweptAABB(px,py,pw,ph,dx,dy,ox,oy,ow,oh)` | Compute time-of-impact `t ∈ [0,1]` and collision normal for a moving AABB vs a static AABB |
| `resolveSweptMovement(vy, scrollDX)` | Full iterative sweep resolver — handles landing, ceiling hits, side blocks, brick breaking |
| `gatherCollisionRects()` | Collect all solid world AABBs (ground, pipes, bricks) |
| `depenetratePlayer(rects)` | Push player out of any pre-existing overlaps using minimum penetration vector |
| `checkStandingSupport()` | Check if player is still supported on a platform after obstacles move |

### Why Swept AABB Cannot Tunnel

The `sweptAABB()` function computes entry/exit times on each axis analytically:

```
tEntry_x = distToEntry_x / dx    tExit_x = distToExit_x / dx
tEntry_y = distToEntry_y / dy    tExit_y = distToExit_y / dy
tEntry = max(tEntry_x, tEntry_y)
tExit  = min(tExit_x,  tExit_y)
collision if tEntry <= tExit AND tEntry in [0, 1]
```

This works for **any velocity magnitude** — even if `dy = 500` pixels/frame, it will find the exact contact time with a 16px-tall pipe lip. No step size or tolerance window is needed.

### Scroll Motion Handling

Horizontal scroll is folded into the swept calculation as relative velocity. In the obstacle-rest-frame, the player moves by `(+scrollDX, vy)` relative to obstacles. After the sweep resolves, `scrollDX` is subtracted from the player's world X to convert back. This means:

- Side collisions from scroll are detected continuously (no tunneling through pipe walls)
- When blocked horizontally, the remaining scroll pushes the player left in world coords (correct crush behavior)

### Edge-Jump Protection (Lip Forgiveness + Wall-Kick Nudge + Head-Center Rule)

Jumping near pipe edges is a common frustration point. Three complementary systems prevent unfair "stuck" situations when the player jumps while touching or near a pipe:

#### 1. Lip Corner Forgiveness (Enhanced)

Pipe lips are wider than the pipe body (`LIP_W=56` vs `PIPE_W=48`), creating a 4px overhang on each side. When the player is sliding along the side of a pipe body and jumps upward, their head can clip this overhang — resulting in a frustrating "bonk" that kills the jump even though the overlap is tiny.

**Lip corner forgiveness** solves this by detecting when an upward-moving player clips only the outer edge of a lip. If the horizontal overlap between the player hitbox and the lip rect is within `LIP_CORNER_FORGIVE` pixels (default: **14**, increased from 8), the collision response **nudges the player sideways** to clear the lip corner instead of blocking the jump. This only activates while the player is ascending (`vy < 0`).

This applies in two places:

1. **Swept collision response** — when the sweep detects a ceiling hit (`normalY=1`) against a `pipe_lip` or `ceiling_pipe_lip` rect, the forgiveness check runs before the standard "stop upward movement" response. If triggered, the player is nudged sideways, the upward velocity is preserved, and the sweep continues with the remaining movement fraction.

2. **Depenetration** — when pre-existing overlap with a lip rect is detected and the player is moving upward, sideways depenetration is forced over vertical depenetration if the horizontal overlap is within the forgiveness margin.

**Safety**: The nudge pushes the player **away** from the pipe (outward past the lip edge), so it cannot cause wall penetration. The pipe body is narrower than the lip, and the nudge clears the player past the lip's outer edge. Full-center hits on the lip (overlap > `LIP_CORNER_FORGIVE` AND head center overlapping) still block the jump as expected.

#### 2. Wall-Kick Nudge

When the player is flush against a pipe body side wall and initiates a jump, a one-time outward push (`WALL_NUDGE_PX = 3` pixels) is applied on the jump start frame. This prevents the lip overhang from immediately blocking the ascent.

- Fires **once per jump** (reset on landing)
- Only on **pipe body side contact** (within 2px of touching)
- Pushes **away** from the pipe — cannot push into the pipe
- Works for both left-side and right-side contact

#### 3. Head-Center Rule

For pipe-lip ceiling collisions, only the **center 45%** of the player's hitbox width counts as a "head hit". If only the edge of the player's head brushes a lip corner, the collision is treated as a **side deflection** (sideways nudge) instead of a ceiling bonk.

This prevents the common case where a tiny corner overlap kills an otherwise clean jump.

| Constant | Default | Purpose |
|----------|---------|---------|
| `LIP_CORNER_FORGIVE` | `14` | Max horizontal overlap (px) that triggers sideways nudge instead of jump block |
| `WALL_NUDGE_PX` | `3` | Pixels of outward push on jump-start when touching pipe wall |
| `HEAD_CENTER_RATIO` | `0.45` | Fraction of hitbox width that counts as "head center" for ceiling bonk |

### Debug Features

#### Edge-protection overlay (always visible)

When lip forgiveness or wall-kick nudge activates, a short-lived label appears at the top-left of the game canvas:
- **`EDGE-FORGIVE`** (cyan) — lip corner forgiveness or head-center rule triggered a sideways deflection
- **`WALL-NUDGE`** (yellow) — wall-kick nudge fired on jump start near a pipe wall

These labels fade out after ~1.5 seconds and are always visible (no debug flag needed).

#### Hitbox overlay (`?debug=1`)

Append `?debug=1` to the URL to render collision boxes:
- **Green** outline = player hitbox
- **Red** outline = pipe lip collision rect
- **Orange** outline = pipe body collision rect
- **Cyan** line = pipe stand-Y surface
- **Yellow** outline = brick hitbox
- Bottom-left text shows scroll speed, vertical velocity, Y position, and `[SweptAABB]` label

#### Self-test (`runCollisionSelfTest()`)

In debug mode (`?debug=1`), a collision self-test runs automatically on page load. You can also trigger it manually from the browser console:

```js
runCollisionSelfTest()
```

The test simulates 7 extreme scenarios:
1. **50 px/frame downward** through 24px brick — must detect landing
2. **60 px/frame upward** through 24px brick — must detect head-hit
3. **250 px/frame horizontal** through 48px pipe — must detect side block
4. **Diagonal 80,40 px/frame** through 16px lip — must detect collision
5. **Moving away** from obstacle — must NOT false-positive
6. **Scroll-induced** collision — must detect horizontal approach
7. **Full resolver test** — 80 px/frame fall onto pipe, verify no penetration

Each test reports pass/fail with contact details. All tests must pass for the collision system to be considered valid.

## Running

Open `index.html` in any modern browser. No build step, no server, no CDN required.

Works on GitHub Pages — just push and visit:
```
https://<username>.github.io/<repo>/plumber-runner/
```

## Custom Sprite Sheet (Sprite Mode)

The game supports two character rendering modes:

1. **Sprite mode** (default) — loads `assets/sprite.png` + `assets/sprite.json`
2. **Procedural mode** (fallback) — draws the character with code (original behavior)

If sprite loading fails (missing files, network error, corrupt image), the game automatically falls back to procedural rendering. No manual switching is needed.

### Sprite Sheet Format

The default sprite sheet is a **single-row PNG** with transparent background (RGBA):

| Property | Value |
|----------|-------|
| Frame size | 28×36 pixels |
| Layout | Single row, left-to-right |
| Total frames | 8 (minimum) |
| Format | PNG with alpha transparency |

**Frame order (column index):**

| Index | Animation | Description |
|-------|-----------|-------------|
| 0 | `idle` | Relaxed stance (title screen) |
| 1 | `run` frame 0 | Left arm forward |
| 2 | `run` frame 1 | Contact pose (legs together) |
| 3 | `run` frame 2 | Right arm forward |
| 4 | `run` frame 3 | Neutral transition |
| 5 | `jump_up` | Arms raised, legs tucked |
| 6 | `fall` | Arms spread, legs dangling |
| 7 | `land` | Squash impact pose |

### How to Replace with Your Own Sprite

1. **Create your sprite sheet** — a PNG file with all animation frames in a single row (or grid), each frame exactly the same size. The default is 28×36 per frame, but you can use any size.

2. **Save as `assets/sprite.png`** — replace the existing file.

3. **Edit `assets/sprite.json`** — update the metadata to match your sprite sheet:
   ```json
   {
     "meta": {
       "image": "sprite.png",
       "frameWidth": 28,
       "frameHeight": 36,
       "columns": 8,
       "rows": 1
     },
     "animations": {
       "idle":    { "frames": [0],       "frameRate": 1,  "loop": true },
       "run":     { "frames": [1,2,3,4], "frameRate": 10, "loop": true },
       "jump_up": { "frames": [5],       "frameRate": 1,  "loop": false },
       "fall":    { "frames": [6],       "frameRate": 1,  "loop": false },
       "land":    { "frames": [7],       "frameRate": 1,  "loop": false }
     }
   }
   ```
   - `frameWidth` / `frameHeight` — size of each frame in pixels
   - `columns` — number of frames per row
   - `rows` — number of rows in the sheet
   - `animations` — maps each animation state to frame indices (0-based, left-to-right, top-to-bottom)
   - `frames` array — the frame indices to play for that animation (run needs ≥ 4 frames)

4. **Refresh the browser** — the game will load your custom sprite automatically.

5. **If something looks wrong** — the game will auto-fallback to the code-drawn character. Check the browser console for `[Sprite]` warnings.

> **Important:** The player hitbox (28×36) is separate from the sprite. If your sprite is a different size, update `frameWidth`/`frameHeight` in sprite.json. The collision box is slightly shrunk from the visual size for fairness (20×32 effective hitbox), so minor size differences are fine.

### Copyright Reminder

**Do NOT use copyrighted or unlicensed sprite art.** This includes but is not limited to:
- Nintendo characters (Mario, Luigi, Link, Kirby, etc.)
- Sprites ripped from commercial games
- Fan art that you don't have permission to use

The bundled `assets/sprite.png` is an **original character** ("Bolt" the Explorer) created for this project. If you replace it, ensure you have the right to use your replacement art.

## Asset & License Information

**The game supports both procedural rendering (code-drawn) and sprite sheet rendering.** The bundled sprite sheet is an original creation matching the procedural character.

- All visual assets are **original pixel art** — either rendered via JavaScript/Canvas code or provided as the bundled sprite sheet
- The player character **"Bolt"** is a fully **original pixel art explorer** with visor and jetpack — designed from scratch, not derived from any Nintendo or other copyrighted IP
- **No Nintendo sprites, Super Mario assets, or any third-party copyrighted materials are used anywhere in this project**
- All 5 animation states (idle, run, jump_up, fall, land) are hand-crafted with multi-frame animation
- The game concept (side-scrolling runner with pipe obstacles) is a generic game mechanic not subject to copyright

### License

This project is released under **MIT License**. All code and procedurally generated assets are original work.
