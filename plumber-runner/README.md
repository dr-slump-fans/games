# Plumber Runner

A retro-style side-scrolling platformer game playable in the browser (desktop & mobile).

## How to Play

**The character does NOT auto-advance** — the player only moves when you press left/right. The world auto-scrolls at a fixed slow speed (obstacles move right to left) but **never speeds up**.

- **The map scrolls at a fixed slow pace**: pipes, bricks, and obstacles scroll left automatically at a constant speed that does not increase over time
- **Move left/right** (Arrow keys, A/D, or mobile left/right buttons) to dodge obstacles — holding a direction automatically accelerates to max speed
- **Short tap JUMP** for a small jump, **long press** for a high jump — two distinct jump heights
- **Must release before jumping again** — holding the button after landing will NOT auto-repeat the jump
- You can **stand on top of pipes** — pipe tops are platforms!
- **Side collisions block you** — you stop when walking into a pipe
- **Standing on pipes/bricks does NOT give score** — score only comes from passing pipes, breaking bricks, completing missions, and clearing boss waves
- You die when you get **crushed/squeezed** between a scrolling obstacle and the left screen edge, or pushed off-screen
- Your score increases each time a pipe scrolls past you
- Obstacles get harder over time (difficulty scales with survival time)
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
- **Scroll speed**: Fixed slow constant — does not change with difficulty (difficulty only affects obstacle layout)
- **Pipe spacing**: Horizontal gap between obstacles shrinks, making the world denser
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
- Scrolls left with the world (auto-scroll)
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
- Bricks scroll left with the world like pipes
- Broken bricks are removed immediately — fragments are cosmetic only

## Player Character — "Pippo" the Plumber

The player character is a fully **original pixel art creation** named "Pippo" — a stout plumber with a red cap, big mustache, and navy work overalls. The character is rendered procedurally on the HTML5 Canvas using filled rectangles, with an optional pre-generated sprite sheet.

**Design features:**
- Deep red cap with brim and yellow hexagonal badge (original geometric symbol)
- Big round nose and prominent dark brown mustache
- Expressive dot eyes with white sclera
- Red work shirt with matching cap
- Deep navy blue overalls with shoulder straps and yellow buttons
- Off-white work gloves
- Dark brown work boots

**This character is 100% original and is NOT derived from any Nintendo, Super Mario, or other copyrighted IP.** The proportions, badge design, color ratios, and facial details are intentionally distinct from any existing franchise characters. No external sprite sheets, images, or third-party assets are used.

### Character Art Revision (v2 — Original Plumber Style)

The character was redesigned from the previous "Bolt" explorer to a classic **plumber archetype** with higher visual recognizability:

**What changed:**
- **Color scheme**: Burnt orange jacket + cyan visor → **red cap + deep navy overalls** (classic plumber identity)
- **Head**: Spiky hair + tech visor → **rounded red cap with brim, hex badge, big nose, dark mustache**
- **Body**: Explorer jacket + jetpack → **red shirt + navy overalls with straps & yellow buttons**
- **Hands**: Bare skin → **off-white work gloves**
- **Run animation**: Added **body bob** (up/down oscillation per stride), more pronounced **arm swing** (arms reach further forward/back), clearer **leg stride alternation**
- **Jump animation**: Single pose → distinct **launch frame** (fist raised, determined look) vs **fall frame** (arms spread, worried face, cap blown back)
- **Landing**: Updated to match new costume with squash pose

**What stayed the same:**
- 28×36 pixel hitbox and collision box — zero gameplay change
- 5-state animation machine (idle, run, jump_up, fall, land)
- 4-frame run cycle timing
- All physics, controls, and difficulty unchanged

**Originality safeguards:**
- Hexagonal geometric badge (not letters/initials)
- Distinct color ratios and proportions from any Nintendo IP
- No copyrighted design elements referenced

## Animation States

The player character has a 5-state animation machine that drives distinct visual poses based on physics:

| State | Trigger | Visual |
|-------|---------|--------|
| `idle` | On ground, not moving (or title screen) | Relaxed stance with subtle breathing bob animation |
| `run` | On ground, moving left/right | 4-frame run cycle — arms and legs alternate, hair bounces |
| `jump_up` | Airborne with upward velocity (`vy < -0.5`) | Fist raised, legs tucked, cap tilted, determined expression |
| `fall` | Airborne with downward velocity (`vy >= -0.5`) | Arms spread for balance, legs dangling, worried expression |
| `land` | Just touched ground after being airborne | 6-frame squash impact pose with dual dust puffs |

