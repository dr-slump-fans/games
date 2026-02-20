# Plumber Runner

A retro-style side-scrolling runner game playable in the browser (desktop & mobile).

## How to Play

The screen scrolls automatically to the right. Your character runs forward on their own — your only control is **jumping**.

- **Short tap** for a small jump, **long press** for a high jump — two distinct jump heights with clear feel difference
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
| Standalone brick group | 1–3 brick obstacle cluster that **replaces a pipe** entirely — a lighter challenge with breakable targets |

## Breakable Brick Rules — Stepping Stones & Standalone Obstacles

Breakable bricks appear in two modes: as **stepping stones** placed in front of pipes, and as **standalone obstacle groups** that replace an entire pipe spawn.

### Standalone Brick Obstacles (Pipe Replacement)

On each pipe spawn, there is a chance the pipe is replaced entirely by a standalone brick group:

- **Replace chance** scales with difficulty: 15% (EASY) → 28% (INSANE), interpolated smoothly
- When triggered, **no pipe is generated** — instead, 1–3 bricks form a small obstacle cluster
- Bricks are arranged in height tiers:
  - **Low** (30–55 px above ground) — clearable with a small jump
  - **Mid** (70–100 px above ground) — needs a medium-hold jump
  - **High** (110–140 px above ground) — requires a full jump
- Bricks are spaced 35–55 px apart horizontally, creating a compact formation
- Standalone bricks follow the same break/stand/score rules as stepping-stone bricks
- Overlap prevention ensures bricks never clip into existing pipes or other bricks
- The formation is always passable — heights match the player's jump capabilities

### Stepping Stone Placement (Pipe-Attached)

- Bricks spawn **40–140 px to the left** of a bottom pipe (never on top of or touching a pipe)
- **Tall pipes** (≥ 140 px) **always** get stepping-stone bricks; shorter pipes have a 30% chance
- **Very tall pipes** (≥ 180 px) get **2 stepping stones** at different heights; others get 1
- Lower bricks are placed ~40–70 px above ground (reachable with a small jump)
- Higher bricks (second stone) are placed at 40–65% of the pipe's height for bridging
- Bricks and pipes maintain a minimum gap (no overlapping or flush contact)

### How to Break

- Jump so your character's **head hits the bottom** of a brick
- You must be **moving upward** (rising during a jump) — falling into a brick won't break it
- On contact, the brick shatters and disappears

### Breaking Effects

1. **Debris animation**: 6 fragments scatter outward with realistic gravity — each piece has a random velocity, size (3–8 px), and color sampled from the brick palette
2. **Score popup**: A floating `+5` text rises from the break point and fades out
3. **Physics feedback**: Your upward velocity is immediately reversed and dampened (×0.4 bounce-down), giving a satisfying "bonk" feel
4. **Score**: Each brick broken awards **+5 points**

### Brick Properties

| Property | Value |
|----------|-------|
| Size | 32×24 pixels |
| Spawn chance | 100% for tall pipes (≥ 140 px), 30% for shorter pipes |
| Count | 2 bricks for very tall pipes (≥ 180 px), 1 otherwise |
| Horizontal distance | 40–140 px in front of the pipe |
| Break condition | Player rising (`vy < 0`) + head overlaps brick bottom |
| Score | +5 per brick |
| Fragments | 6 debris pieces with gravity physics |
| Fragment lifetime | 40–60 frames |

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

### Debug Features

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

## Asset & License Information

**All game assets (character, pipes, ground, clouds, hills, breakable bricks, debris fragments) are drawn programmatically on the HTML5 Canvas at runtime.** No external sprite sheets, images, or fonts are used.

- All visual assets are **original pixel art** rendered via JavaScript/Canvas code
- The player character **"Bolt"** is a fully **original pixel art explorer** with visor and jetpack — designed from scratch, not derived from any Nintendo or other copyrighted IP
- **No Nintendo sprites, Super Mario assets, or any third-party copyrighted materials are used anywhere in this project**
- All 5 animation states (idle, run, jump_up, fall, land) are hand-crafted procedural pixel art with multi-frame animation
- The game concept (side-scrolling runner with pipe obstacles) is a generic game mechanic not subject to copyright

### License

This project is released under **MIT License**. All code and procedurally generated assets are original work.