Transitions happen automatically every frame in `updateAnimState()`:
- **Idle → Run**: player starts moving → state becomes `run`
- **Ground → Air**: jump sets `onGround = false` → state becomes `jump_up`
- **Rising → Falling**: when `vy` crosses the threshold → state becomes `fall`
- **Air → Ground**: landing detected via `wasOnGround` flag → state becomes `land` for 6 frames
- **Land → Run/Idle**: after land timer expires → state becomes `run` (if moving) or `idle` (if stationary)

## Player Position & Camera

The player starts at screen position X=320 on each new game. The camera is fixed — the world auto-scrolls left instead of the camera following the player. The character does **not** auto-advance; the player only moves when left/right input is given.

- **Auto-scroll**: obstacles (pipes, bricks, mushrooms) move left each frame at a fixed slow constant speed (does not increase over time)
- The player moves within screen bounds using left/right controls
- If a scrolling obstacle pushes the player to the left screen edge and overlaps them, the player is **crushed and dies**
- Player is clamped to the visible screen area (cannot walk off-screen)

## Minimum Brick Height Rule

All breakable bricks must have their **top surface at least 2× the player's height above the ground** (72 px minimum, since the player is 36 px tall). This prevents bricks from spawning too close to ground level, ensuring they always appear as elevated obstacles that require a jump to interact with.

| Constant | Value | Purpose |
|----------|-------|---------|
| `BRICK_MIN_HEIGHT_ABOVE_GROUND` | `72` (2 × 36) | Minimum distance from ground to brick top surface |

This rule applies to both stepping-stone bricks (placed before pipes) and standalone brick groups (pipe replacements).

## Controls

### Desktop

| Action | Keys |
|--------|------|
| Move Left | `Arrow Left` or `A` |
| Move Right | `Arrow Right` or `D` |
| Jump | `Space` or `Arrow Up` — tap for small jump, hold for high jump |

### Mobile

| Position | Buttons |
|----------|---------|
| Left side | **←** and **→** — move left/right |
| Right side | **JUMP** |

All buttons support multi-touch — you can hold a direction + JUMP simultaneously.

### Auto-Acceleration

Holding a direction key/button automatically accelerates from zero to max speed — no separate RUN button needed:

- **Smooth ramp-up** over ~1.1 seconds to max speed while held
- **Smooth deceleration** back to zero on release
- **Max speed**: 4.5 px/frame
- Run animation speed scales with current velocity

| Constant | Value | Purpose |
|----------|-------|---------|
| `PLAYER_MAX_SPEED` | `4.5` | Max movement speed (px/frame) |
| `PLAYER_ACCEL` | `0.07` | Acceleration per frame toward max speed |
| `PLAYER_DECEL` | `0.22` | Deceleration per frame when no input |

## Collision System — Swept AABB (Continuous Collision Detection)

The game uses **Swept AABB** (axis-aligned bounding box) continuous collision detection to prevent tunneling at any speed. This replaces the previous sub-stepping approach which could still miss thin obstacles at extreme velocities.

### How It Works

Instead of moving the player and then checking for overlap (discrete collision), Swept AABB computes the **exact time of first contact** between the player's moving hitbox and each obstacle's AABB along the movement vector. This is mathematically exact and cannot miss any collision regardless of speed.

#### Per-Frame Update Order

1. **Compute desired velocity** — gravity, jump initiation, variable jump hold, manual horizontal movement
2. **Swept resolve** — `resolveSweptMovement(vy, playerDX)`:
   - Player moves by `(playerDX, vy)` against obstacles
   - Gather all solid AABBs (ground, pipes lip/body, ceiling pipes, bricks)
   - Depenetrate any pre-existing overlaps (safety net)
   - Iterate up to `SWEEP_MAX_ITERATIONS` (4):
     - Call `sweptAABB()` against every obstacle to find earliest collision time `t ∈ [0, 1]`
     - Move player to contact point (`t - ε`)
     - Resolve collision normal: zero the normal-axis velocity, keep tangent velocity
     - Special handling: brick hit from below → break brick, bounce player down
     - Consume used time fraction, repeat with remaining movement
3. **Auto-scroll** — move all obstacles left by `scrollSpeed`; push player left if overlapping
4. **Post-move checks** — standing support loss, crush detection, off-screen death
5. **Cleanup** — remove off-screen obstacles, spawn new ones

#### Key Functions

| Function | Purpose |
|----------|---------|
| `sweptAABB(px,py,pw,ph,dx,dy,ox,oy,ow,oh)` | Compute time-of-impact `t ∈ [0,1]` and collision normal for a moving AABB vs a static AABB |
| `resolveSweptMovement(vy, playerDX)` | Full iterative sweep resolver — handles landing, ceiling hits, side blocks, brick breaking |
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

### Player Movement Handling

The player's manual horizontal velocity (`playerVX`) is passed directly to the swept collision resolver along with vertical velocity. Obstacles auto-scroll left each frame; after scrolling, any resulting overlap pushes the player left. When the player hits a wall, their horizontal velocity is zeroed.

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

The test simulates 9 extreme scenarios:
1. **50 px/frame downward** through 24px brick — must detect landing
2. **60 px/frame upward** through 24px brick — must detect head-hit
3. **250 px/frame horizontal** through 48px pipe — must detect side block
4. **Diagonal 80,40 px/frame** through 16px lip — must detect collision
5. **Moving away** from obstacle — must NOT false-positive
6. **Scroll-induced** collision — must detect horizontal approach
7. **Full resolver test** — 80 px/frame fall onto pipe, verify no penetration
8. **80px horizontal shift** blocked by adjacent pipe — must not penetrate pipe body
9. **60-frame repeated collision** — sustained pushing into pipe must never penetrate

Each test reports pass/fail with contact details. All tests must pass for the collision system to be considered valid.

### Depenetration Fallback (Anti-Clip Safety Net)

Even with swept AABB and pre-sweep depenetration, edge cases can cause the player hitbox to overlap a pipe after all frame processing completes. Common causes include:

- **Edge-protection nudges**: `EDGE-FORGIVE` and `WALL-NUDGE` sideways pushes could, in rare cases, place the player inside a neighboring obstacle.
- **Accumulated floating-point drift**: multiple collision responses in one frame may cause tiny overlaps.

To guarantee the player is **never rendered inside a pipe**, a **frame-end depenetration fallback** runs after all movement (obstacle scroll, X-recovery, edge nudges) completes:

1. Gather all solid collision AABBs (pipes, bricks — excluding ground).
2. For up to 4 iterations, check if the player hitbox overlaps any rect.
3. If overlap is found, compute the **minimum penetration vector** and push the player out along the smallest axis.
4. Adjust velocity: if pushed upward, land the player; if pushed downward, zero upward velocity.
5. Increment the `depenFixCount` counter for debug tracking.

Additionally, all nudge systems (`EDGE-FORGIVE`, `WALL-NUDGE`) verify the destination position is clear before applying the push. If the nudge would create a new overlap with another obstacle, it is **cancelled** (or falls back to the normal collision axis resolution).

#### Debug: `DEPEN FIX` counter (`?debug=1`)

In debug mode, the bottom-left status line displays `DEPEN FIX:N` — the cumulative number of times the frame-end depenetration fallback had to correct an overlap. Under normal play this should stay at 0 or increase very rarely. A rapidly increasing count indicates an edge case in the primary collision system that the fallback is catching.

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

The bundled `assets/sprite.png` is an **original character** ("Pippo" the Plumber) created for this project. If you replace it, ensure you have the right to use your replacement art.

## Fun Pack v1

Three new systems that add depth, replayability, and satisfying feedback to every run.

### A) Combo System

Chain events within a short time window to build a combo multiplier for bonus points.

**Combo Events:**
- **Break a brick** — base 5 points, triggers combo

**Rules:**
- Each event resets a **2.5-second combo window**; chain events before it expires to build the multiplier
- Combo level increments per event: x1, x2, x3... up to **x5 max**
- Score bonus per event = base points × combo level (on top of the normal score)
- Combo resets on timeout (2.5s without a combo event) or on death

**Visual:**
- `COMBO xN!` popup appears center-screen when combo ≥ 2, with scale-in animation
- Persistent combo bar in top-right shows current combo level and remaining time
- In debug mode (`?debug=1`): `PERFECT LAND` label flashes on successful perfect landings

| Constant | Value | Purpose |
|----------|-------|---------|
| `COMBO_WINDOW` | `2.5` | Seconds to chain the next combo event |
| `COMBO_MAX` | `5` | Maximum combo multiplier |
| `COMBO_PERFECT_LAND_VY` | `4.0` | Max `|vy|` for a landing to count as "perfect" |

### B) Speed Wave (Difficulty Rhythm)

The internal difficulty speed factor oscillates smoothly, creating rhythm variation in obstacle density and spawning.

**How it works:**
- A sine wave with **20-second period** modulates the difficulty speed factor by **±10%**
- The wave ramps in gently over the first 30 seconds (intro fade)
- **No longer affects scroll speed** (scroll is fixed constant); retained for obstacle spawn pacing variation

**Debug (`?debug=1`):**
- Bottom status line shows `SPEED_WAVE:X.XXX` — the current wave multiplier (1.0 = no effect, 1.10 = +10%, 0.90 = −10%)

| Constant | Value | Purpose |
|----------|-------|---------|
| `SPEED_WAVE_PERIOD` | `20` | Seconds per full wave cycle |
| `SPEED_WAVE_AMP` | `0.10` | Amplitude (±10% of base speed) |

### C) Mission System (Per-Run Task)

Each run randomly assigns one lightweight mission from a pool. Complete it for a score bonus.

**Mission Pool (3 types):**

| Mission | Description | Target | Time Limit |
|---------|-------------|--------|------------|
| Break Bricks | Break 3 bricks | 3 | 30 seconds |
| Eat Mushroom | Collect 1 mushroom | 1 | None |
| Land Platforms | Land on 2 platforms consecutively (no ground touch between) | 2 | None |

**Rules:**
- One mission per run, randomly selected at game start
- Mission HUD shows the task description and progress (`[progress/target]`) below the time display
- Timed missions show remaining seconds
- On completion: **+50 score** bonus and `MISSION COMPLETE!` popup (displayed for 2 seconds)
- The "Land Platforms" mission resets progress if the player touches the ground between platform landings
- No penalty for failing a mission — it simply stays incomplete

**Debug (`?debug=1`):**
- Bottom status line shows `MISSION:type progress/target`

| Constant | Value | Purpose |
|----------|-------|---------|
| `MISSION_REWARD_SCORE` | `50` | Score bonus for completing a mission |
| `MISSION_COMPLETE_DISPLAY` | `120` | Frames to show the completion popup |

## Fun Pack v2: Boss Wave

A periodic mini-challenge that creates exciting rhythm spikes every 60 seconds, rewarding survival with bonus points.

### Trigger

- Boss Wave activates every **60 seconds** of survival time
- Each wave lasts **10 seconds**
- After the wave ends, normal gameplay resumes
- The cycle repeats: 60s normal → 10s boss → 60s normal → 10s boss ...

### Boss Wave Modes

Two obstacle patterns alternate each wave:

| Mode | Name | Pattern | Challenge |
|------|------|---------|-----------|
| A | Dense Low | Short bottom pipes (50–80px) at tight intervals (120px apart) | Rhythm jumping — rapid successive hops |
| B | High-Low Mix | Alternating tall bottom pipes, ceiling pipes with helpful bricks, and brick-only gaps | Precision and platform awareness |

- Odd-numbered waves use **Mode A**, even-numbered waves use **Mode B**
- All patterns are survivable — no guaranteed-death layouts
- Mode B includes breakable bricks (some special) for bonus points and mushroom spawns

### Reward

- Surviving a Boss Wave awards **+100 points**
- A `BOSS CLEAR +100` popup appears for 2 seconds after completion
- Points stack with the combo system — breaking bricks during a boss wave still triggers combos

### Integration with Existing Systems

- **Speed Wave**: amplitude is dampened to 30% during Boss Waves to prevent unfair speed spikes
- **Combo System**: fully active during Boss Waves — chain brick breaks and perfect landings for multiplied bonus
- **Mission System**: missions continue tracking during Boss Waves
- **Collision**: all swept AABB collision detection and safety systems remain active

### HUD

- `BOSS WAVE! Xs` — red pulsing text at center-screen during the wave, with countdown
- `BOSS CLEAR +100` — orange text after surviving, fades out over 2 seconds

### Debug (`?debug=1`)

Bottom status line shows:
- `BOSS:ON/OFF` — whether a boss wave is active
- `BOSS_T:X.X` — seconds remaining in current wave
- `BOSS_MODE:A/B` — current wave pattern
- `BOSS_COUNT:N` — total waves this run
- `NEXT:Xs` — survival time threshold for next wave

| Constant | Value | Purpose |
|----------|-------|---------|
| `BOSS_WAVE_INTERVAL` | `60` | Seconds between boss waves |
| `BOSS_WAVE_DURATION` | `10` | Seconds each boss wave lasts |
| `BOSS_WAVE_REWARD_SCORE` | `100` | Score bonus for surviving a boss wave |
| `BOSS_WAVE_SPEED_WAVE_DAMP` | `0.3` | Speed wave amplitude multiplier during boss (30%) |
| `BOSS_WAVE_SPAWN_GAP` | `120` | Pixels between boss wave obstacles |

## Fun Pack v2.1: Boss Audio / Haptics

Adds programmatically generated sound effects and mobile vibration feedback to Boss Wave events, heightening the climactic feel without any external audio files.

### Sound Effects (WebAudio)

All sounds are synthesized at runtime using the Web Audio API (`OscillatorNode` + `GainNode`). No `.mp3`/`.wav` files needed.

| Event | Sound | Description |
|-------|-------|-------------|
| Boss Wave Start | Alarm beeps | Three rapid square-wave sweeps (880→440→880 Hz), creating an alert/siren feel |
| Countdown (last 3s) | Short beep | One sine-wave pip at 1 kHz per remaining second (3, 2, 1) |
| Boss Clear | Victory arpeggio | Ascending triangle-wave notes (C5→E5→G5→C6), triumphant feel |

- Volume is conservative (gain 0.08–0.10) to avoid being jarring
- `AudioContext` is lazily created on first user interaction to comply with browser autoplay policies

### Vibration (Vibration API)

| Event | Pattern | Description |
|-------|---------|-------------|
| Boss Wave Start | `[80, 40, 80, 40, 120]` | Short-short-long alert pulse |
| Boss Clear | `[40, 30, 40]` | Quick double-tap reward feel |

- Feature-detected: `navigator.vibrate` is checked before use
- Desktop browsers without vibration support silently skip — no errors thrown

### Settings Toggles

Two buttons at the top-center of the screen:

- **SFX ON/OFF** — toggles all sound effects
- **VIB ON/OFF** — toggles vibration feedback

Both default to ON. Settings are session-only (not persisted to storage). Toggles are always visible and clickable during gameplay and menus.

### Browser Compatibility

| Feature | Chrome | Firefox | Safari | Mobile Chrome | Mobile Safari |
|---------|--------|---------|--------|---------------|---------------|
| WebAudio SFX | Yes | Yes | Yes | Yes | Yes |
| Vibration API | Yes | Yes | No | Yes (Android) | No (iOS) |

- iOS Safari does not support the Vibration API — VIB toggle will have no effect on iOS devices
- WebAudio requires a user gesture (tap/click) before sounds can play — the START button satisfies this requirement

### Debug (`?debug=1`)

Bottom status line adds:
- `SFX:ON/OFF` — current sound effects state
- `VIB:ON/OFF` — current vibration state
- `VIB_SUPPORTED:true/false` — whether the browser supports the Vibration API

## Asset & License Information

**The game supports both procedural rendering (code-drawn) and sprite sheet rendering.** The bundled sprite sheet is an original creation matching the procedural character.

- All visual assets are **original pixel art** — either rendered via JavaScript/Canvas code or provided as the bundled sprite sheet
- The player character **"Pippo"** is a fully **original pixel art plumber** with red cap, mustache, and overalls — designed from scratch, not derived from any Nintendo or other copyrighted IP
- **No Nintendo sprites, Super Mario assets, or any third-party copyrighted materials are used anywhere in this project**
- All 5 animation states (idle, run, jump_up, fall, land) are hand-crafted with multi-frame animation
- The game concept (side-scrolling runner with pipe obstacles) is a generic game mechanic not subject to copyright

### License

This project is released under **MIT License**. All code and procedurally generated assets are original work.
