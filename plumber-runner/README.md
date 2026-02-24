# Plumber Runner

A retro-style side-scrolling platformer game playable in the browser (desktop & mobile).

## How to Play

The map does **not auto-scroll**. The player moves freely using left/right controls. When the player reaches the **center of the screen (50% width)**, the camera begins scrolling forward to follow them. The camera **never scrolls backward** — you can only move left within the visible area, but the world won't rewind.

- **No auto-scroll**: the map stays still until the player pushes forward past the screen midpoint
- **Camera follows at midpoint**: when the player crosses the center of the screen, the camera begins tracking them, keeping the player near the center
- **Forward only**: the camera offset only increases (monotonic) — pressing left moves the player within the screen but never scrolls the map backward
- **No floor drift**: standing idle keeps the player stationary (no conveyor belt effect)
- **Move left/right** (Arrow keys, A/D, or mobile left/right buttons) to dodge obstacles — holding a direction automatically accelerates to max speed
- **Short tap JUMP** for a small jump, **long press** for a high jump — two distinct jump heights
- **Must release before jumping again** — holding the button after landing will NOT auto-repeat the jump
- You can **stand on top of pipes** — pipe tops are platforms!
- **Side collisions block you** — you stop when walking into a pipe
- **Standing on pipes/bricks does NOT give score** — score only comes from passing pipes, breaking bricks, completing missions, and clearing boss waves
- You die when you get **crushed/squeezed** between an obstacle and the left camera edge, or pushed off-screen
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
- **Scroll speed**: No auto-scroll — camera follows player (difficulty only affects obstacle layout)
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

## Platformer Level Generator (Chunk System)

The level is generated using a **chunk-based system** that produces playable, reachable platformer segments with good rhythm. Instead of spawning individual obstacles, the generator builds the world from fixed-width **chunks** (600–900 px each), each drawn from a template pool.

### Chunk Types

| Type | Description | Danger Level |
|------|-------------|--------------|
| `rest` | Flat ground with maybe 1 low pipe + optional brick. Breathing room. | Safe |
| `single_platform` | 1 bottom pipe as platform + optional stepping bricks | Low |
| `double_platform` | 2 bottom pipes at staggered heights — staircase platforming | Medium |
| `pipe_mix` | Mixed obstacles: bottom pipe + optional ceiling pipe, bricks | High |
| `turtle_zone` | Flat/low terrain with turtle enemies — room for stomping | Low |
| `reward` | Brick cluster (2–4 bricks) with high special brick chance | Safe |

### Reachability Constraints

Every chunk is validated against player physics limits before being committed to the world:

| Constraint | Value | Source |
|------------|-------|--------|
| Max jump height | 150 px | `JUMP_INITIAL` + `JUMP_HOLD_ACCEL` × `JUMP_HOLD_MAX_T` |
| Max horizontal jump range | 240 px | Full jump airtime × `PLAYER_MAX_SPEED` |
| Min clearance for ceiling pipes | 42 px | Player height (36) + margin |
| Min gap in pipe pairs | player.h + 20 px | Passable vertical space |

If a generated chunk fails reachability validation, it is **rerolled** (up to 5 times). After 2 failed attempts, the generator falls back to simpler chunk types (`rest` or `single_platform`). After all rerolls fail, a `rest` chunk is forced.

### Difficulty Curve

Chunk selection weights shift over survival time across 4 phases:

| Phase | Time | Max Pipe Height | Focus |
|-------|------|-----------------|-------|
| Tutorial | 0–60s | 100 px | Mostly `rest` + `single_platform`, low obstacles |
| Medium | 60–180s | 140 px | Add `double_platform`, `pipe_mix`, `turtle_zone` |
| Hard | 180–300s | 200 px | All types, higher complexity |
| Max | 300s+ | 240 px | Full difficulty, `pipe_mix` dominant |

Difficulty increases through **segment complexity and element combinations**, not raw speed.

### Safety Rules

- **Max 2 consecutive danger chunks** (`double_platform` or `pipe_mix`), then a forced rest/easy chunk
- **Every 5 chunks**, at least one `rest` or `reward` chunk is guaranteed
- **Turtle placement**: only on surfaces with ≥60 px clear ground on each side, validated against nearby pipes
- **Bricks**: placed at reachable heights (≥72 px above ground, ≤150 px)
- **No instant-death traps**: ceiling pipes require minimum 42 px clearance; pipe pairs require gap ≥ player height + 20 px

### Debug Overlay (`?debug=1`)

When debug mode is active, the chunk system adds:

- **Chunk boundary markers**: yellow dashed vertical lines at each chunk start, with chunk ID and type label
- **Reroll indicators**: orange label showing reroll count when a chunk needed regeneration
- **Bottom status line**: `CHUNK:#N type PHASE:Name REROLLS:N NEXT_X:N TOTAL:N CONSEC_DANGER:N`

### Constants

| Constant | Value | Purpose |
|----------|-------|---------|
| `CHUNK_MIN_WIDTH` | `600` | Minimum chunk width (px) |
| `CHUNK_MAX_WIDTH` | `900` | Maximum chunk width (px) |
| `CHUNK_PLAYER_MAX_JUMP_H` | `150` | Conservative max jump height for validation |
| `CHUNK_PLAYER_MAX_JUMP_X` | `240` | Conservative max horizontal jump range |
| `CHUNK_MAX_CONSEC_DANGER` | `2` | Max consecutive danger chunks before forced rest |
| `CHUNK_SAFE_INTERVAL` | `5` | Every N chunks, guarantee a safe chunk |
| `CHUNK_MAX_REROLLS` | `5` | Max rerolls per chunk for reachability |

## Theme Chunk System

The level generator uses a **theme state machine** to create distinct visual and gameplay segments. Instead of uniform difficulty throughout, the world cycles through three themes that alter chunk selection weights, obstacle parameters, and visual style.

### Themes

| Theme | Style | Key Characteristics |
|-------|-------|---------------------|
| **PLAINS** | Open, relaxed | More rest/reward chunks, lower pipe heights (-20 px), fewer turtles (60%), wider spacing |
| **CAVE** | Claustrophobic, rhythmic | More pipe_mix and double_platform, higher ceiling pipes (+30 px maxTopH), short-distance rhythm jumps |
| **TOWER** | Vertical, layered | Taller bottom pipes (+20 px), more double_platform (staircase), fewer turtles (50%), clear vertical layers |

### Theme Cycling

- Each theme lasts **4–8 chunks** (randomly chosen)
- When a theme expires, a different theme is selected at random
- The **first chunk** of each new theme is a **transition chunk**: weight biases are softened (40% theme / 60% base), danger chunks are suppressed, and a `rest` weight floor of 25 is guaranteed — this prevents sudden difficulty spikes at theme boundaries

### Weight Multipliers

Each theme applies multipliers to the base difficulty-phase weights:

| Type | PLAINS | CAVE | TOWER |
|------|--------|------|-------|
| `rest` | 1.8x | 0.5x | 0.4x |
| `single_platform` | 1.2x | 1.0x | 1.3x |
| `double_platform` | 0.5x | 1.5x | 1.8x |
| `pipe_mix` | 0.3x | 1.8x | 1.0x |
| `turtle_zone` | 0.7x | 0.8x | 0.5x |
| `reward` | 1.5x | 0.8x | 1.2x |

### Parameter Offsets

| Parameter | PLAINS | CAVE | TOWER |
|-----------|--------|------|-------|
| `maxPipeH` | -20 px | +10 px | +20 px |
| `maxTopH` | -20 px | +30 px | -10 px |
| Turtle spawn chance | 60% | 100% | 50% |
| Reward brick mult | 1.4x | 0.8x | 1.1x |

All parameter offsets are clamped to reachability limits (`CHUNK_PLAYER_MAX_JUMP_H` for pipe height, 42 px min clearance for ceiling pipes).

### Reachability Safety

Theme biases do **not** bypass any existing safety rules:

- **Reachability validation + reroll** still runs on every chunk
- **Max 2 consecutive danger chunks** rule still forces rest/easy
- **Every 5 chunks safe chunk guarantee** still applies
- Transition chunks are biased toward safe types
- Parameter offsets are clamped to physics-derived limits

### Visual Feedback

Each theme has distinct visual styling that transitions smoothly (~2 seconds) between themes:

| Element | PLAINS | CAVE | TOWER |
|---------|--------|------|-------|
| Sky gradient | Blue (#5c94fc → #92c4f8) | Dark navy (#2a2a3e → #3d3d5c) | Twilight purple (#4a3a6e → #7a6a9e) |
| Ground | Brown (#c0784a) | Grey-blue (#555566) | Sandy (#887766) |
| Hills | Green (#3a9d5c) | Dark blue (#2a3a4c) | Purple (#5a4a6c) |

### HUD

- **`THEME: PLAINS`** — shown in the top-right, color-coded per theme
- **`OPEN PLAINS`** / **`ENTER CAVE`** / **`HIGH TOWER`** — center-screen announcement on theme change, fades out over ~2 seconds

### Debug (`?debug=1`)

Bottom status line adds:
- `THEME:PLAINS` — current active theme
- `REMAIN:N` — chunks remaining in current theme
- `NEXT:CAVE` — next theme that will activate
- `TRANSITION:YES/NO` — whether current chunk is a transition chunk
- `COLOR_LERP:0.XX` — visual color transition progress (0→1)

Chunk boundary markers also show the theme name for each chunk.

### Constants

| Constant | Value | Purpose |
|----------|-------|---------|
| `THEME_MIN_CHUNKS` | `4` | Minimum chunks per theme |
| `THEME_MAX_CHUNKS` | `8` | Maximum chunks per theme |
| `THEME_TRANSITION_CHUNKS` | `1` | Number of transition chunks at theme start |
| `THEME_ANNOUNCE_DURATION` | `120` | Frames to show theme announcement (~2s) |

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
| Question block | Golden block with "?" — hit from below to pop a **coin** (+10 points), then becomes a used grey block (stays solid) |
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

When a special brick is broken, a **red mushroom** pops out, **drops to the ground under gravity, then walks along the ground** (掉落到地面後沿地面移動):

- Mushroom spawns centered on the broken brick, **direction biased toward the player** for reachability
- If the spawn position overlaps another unbroken brick, the mushroom is pushed above it
- Mushroom **pops upward with visible initial velocity** (vy=-7) — 先從磚塊中彈出再落地行走，類似經典 Mario 香菇行為
- During the pop-out phase, the mushroom has **30 frames of spawn grace** (~0.5s) — pickup is disabled until grace expires, preventing "instant eat on headbutt"
- Spawn position is shifted to maintain **≥24px horizontal distance** from the player
- If the spawn position overlaps the player hitbox, the mushroom is **shifted horizontally** away from the player for extra safety
- After the arc, the mushroom **falls under gravity** (0.4 px/frame²) until landing on the ground or a solid surface
- After landing, the mushroom **walks horizontally along the ground** at 1.8 px/frame in world-space
- **Bounces off pipe walls AND unbroken bricks** (reverses horizontal direction on side collision, lands on top surfaces)
- **Unstuck logic**: if a mushroom remains embedded in a solid for 30+ frames, it teleports to ground level
- Removed when off-screen

**Collecting:** Walk into the mushroom (actual AABB overlap required) to pick it up. On pickup:
- The **double jump** ability activates for **25 seconds**
- A `MUSHROOM!` popup appears
- Picking up another mushroom while the timer is active **resets the timer** to 25 seconds

### Mushroom Pickup Detection (Armed Contact Pickup)

Mushrooms are collected **only when the player's inset pickup box overlaps the mushroom's inset pickup box** AND the mushroom has been **armed**. Arming requires: grace expired, mushroom in `ground-run` state, and the mushroom must have been **fully separated** from the player for at least 8 consecutive frames. Once armed, pickup stays armed (no re-lock on re-overlap).

| Constant | Default | Purpose |
|----------|---------|---------|
| `MUSHROOM_PICKUP_INSET_X` | `4` | Pixel inset on each side of mushroom for strict pickup box |
| `MUSHROOM_PICKUP_INSET_Y` | `4` | Pixel inset on top/bottom of mushroom for strict pickup box |
| `PLAYER_PICKUP_INSET_X` | `2` | Pixel inset on each side of player hitbox for pickup |
| `PLAYER_PICKUP_INSET_Y` | `2` | Pixel inset on top/bottom of player hitbox for pickup |
| `MUSHROOM_SPAWN_GRACE` | `30` | Frames of pickup immunity after spawn (~0.5s) |
| `MUSHROOM_ARM_SEP_FRAMES` | `8` | Consecutive no-overlap frames needed to arm pickup after grace expires |
| `MIN_SPAWN_DIST` | `24` | Minimum horizontal px distance from player at spawn |

#### Debug Features (`?debug=1`)

- ~~Mushroom hitbox / pickup box overlays~~ — disabled (collision logic unchanged)
- **`MUSHROOM PICKUP`** (red text, top-left): flashes for ~2s when a mushroom is collected
- **Bottom status line**: shows `mush:N` (number of active mushrooms)
- **Console logs**: spawn position, state transitions (`pop→fall→ground-run`), collection events, unstuck teleports

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
| `MUSHROOM_POP_VY` | `-7` | Initial upward velocity when popping out of brick |
| `MUSHROOM_SPAWN_GRACE` | `15` | Frames of collision immunity after spawn (pop-out protection) |
| `DOUBLE_JUMP_DURATION` | `25` | Seconds of double jump ability after eating mushroom |
| `MAX_AIR_JUMPS` | `1` | Maximum air jumps per airborne session |
| `AIR_JUMP_INITIAL` | `-4.2` | Air jump initial velocity (60% of ground jump) |
| `AIR_JUMP_HOLD_MAX_T` | `8` | Air jump hold frames (55% of ground jump) |

## Question Blocks & Coin System

### Question Blocks

**~30% of non-special bricks** are randomly upgraded to **question blocks** (mutually exclusive with special bricks — a brick is either normal, special, or question). Question blocks are visually distinct:

- **Golden yellow color scheme** instead of brown/terracotta
- **Animated white "?" glyph** that shimmers
- **Corner rivets** for a metallic look

Question blocks follow different rules from normal bricks:

1. **Single-use**: each question block can only be triggered **once**
2. **Not breakable**: hitting a question block from below does NOT destroy it — it stays solid as a platform
3. **Coin pop**: on hit, a gold coin pops upward from the block with a short arc animation, then fades out
4. **Score**: each coin awards **+10 points** (`COIN_SCORE`)
5. **Used state**: after triggering, the block turns into a **dark grey "used block"** — visually inert, still solid

### Coin Counter HUD

A persistent **COIN: N** counter is displayed in the top-right HUD area (below the score), showing total coins collected this run. The counter resets to 0 on game restart.

### Coin Pop Animation

When a question block is hit:
- A small golden coin sprite (8×10 px) pops upward from the block
- The coin rises with initial velocity, decelerates under gravity, then fades out over ~0.5 seconds
- A floating `+10` score popup appears simultaneously

### Constants

| Constant | Value | Purpose |
|----------|-------|---------|
| `QUESTION_BLOCK_CHANCE` | `0.30` | Chance a non-special brick becomes a question block |
| `COIN_SCORE` | `10` | Points awarded per coin from question block |

### What Cannot Be Broken

- **Ground** — always solid
- **Pipes** (bottom and ceiling) — always solid, act as platforms or obstacles
- **Question blocks** — they turn into used blocks but remain solid; they cannot be shattered
- Only the dedicated **breakable brick** obstacles can be destroyed

### Brick Interaction

- You can **stand on top** of intact bricks (they act as platforms from above)
- Bricks are placed before pipes as launch platforms — use them to reach tall pipe tops
- Bricks remain stationary in world-space like pipes
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

The player starts at world position X=160 on each new game. The camera follows the player when they push past the screen midpoint.

- **No auto-scroll**: obstacles remain stationary in world-space; the player walks through the world
- **Camera trigger**: when the player's world X exceeds `cameraX + SCREEN_HALF_X` (50% screen width), the camera advances to keep the player at the midpoint
- **Forward-only camera**: `cameraX` is monotonically increasing — pressing left moves the player within the visible area but never rewinds the camera
- **No floor drift**: standing idle keeps the player stationary
- The player is clamped to the camera-visible area (`cameraX` to `cameraX + DESIGN_W`)
- If the player is pushed against the left camera edge by an obstacle, they are **crushed and die**

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

Holding a direction key/button automatically accelerates from zero to max speed — no separate RUN button needed. Standing still keeps the player stationary (no floor drift):

- **Smooth ramp-up** over ~1.1 seconds to max speed while held
- **Smooth deceleration** back to zero on release
- **Max speed**: 4.5 px/frame
- Run animation speed scales with current velocity

| Constant | Value | Purpose |
|----------|-------|---------|
| `PLAYER_MAX_SPEED` | `4.5` | Max movement speed (px/frame) |
| `PLAYER_ACCEL` | `0.07` | Acceleration per frame toward max speed |
| `PLAYER_DECEL` | `0.22` | Deceleration per frame when no input |
| `BRAKE_TO_STOP_TIME` | `0.5` | Seconds to brake to zero on ground when reversing |
| `BRAKE_DECEL_MIN` | `0.10` | Min decel per frame during ground brake (prevents infinite slide at low speed) |
| `BRAKE_DECEL_MAX` | `0.60` | Max decel per frame during ground brake (caps at very high speed) |
| `AIR_BRAKE_DECEL` | `0.30` | Weaker reverse-brake deceleration in air |

### Braking & Reverse Movement (Mario-style)

When the player inputs the **opposite direction** of their current velocity (`inputDir × vx < 0`), a dedicated braking phase activates:

- **Ground brake** — time-based: deceleration is computed each frame so that speed reaches zero in approximately `BRAKE_TO_STOP_TIME` (0.5 s), clamped between `BRAKE_DECEL_MIN` and `BRAKE_DECEL_MAX` to prevent extreme values. The player skids with the `brake` animation (skidding pose + dust particles) for the full 0.5 s, then accelerates in the new direction. This gives a satisfying slide-to-stop feel before reversing.
- **Air brake** — uses `AIR_BRAKE_DECEL` (weaker than ground but stronger than normal decel). No 0.5 s time constraint — provides noticeable air-control drag without the abrupt ground stop. No brake animation in air — jump/fall poses are preserved.
- **Same-direction input** — unchanged smooth ramp-up toward `PLAYER_MAX_SPEED`.
- **No input** — unchanged passive decel via `PLAYER_DECEL`.

Debug overlay (`debug=1`) shows `vx`, `brake:0/1`, `brakeT` (remaining brake timer), and `onGround:0/1` on the bottom status line.

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
3. **Camera follow** — update `cameraX` based on player position (forward-only, midpoint trigger); push player out if overlapping
4. **Post-move checks** — standing support loss, crush detection, off-screen death
5. **Cleanup** — remove obstacles behind camera, spawn new ones ahead

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

The player's manual horizontal velocity (`playerVX`) is passed directly to the swept collision resolver along with vertical velocity. Obstacles are stationary in world-space; the camera follows the player. When the player hits a wall, their horizontal velocity is zeroed.

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

## Turtle Enemy System

Ground-walking turtle enemies add a new threat and scoring mechanic. Turtles walk along the ground, interact with terrain, and can be defeated by stomping. Turtle head direction always matches its movement direction. After stomping an idle shell, it pops upward, then falls below the ground and disappears.

### Enemy States

| State | Behavior | Visual |
|-------|----------|--------|
| `walk` | Walks leftward on ground, reverses at walls/edges | Green-shelled turtle with animated legs |
| `shell_idle` | Stationary shell on ground, waiting to be kicked | Compact green dome, no movement |
| `shell_move` | Shell sliding at high speed, deadly to player and other turtles | Green dome with speed lines |
| `shell_bounce_dead` | Stomped shell bouncing upward then falling off-screen | Green dome, rising then falling |
| `dead` | Defeated turtle, fading upside-down shell | Flipping shell, fades out |

### Collision Rules

| Situation | Result |
|-----------|--------|
| Player stomps walking turtle (falling from above) | Turtle → `shell_idle`, player bounces up, **+10 points** |
| Player touches walking turtle from side/below | **Player dies** (Game Over) |
| Player stomps idle shell (falling from above) | **+5 points**, shell enters `shell_bounce_dead` (pops up then falls off-screen), player bounces |
| Player touches idle shell from side | Shell kicked (`shell_move`), **player safe**, no score |
| Moving shell hits player | **Player dies** (Game Over) |
| Moving shell hits walking turtle | Other turtle dies, **+20 points** with score popup |
| Moving shell hits pipe/brick wall | Shell bounces back (reverses direction) |

### Stomp Detection

A stomp is registered when:
- Player is falling (`vy > 0`)
- Player's bottom edge is above 40% of the turtle's height

This prevents side-collisions from registering as stomps. On stomp, the player receives a bounce (`vy = -5.5`).

### Shell Mechanics

- **Kick grace**: After stomping, a brief grace period (10 frames) prevents immediately kicking the shell
- **Kick direction**: Shell slides away from the player's center
- **Shell speed**: 5.5 px/frame — fast enough to be visually exciting and dangerous
- **Wall bounce**: Shells reverse direction on pipe/brick contact
- **Chain kills**: A moving shell can defeat multiple turtles in a row, each awarding +20 points

### Spawning

- Turtles spawn randomly ahead of the camera on ground level
- Spawn chance: ~30% per frame (throttled by spawn gap)
- Minimum gap between spawns: 400 px
- Spawn position is validated to avoid overlapping pipes or bricks
- Turtles are removed when they move far off-screen

### Scoring

| Action | Points |
|--------|--------|
| Stomp a turtle | +10 (`TURTLE_STOMP_SCORE`) |
| Stomp an idle shell | +5 (`TURTLE_SHELL_STOMP_SCORE`) |
| Shell kills another turtle | +20 (`TURTLE_SHELL_KILL_SCORE`) |

### Debug (`?debug=1`)

- **Hitbox overlays**: Lime = walking turtle, Teal = idle shell, Red = moving shell, Grey = bounce dead
- **State labels**: Each turtle shows its current state above the hitbox
- **Bottom status line**: `TURTLES:N walk:N idle:N move:N bdead:N dead:N | ...`

### Constants

| Constant | Value | Purpose |
|----------|-------|---------|
| `TURTLE_W` | `24` | Walking turtle width (px) |
| `TURTLE_H` | `28` | Walking turtle height (px) |
| `SHELL_W` | `24` | Shell width (px) |
| `SHELL_H` | `16` | Shell height (px) |
| `TURTLE_WALK_SPEED` | `1.0` | Walking speed (px/frame) |
| `SHELL_MOVE_SPEED` | `5.5` | Shell sliding speed (px/frame) |
| `TURTLE_STOMP_SCORE` | `10` | Points for stomping |
| `TURTLE_SHELL_STOMP_SCORE` | `5` | Points for stomping an idle shell |
| `TURTLE_SHELL_KILL_SCORE` | `20` | Points for shell killing another turtle |
| `TURTLE_STOMP_BOUNCE_VY` | `-5.5` | Player bounce velocity on stomp |
| `TURTLE_SPAWN_CHANCE` | `0.30` | Per-frame spawn probability (throttled) |
| `TURTLE_MIN_SPAWN_GAP` | `400` | Minimum px between turtle spawns |

## Flagpole Level-Clear Flow

A flagpole spawns at a fixed world-X distance (`FLAGPOLE_DISTANCE = 5000`). Reaching it ends the current run with a victory sequence.

### Collision & Guard
- On first contact with the flagpole hitbox, `levelCleared` is set **once**; a duplicate-collision guard (`if (!levelCleared)`) prevents re-triggering.
- A one-time score bonus (`LEVEL_CLEAR_BONUS = 50`) is awarded with a "LEVEL CLEAR +50" popup.

### Slide Animation (~1.25 s)
- The player snaps horizontally to the pole center and enters the **sliding** phase.
- Each frame, the player eases downward toward ground level.
- During sliding, all normal gameplay (movement, gravity, enemies, death checks) is frozen — the `update()` early-return prevents any further game logic.

### Done Phase & Overlay
- After `LEVEL_CLEAR_SLIDE_FRAMES` (75 frames ≈ 1.25 s) the phase switches to **done**.
- A dark overlay displays "LEVEL CLEAR!", final score, and survival time.
- Any input (jump / move) restarts the game; inputs during the slide phase are ignored.

### Constants
| Constant | Value | Purpose |
|---|---|---|
| `FLAGPOLE_DISTANCE` | 5000 | World X where flagpole spawns |
| `FLAGPOLE_W / H` | 16 / 200 | Pole collision size |
| `LEVEL_CLEAR_BONUS` | 50 | One-time score bonus |
| `LEVEL_CLEAR_SLIDE_FRAMES` | 75 | Slide duration (frames) |

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

## Step 2: Coin Sound Effects & Combo Feedback

Adds a short synthesized "coin" sound when a question block is hit, plus a pitch-rising combo system for rapid consecutive hits.

### Coin SFX

A two-note square-wave chirp (root + fifth) plays each time a question block pops a coin. The sound is generated entirely via WebAudio (`OscillatorNode` + `GainNode`) — no external audio files.

- Base frequency: **988 Hz** (B5)
- Volume: gain 0.06, fading to 0 over 60 ms per note — conservative to avoid being jarring
- Respects the existing **SFX ON/OFF** toggle

### Combo Pitch Scaling

When question blocks are hit in rapid succession (within **1.2 seconds**), each subsequent hit raises the coin sound by one semitone (100 cents). This gives an ascending "staircase" feel that rewards rhythmic play.

| Parameter | Value | Description |
|-----------|-------|-------------|
| `COIN_COMBO_WINDOW` | `1.2` | Seconds — hits within this window continue the combo |
| `COIN_COMBO_MAX` | `8` | Maximum combo level (caps pitch at +8 semitones) |
| `COIN_BASE_FREQ` | `988` | Base frequency in Hz (B5) |

- Combo level resets to 0 when the window expires without a new hit
- Combo state resets on game restart
- No scoring or gameplay changes — combo only affects audio pitch

## Step 3: Block Bump & Coin Pop Polish

Visual refinements to question-block interaction feel.

### Block Bump Animation
When a question block is hit from below, the block now plays a quick **bump animation** — it visually pops upward by 6 px and returns over 8 frames using a sine curve. This is purely visual; the collision box stays in place for stability.

| Constant | Value | Purpose |
|----------|-------|---------|
| `BLOCK_BUMP_FRAMES` | `8` | Total frames for the bump animation |
| `BLOCK_BUMP_HEIGHT` | `6` | Maximum upward pixel offset |

### Enhanced Coin Pop
- **Higher arc**: initial velocity increased from −4 to **−6 px/frame**, lifetime extended from 30 to **40 frames**
- **Spin effect**: the coin visually stretches/compresses horizontally to simulate a rotating coin
- **Smooth fade-out**: coin fades to transparent over the last 15 frames of its life

### HUD Coin Combo Indicator
When hitting question blocks in rapid succession, the coin HUD shows **`x2`, `x3`, …** next to the coin count for the duration of the combo window, giving immediate visual feedback for combo streaks.

## Step 4: Coin Accumulation & 1UP Life System

Classic Mario-style extra-life mechanic tied to coin collection.

### Lives System
- Player starts each run with **3 lives** (`INITIAL_LIVES = 3`)
- HUD displays `LIFE: N` in green below the coin counter
- On death with lives remaining: player **respawns in place** (near camera center) instead of Game Over
  - Score, coins, timer, and world state are preserved
  - Nearby turtles (within 200 px) are cleared to prevent instant re-death
  - Mushroom power-up timer is reset on respawn
- On death with 0 lives: standard Game Over flow (unchanged)

### 100-Coin 1UP
- When `coins >= 100`: `lives += 1`, `coins -= 100` (handles multiples via `while` loop)
- Floating popup displays **`1UP!`** above the player
- Ascending two-note SFX jingle (E5 → A5, triangle wave)
- `check1UP()` is called immediately after each coin increment

| Constant | Value | Purpose |
|----------|-------|---------|
| `INITIAL_LIVES` | `3` | Starting lives per run |
| 1UP threshold | `100 coins` | Coins needed for an extra life |

## Enemy Interaction Step 1: Patrol Stability & Shell Combo Scoring

Refines turtle enemy behavior for smoother patrol and adds escalating combo rewards for shell chain kills.

### Patrol Stabilization

Walking turtles now use a **turn cooldown** (`TURTLE_TURN_COOLDOWN = 8` frames) that prevents rapid direction flipping. This eliminates the 1px jitter/twitching that occurred when a turtle sat at the exact boundary of a pipe or platform edge.

**Key changes:**
- Side collisions with pipes/bricks now **set** the direction explicitly (face away from wall) instead of toggling — hitting the same wall repeatedly no longer causes oscillation
- Platform edge detection respects the cooldown — the turtle commits to its turn and walks away before checking again
- All existing death rules, stomp rules, and shell mechanics are preserved unchanged

### Shell Combo Kill Scoring

When a moving shell kills multiple turtles in sequence, each successive kill awards escalating points:

| Kill # | Points | Popup |
|--------|--------|-------|
| 1st | 20 | `+20` (standard) |
| 2nd | 40 | `SHELL x2 +40` (cyan) |
| 3rd | 80 | `SHELL x3 +80` (cyan) |
| 4th | 160 | `SHELL x4 +160` (cyan) |
| 5th+ | 320 | `SHELL x5 +320` (cyan, capped) |

- Formula: `SHELL_COMBO_BASE × 2^(comboLevel - 1)`, capped at `SHELL_COMBO_MAX = 5`
- Combo counter resets when the shell is kicked (new kick = fresh combo)
- Combo popups use a distinct **cyan** color and slightly larger font to stand out from normal score popups

| Constant | Value | Purpose |
|----------|-------|---------|
| `TURTLE_TURN_COOLDOWN` | `8` | Min frames between walk direction reversals |
| `SHELL_COMBO_MAX` | `5` | Maximum shell combo multiplier level |
| `SHELL_COMBO_BASE` | `20` | Base score for first shell kill (doubles per combo) |

## Enemy Interaction Step 2: Shell Bounce Feel & Patrol Readability

Micro-polish pass that improves shell bounce reliability and adds a subtle visual cue for turtle patrol turns.

### Shell Bounce Anti-Sticking

Moving shells now have a **bounce cooldown** (`SHELL_BOUNCE_COOLDOWN = 4` frames) after each wall/brick bounce. During cooldown, the shell ignores further bounce triggers, preventing rapid direction-flipping that caused the shell to visually "stick" or jitter against walls when collision geometry overlapped across consecutive frames.

**Key changes:**
- Each shell_move bounce (pipe or brick) sets `bounceCooldown = 4`
- While `bounceCooldown > 0`, further bounce reversal is suppressed — the shell commits to its new direction
- All death rules, stomp mechanics, combo scoring, and kick behavior are unchanged

### Patrol Turn Visual Hint

Walking turtles now show a brief **front-leg lift** when they reverse direction (during the existing `turnCooldown` window). The front leg raises 3 px for the 8-frame cooldown period, giving players a subtle but readable cue that the turtle has turned. The walk animation also freezes during the lift, reinforcing the "pause and turn" feel.

| Constant | Value | Purpose |
|----------|-------|---------|
| `SHELL_BOUNCE_COOLDOWN` | `4` | Frames of bounce immunity after shell wall-bounce |

## Enemy Interaction Step 3: Shell Combo Feedback Enhancement

Audio and visual feedback polish for shell combo kills, making multi-kill chains feel more rewarding without changing any scoring or death rules.

### Escalating Shell Combo SFX

New `sfxShellCombo(comboLevel)` function generates a WebAudio two-tone "thwack-ping" on every shell kill. Feedback escalates with combo level:

- **Pitch** rises ~2 semitones per combo step (base 330 Hz → up to ~523 Hz at combo 5)
- **Timbre** shifts from `square` wave to `sawtooth` at combo level 3+ for a grittier, more intense feel
- **Third "sparkle" note** added at combo level 3+ (octave above base) for extra reward cue
- **Volume** stays conservative (0.07 peak, +0.01 per level on the second note)

### Enhanced Shell Combo Popup Visuals

Shell combo popups (`SHELL x2 +40`, etc.) now escalate visually:

- **Color** shifts from teal (#4aeadc) through cyan (#5af8ff) to gold (#fff44f / #ff6) at high combos
- **Font size** scales 16 → 24 px across combo levels 1–5
- **Initial scale** starts larger at higher combos (1.15× → 1.75×), then shrinks to 1.0× over 30 frames
- **Display duration** increases (+8 frames per combo level on top of the base 55 frames)
- First kill (combo 1) uses the standard popup style with just the SFX

### What Did NOT Change

- Score formula: `SHELL_COMBO_BASE × 2^(comboLevel - 1)` — unchanged
- Death/damage rules — unchanged
- Stomp, kick, and bounce mechanics — unchanged

## Enemy Interaction Step 4: Spawn Density Rhythm & Patrol Stabilization

Final polish pass for enemy spawning fairness and patrol reliability.

### Rhythmic Spawn Density

Supplemental random turtle spawning is now gated by a distance-based rhythm cycle (`SPAWN_RHYTHM_CYCLE = 1200 px`). Each cycle alternates between a **pressure window** (60% — normal spawning) and a **relief window** (40% — random spawns suppressed). This creates natural breathing room so the player isn't under constant enemy pressure.

### Nearby-Turtle Density Cap

`spawnTurtle()` now counts active walk/idle turtles within `TURTLE_MIN_SPAWN_GAP` (400 px) of the proposed spawn point. If 2+ (`TURTLE_NEARBY_CAP`) already exist, the spawn is rejected. This prevents unfair clusters of 3+ turtles in a short stretch.

### Patrol Edge-Detection Stabilization

- Edge-detection probe widened from 1×1 to **4×6 pixels**, reducing false edge triggers from sub-pixel alignment
- On edge reversal, turtle is **snapped back 3 px** away from the edge to prevent flip-flop oscillation
- `TURTLE_TURN_COOLDOWN` increased from 8 → **12 frames** for more decisive direction changes

### What Did NOT Change

- Score formula, death/damage rules, shell combo mechanics — all unchanged
- Chunk-based turtle placement logic — unchanged (rhythm only gates the supplemental random spawner)
- Shell bounce cooldown and anti-sticking — unchanged

## Hidden Blocks & Lightweight Hidden Route (Step 1)

Secret blocks that are invisible until the player discovers them by head-bumping from below — a classic hidden-item mechanic that rewards exploration.

### Hidden Block Mechanic

Hidden blocks are **invisible and non-solid** by default. The player can walk and jump through them freely. When the player's head hits a hidden block from below while jumping (ascending), the block is **revealed**:

1. The block becomes **visible** — drawn as a distinctive teal/cyan metallic block with a "!" mark
2. The block becomes **permanently solid** — acts as a platform (like a used question block)
3. A **bump animation** plays (same sine-based pop as question blocks)
4. **+10 score** is awarded with a floating popup
5. A **coin pop SFX** plays for satisfying audio feedback
6. The player **bounces downward** (vy reversed at 40%) — standard "bonk" feel

### Hidden Route Entry Points

Hidden blocks are placed in `single_platform` and `pipe_mix` chunks as **shortcut stepping stones**:

- **`single_platform`**: When pipe height >= 100 px, 20% chance to place a hidden block at 70–90% of pipe height, 40–90 px left of the pipe. If revealed, provides a direct shortcut to the pipe top without needing the normal stepping-stone bricks.
- **`pipe_mix`**: When pipe height >= 140 px (tall pipe threshold), 20% chance to place a hidden block at 60–80% of pipe height, 20–80 px right of the pipe lip. If revealed, gives a shortcut stepping point past the pipe.

### Fairness Rules

- **Optional**: All levels are completable without discovering any hidden blocks — they're purely bonus shortcuts
- **Non-obstructive**: Unrevealed hidden blocks have no collision — they can't trap, block, or crush the player
- **Reachable**: All hidden block positions are within the player's jump range (max 150 px jump height)
- **No death traps**: Hidden blocks are placed at safe positions, never near screen edges or in squeeze corridors
- **Enemies pass through**: Unrevealed hidden blocks don't interact with turtles, mushrooms, or shells

### Debug (`?debug=1`)

- **Dashed teal outline**: Unrevealed hidden blocks are shown with a semi-transparent dashed teal rectangle
- **Solid teal outline**: Revealed hidden blocks show a solid teal hitbox outline
- All existing debug overlays (chunk markers, brick hitboxes, etc.) continue to work

### Constants

| Constant | Value | Purpose |
|----------|-------|---------|
| `HIDDEN_BLOCK_SCORE` | `10` | Points awarded when a hidden block is revealed |
| `HIDDEN_BLOCK_CHANCE` | `0.20` | Chance per eligible chunk to spawn a hidden block |
| `HIDDEN_HINT_RANGE` | `60` | Horizontal proximity range for spark hint (px) |
| `HIDDEN_HINT_FREQ` | `8` | Spawn a hint spark every N frames (low frequency) |
| `HIDDEN_REVEAL_BONUS` | `5` | Extra bonus points on reveal ("SECRET!" reward) |

## Hidden Blocks — Readability Hints & Reward Feedback (Step 2)

Building on the hidden block foundation from Step 1, this step adds subtle discoverability cues and a stronger reward loop.

### Proximity Hint Sparks

When the player is **horizontally within 60 px** of an unrevealed hidden block and positioned just below it, a tiny **teal spark** particle floats upward from the block's underside. The sparks are:

- **Very subtle**: max 0.5 alpha, 1.5–2.5 px size, 18-frame lifetime
- **Low frequency**: one spark per 8 frames at most, only one block hints at a time
- **Non-spoiling**: no outline, no shape — just a faint shimmer that rewards attentive players

### Reveal Reward Feedback

When a hidden block is successfully revealed by a head-bump:

- **Bonus score**: +15 total (10 base + 5 SECRET bonus), up from the original +10
- **"SECRET!" popup**: a teal-colored floating text label appears above the score popup
- **Distinct SFX**: a rising three-note triangle-wave chime (660→880→1100 Hz) replaces the generic coin sound, giving hidden blocks a unique audio identity

### Design Principles Preserved

- Hidden blocks remain **optional shortcuts**, never required
- The +5 bonus is small enough not to distort the score economy
- Hint sparks are ambient and easily missed — they don't spell out "jump here"

## Hidden Blocks — Shortcut Corridors & Risk/Reward (Step 3)

Step 3 completes the hidden block feature by introducing **perceivable shortcut corridors** — pairs of hidden blocks that form a short secret path, rewarding discovery with bonus coins while remaining non-essential.

### Shortcut Corridors

A **shortcut corridor** is a pair of 2 consecutive hidden blocks placed at staggered heights, forming a secret stepping-stone path. They appear in three chunk types:

- **`single_platform`**: When pipe height >= 130 px, 12% chance. Two hidden blocks placed left of the pipe at 55% and 80% height — a 2-step secret staircase to the pipe top.
- **`pipe_mix`**: When pipe height >= 160 px, 12% chance. Two hidden blocks placed right of the pipe at 50% and 78% height — a shortcut path over the tall pipe.
- **`double_platform`**: When second pipe height >= 120 px and gap >= 150 px, 12% chance. Two hidden blocks bridge the gap between pipes — a secret aerial path.

Shortcuts use the `else` branch of the single hidden block roll, so a chunk gets either a single hidden block **or** a shortcut corridor, never both (except `double_platform` which is independent).

### Risk/Reward Balance

- **Reward**: Each shortcut block awards a **bonus coin** on reveal (in addition to the standard +15 score). Finding both blocks in a corridor gives 2 extra coins — meaningful but not game-breaking.
- **Failure safety**: Missing a shortcut block never causes death. All shortcut blocks are placed above open ground or near safe pipe surfaces. The main route always remains passable.
- **Coin pop feedback**: Shortcut reveals trigger a coin pop animation and SFX on top of the standard SECRET! popup, giving extra positive reinforcement.

### Constants

| Constant | Value | Purpose |
|---|---|---|
| `HIDDEN_SHORTCUT_CHANCE` | `0.12` | Chance per eligible chunk to spawn a 2-block shortcut corridor |
| `HIDDEN_SHORTCUT_COIN` | `true` | Whether shortcut blocks award a bonus coin on reveal |

### Version Display

The title/start screen now shows the game version (`GAME_VERSION` constant, currently `v0.5.2`) below the START button. The version is displayed in small gray text and only appears on the title screen, not on game-over.

## Level Rhythm Sections — Underworld / Tower (Mario List Item 5, Step 1)

A **rhythm section** system overlays on top of the existing theme system, cycling between two distinct level feel modes that alter chunk selection weights and obstacle parameters.

### Section Types

| Section | Feel | Key Characteristics |
|---------|------|---------------------|
| **UNDERWORLD** | Dense, low-pipe corridors | More `single_platform` (1.4×) and `pipe_mix` (1.6×), shorter bottom pipes (−25 px), more ceiling pipes (+15 px maxTopH), more turtles (1.3×). Creates a cramped, ground-level gauntlet. |
| **TOWER** | Vertical platform climbing | More `double_platform` (1.8×), taller bottom pipes (+30 px), fewer ceiling pipes (−15 px maxTopH), fewer turtles (0.4×). Creates a staircase-climbing feel. |

### Section Cycling

- Each section lasts **5–9 chunks** (randomly chosen)
- Sections alternate: UNDERWORLD → TOWER → UNDERWORLD → ...
- On transition, a center-screen announcement appears for ~2 seconds:
  - **`ENTER UNDERWORLD`** — orange text (#ff6644)
  - **`CLIMB TOWER`** — cyan text (#44ccff)

### Relationship to Theme System

Sections and themes are **independent layers** that stack:

1. Base difficulty phase weights → theme weight multipliers → **section weight multipliers**
2. Base difficulty params → theme parameter offsets → **section parameter offsets**

This means a CAVE theme + UNDERWORLD section produces very dense, claustrophobic corridors, while a PLAINS theme + TOWER section gives open vertical climbing with gentle base spacing.

### Weight Multipliers

| Type | UNDERWORLD | TOWER |
|------|------------|-------|
| `rest` | 0.6× | 0.5× |
| `single_platform` | 1.4× | 0.8× |
| `double_platform` | 0.5× | 1.8× |
| `pipe_mix` | 1.6× | 0.7× |
| `turtle_zone` | 1.3× | 0.4× |
| `reward` | 1.0× | 1.3× |

### Parameter Offsets

| Parameter | UNDERWORLD | TOWER |
|-----------|------------|-------|
| `maxPipeH` | −25 px | +30 px |
| `maxTopH` | +15 px | −15 px |

All offsets are clamped to reachability limits (same as theme offsets).

### Reachability Safety

Section biases do **not** bypass any existing safety rules:

- Reachability validation + reroll still runs on every chunk
- Max 2 consecutive danger chunks rule still applies
- Every 5 chunks safe chunk guarantee still applies
- Theme transition softening still applies independently

### Constants

| Constant | Value | Purpose |
|----------|-------|---------|
| `SECTION_MIN_CHUNKS` | `5` | Minimum chunks per section |
| `SECTION_MAX_CHUNKS` | `9` | Maximum chunks per section |
| `SECTION_ANNOUNCE_DURATION` | `120` | Frames to show section announcement (~2s) |

## Section Transition Visual Layer & Difficulty Smoothing (Mario List Item 5, Step 2)

Building on the rhythm section system from Step 1, this step adds a **visual transition flash** when switching between UNDERWORLD and TOWER sections, and **softens the first chunk** of each new section to prevent difficulty spikes at the boundary.

### Visual Transition Flash

When a section switch occurs, a brief color flash overlay appears for ~0.75 seconds:

- **Edge vignette bars** at the top and bottom 8% of the screen, tinted with the section's announce color
- **Subtle full-screen tint** at ~35% of the vignette intensity
- Quick flash-in (first 20% of duration) then smooth fade-out (remaining 80%)
- UNDERWORLD flash: orange (#ff6644), TOWER flash: cyan (#44ccff)

The effect is lightweight — no sprite or asset changes, just a brief atmospheric pulse that signals the environment shift.

### Transition Chunk Difficulty Smoothing

The first chunk spawned in a new section uses blended parameters to avoid a sudden difficulty spike:

- **Weight blending**: section weight multipliers are softened to 40% strength (same approach as theme transitions)
- **Parameter blending**: section parameter offsets (`maxPipeH`, `maxTopH`) are applied at 40% instead of 100%
- **Safety bias**: the first chunk also biases toward safer types (`rest` weight boosted to ≥20, `pipe_mix` ×0.6, `turtle_zone` ×0.5)

This mirrors the existing `themeTransitionActive` pattern, ensuring the player has a brief adjustment period before the full section feel kicks in.

### New Constants

| Constant | Value | Purpose |
|----------|-------|---------|
| `SECTION_FLASH_DURATION` | `45` | Frames for the section flash overlay (~0.75s) |
| `sectionTransitionActive` | `bool` | True during first chunk of a new section |

### Version

Updated `GAME_VERSION` from `v0.5.0` → **`v0.5.1`**.

## Section Final Integration & Polish (Mario List Item 5, Step 3 — Completion)

This step completes the rhythm section system (Item 5 main trunk) with final smoothing, identification polish, and ambient cues.

### 2-Chunk Transition Ramp-In

The transition smoothing from Step 2 (single chunk) is extended to **2 chunks**:

- **Chunk 1** (first after switch): section weights/params blend at 40% strength, strong safety bias (rest ≥30, pipe_mix ×0.6, turtle_zone ×0.5)
- **Chunk 2**: blend increases to 70% strength, lighter safety bias (rest ≥20, pipe_mix ×0.8, turtle_zone ×0.75)
- **Chunk 3+**: full section parameters, no safety override

This eliminates difficulty spikes at section boundaries while keeping the distinct section feel within 2 chunks. Implemented via `sectionTransitionCountdown` (2→1→0) which graduates the blend factor in `applySectionWeights()` and `applySectionParams()`.

### Persistent HUD Section Label

A small label below the level bar shows the current section name (`UNDERWORLD` / `TOWER`):

- Default: subtle gray text (#aaa), 11px monospace
- On section switch: temporarily highlights with the section's announce color and a CSS glow (`text-shadow`) for the duration of the announce timer (~2s), then fades back to gray
- Provides at-a-glance section awareness without cluttering the HUD

### Section Sky Tint

A very subtle full-sky color overlay differentiates sections at the ambient level:

- **UNDERWORLD**: warm amber tint (`rgba(180, 80, 40, 0.06)`)
- **TOWER**: cool blue tint (`rgba(60, 120, 200, 0.06)`)

The tint is applied as a single `fillRect` over the sky gradient (below clouds/hills), barely perceptible but enough to shift the mood between dense underground corridors and open vertical climbs.

### New Variables

| Variable | Type | Purpose |
|----------|------|---------|
| `sectionTransitionCountdown` | `int` | Ramp-in counter: starts at 2, decrements each chunk, drives graduated blend |
| `SECTION_SKY_TINT` | `object` | Per-section rgba sky overlay color |
| `hudSectionLabel` | `element` | Persistent HUD section name label |

### Version

Updated `GAME_VERSION` from `v0.5.1` → **`v0.5.2`**.

## Frame-rate Independent Simulation

The game uses a **fixed timestep** loop to ensure identical physics and game speed regardless of the display's refresh rate. Whether running on a 30 Hz phone, a 60 Hz laptop, or a 144+ Hz gaming monitor, the gameplay experience is the same.

### How It Works

The main loop uses `requestAnimationFrame` with an **accumulator pattern**:

1. Each render frame, the real elapsed wall-clock time (`dt`) is measured.
2. `dt` is added to an accumulator.
3. The game logic (`update()`) runs in fixed increments of **1/60th of a second** (`FIXED_DT = 1/60`) until the accumulator is drained.
4. After all logic steps, a single `draw()` call renders the current state.

```
realDt = (now - lastTimestamp) / 1000   // seconds
accumulator += realDt
while (accumulator >= FIXED_DT):
    update()                             // always 1/60s per call
    accumulator -= FIXED_DT
draw()
```

### Safety Measures

| Measure | Value | Purpose |
|---------|-------|---------|
| `MAX_FRAME_DT` | `0.1s` | Clamp real dt to prevent death spiral when switching back to the tab after being away |
| `MAX_STEPS_PER_FRAME` | `5` | Cap logic steps per render frame; excess accumulator is drained to prevent permanent lag spiral |
| Accumulator reset | On `startGame()` | Prevents stale dt from title/death screen carrying over into gameplay |

### Why Fixed Timestep (Not Delta-Time Scaling)

- **Deterministic**: every `update()` call sees the exact same time step — no floating-point drift from variable `dt` multiplication.
- **Zero constant changes**: all existing physics values (gravity, jump velocity, acceleration, timers) were tuned for 60 FPS and work unmodified.
- **Collision stability**: the swept AABB collision system operates identically every step — no risk of tunneling from large `dt` values.

### Debug Overlay (`?debug=1`)

When debug mode is active, the bottom status area includes:

- `dt:X.Xms` — raw wall-clock time of the last render frame
- `logicSteps:N` — number of `update()` calls executed in the last render frame (typically 1 at 60 Hz, 2 at 30 Hz, 0–1 at 144 Hz)
- `fps(est):X.X` — exponentially smoothed estimate of the display refresh rate

### Expected Behavior at Different Refresh Rates

| Display | Logic steps/frame | Result |
|---------|-------------------|--------|
| 30 Hz | 2 | Two update() calls per draw — game runs at correct speed, slightly choppier animation |
| 60 Hz | 1 | One update() per draw — baseline experience |
| 120 Hz | 0 or 1 (alternating) | Some frames skip logic, some run one step — smooth animation, correct speed |
| 144 Hz | 0 or 1 (alternating) | Same as 120 Hz — no speed increase |
| Tab hidden | 0 (clamped) | dt capped at 100ms, max 5 catch-up steps — no death spiral or teleporting |

## Player Form System — Lives & Hurt State (Mario List Item 6, Step 1)

The player now has two form states: **small** and **big**.

### Form States

| Form | Visual | Behaviour on Hit |
|------|--------|-------------------|
| `small` | Normal size (28×36) | Loses a life / game over (existing death flow) |
| `big` | 1.3× scaled sprite | Downgrades to `small` + ~2s invincibility frames |

### Becoming Big

- Collecting a **mushroom** power-up sets `playerForm = 'big'` (in addition to existing double-jump timer).
- If already `big`, mushroom just refreshes the double-jump timer.

### Hurt / Invincibility Rules

- `big` → hit → becomes `small`, gains **120 frames (~2s)** of invincibility (sprite flashes).
- `small` → hit → existing death/respawn/game-over flow.
- During invincibility frames, all damage sources are ignored.

### Visual Feedback

- **Big form**: player sprite is drawn at 1.3× scale anchored at feet, with a **pulsing golden glow aura** behind the sprite and a **★ BIG** HUD badge with gold text-shadow.
- **Invincibility flicker**: sprite alternates between 90% and 25% opacity with an **adaptive blink rate** — fast (3-frame period) right after being hit, slowing to 8-frame period as invincibility wears off. Player is always partially visible (never fully hidden).
- **Hurt flash**: a brief red screen overlay (8 frames, ~0.13s) on big→small downgrade.
- **Hurt screen shake**: short decaying camera shake (12 frames, ~0.2s) on big→small downgrade.
- **HUD**: `SMALL` (light blue) / `★ BIG` (gold + glow) label shown below the life counter.

### State Resets

- `resetGame()` → `playerForm = 'small'`, `hurtInvincibleTimer = 0`, `hurtShakeTimer = 0`, `hurtFlashTimer = 0`
- `respawnPlayer()` → same resets (form lost on death)

## Form Feel & Hurt Feedback (Mario List Item 6, Step 2)

Step 2 refines the **big/small form system** introduced in Step 1 with enhanced game-feel and clearer feedback.

### BIG State Enhancements

- **Golden glow aura**: subtle pulsing elliptical glow behind the player in BIG form (alpha oscillates 0.07–0.17).
- **+5% speed bonus**: BIG form moves slightly faster (`BIG_SPEED_BONUS = 1.05`), stacking with coin-rush multiplier. Not enough to break balance, but enough to feel powerful.
- **HUD upgrade**: BIG label now shows `★ BIG` in gold with a glowing text-shadow effect.

### Hurt Feedback (big→small)

| Feedback | Duration | Description |
|----------|----------|-------------|
| SFX `sfxHurt()` | ~0.16s | Descending triangle wave (520→220 Hz) + low sine undertone (120 Hz) |
| Haptics `vibHurt()` | ~130ms | Short vibration burst `[60, 30, 40]` |
| Red flash | 8 frames | Full-screen red overlay fading from 22% to 0% opacity |
| Screen shake | 12 frames | Decaying random camera offset (±3px → 0) |

### Improved Invincibility Flicker

The old uniform 4-frame on/off blink is replaced with an **adaptive-rate ghost flicker**:
- Blink period starts at **3 frames** (fast, urgent) and gradually slows to **8 frames** (calm, fading).
- Instead of fully hiding the sprite, the "dim" phase renders at **25% opacity** — player is always visible, avoiding confusion about character position.

## Form & Life Flow Final Integration (Mario List Item 6, Step 3 — Trunk Complete)

Step 3 is the **final consistency pass** for the big/small form system and life cycle, closing out Item 6's main trunk.

### What was audited & fixed

| Flow | Before | After |
|------|--------|-------|
| **big → hurt → small** | Correct: downgrades + invincibility | Unchanged (verified) |
| **small → hurt → respawn** | Respawn granted **no** invincibility — player could be instantly re-killed | Respawn now grants `HURT_INVINCIBLE_FRAMES` (120 frames / ~2 s) of post-respawn invincibility with the same flicker feedback |
| **small → hurt → game over** | Correct: triggers overlay | Unchanged (verified) |
| **Level clear → restart** | `resetGame()` resets form to small, clears all hurt timers | Unchanged (verified) |
| **Game over → restart** | Same `resetGame()` path | Unchanged (verified) |

### Key change

- `respawnPlayer()` now sets `hurtInvincibleTimer = HURT_INVINCIBLE_FRAMES` instead of `0`, so the player gets the same invincibility flicker window after losing a life as after a big→small downgrade. Nearby enemies are still cleared within 200 px as before.

### Version

Updated `GAME_VERSION` from `v0.5.4` → **`v0.5.5`**.

---

## v0.5.6 — Balance Pass

A parameters-only tuning pass to smooth overall feel, reduce frustration, and keep reward feedback readable without adding new systems.

### Movement / Brake
- `BRAKE_DECEL_MIN` 0.10 → **0.12** — snappier tail-end stop, less sluggish
- `BRAKE_DECEL_MAX` 0.60 → **0.55** — softer peak brake for more natural curve
- `AIR_BRAKE_DECEL` 0.30 → **0.25** — air pullback less forceful, more controllable

### Enemy Pressure
- `TURTLE_MIN_SPAWN_GAP` 400 → **440 px** — more breathing room between turtles
- `SPAWN_RHYTHM_RELIEF` 0.40 → **0.45** — longer relief windows in spawn rhythm
- `SHELL_COMBO_MAX` 5 → **4** — cap combo earlier to prevent score explosion
- `SHELL_COMBO_BASE` 20 → **15** — lower base keeps chain rewarding but not game-breaking

### Coin / Question Brick
- `COIN_COMBO_WINDOW` 1.2 → **1.0 s** — combo resets faster, less pitch-spam
- `COIN_COMBO_MAX` 8 → **6** — caps pitch escalation before it gets shrill
- Score popup lifetime 45 → **38 frames** — popups clear faster, less screen clutter

### Hidden Brick / Shortcut
- `HIDDEN_HINT_RANGE` 60 → **50 px** — tighter proximity before sparks appear
- `HIDDEN_HINT_FREQ` 8 → **12 frames** — spark hints more subtle and less frequent
- `HIDDEN_SHORTCUT_CHANCE` 0.12 → **0.10** — slightly rarer shortcuts to preserve surprise

### Life / Form
- `HURT_INVINCIBLE_FRAMES` 120 → **150** (~2 s → 2.5 s) — more recovery time after hit
- `HURT_SHAKE_FRAMES` 12 → **10** — shorter screen-shake, less jarring
- Respawn enemy clear radius 200 → **250 px** — safer respawn zone

### Version

Updated `GAME_VERSION` from `v0.5.5` → **`v0.5.6`**.

---

## v0.6.0 Step 1 — Star Rating & Checkpoint Flag

### Star Rating (Level Clear)
When the player touches the flagpole, a **1–3 star rating** is calculated and displayed on the LEVEL CLEAR overlay:

| Stars | Condition |
|-------|-----------|
| ★☆☆ | Base — cleared the level |
| ★★☆ | Cleared within **120 seconds** |
| ★★★ | Also collected **≥30 coins** OR completed with **zero deaths** |

Star thresholds are tunable via `STAR_TIME_THRESHOLDS` and `STAR_COIN_THRESHOLD` constants.

### Checkpoint Flag
- A **checkpoint flag** is placed at `x = 2500` (roughly mid-level, ~50% of the 5000-unit course)
- First contact triggers `checkpointReached = true` with a "CHECKPOINT!" popup
- The flag visually flips from orange (unactivated) to green (activated)
- On death with `lives > 0`: if the checkpoint was reached and the camera hasn't passed it, the player **respawns at the checkpoint** instead of near the current camera position
- Only a **single checkpoint** per level in this version

### State Tracking
- `deathsThisRun` — counts lives lost (used for star calculation)
- `checkpointReached` / `checkpointActivated` — checkpoint flag state
- All new state resets properly in `startGame()`

### Version

Updated `GAME_VERSION` from `v0.5.6` → **`v0.6.0`**.

---

## v0.6.1 Step 2 — Star Rating Readability & Checkpoint Polish

### Star Rating Source Summary
- The LEVEL CLEAR overlay now shows a **breakdown line** below the stars indicating which criteria were met:
  - `✓ Time ≤120s` / `✗ Time >120s` — whether the time bonus star was earned
  - `✓ Coins ≥30` / `✓ No deaths` / `✗ Coins <30 & died` — whether the coin/flawless star was earned
- The 1–3 star mechanism is **unchanged**; this is a readability improvement only

### Checkpoint Trigger Feedback
- Touching the checkpoint flag now triggers a **green screen flash** (1 second, fading) with large centered "CHECKPOINT!" and "Progress saved" text
- Provides much clearer feedback that progress was saved vs the previous small popup only
- New state variable `checkpointFlashTimer` drives the overlay; resets on `startGame()`

### Checkpoint Respawn Protection
- Respawning at the checkpoint now uses a **wider enemy clear radius** (400px vs 250px) to prevent instant re-kills from enemies near the checkpoint area
- Existing invincibility frames (`HURT_INVINCIBLE_FRAMES = 150`, ~2.5s) remain unchanged

### Version

Updated `GAME_VERSION` from `v0.6.0` → **`v0.6.1`**.

---

## v0.6.2 Step 3 — Star Rating & Checkpoint Final Integration

### Star Rating Display Polish
- Tightened the LEVEL CLEAR overlay layout: reduced font sizes and vertical spacing so it reads cleanly on small/mobile screens without blocking gameplay view
- Star criteria summary is now **compact** (`✓ Time  ✓ Coins` / `✓ No death`) instead of verbose thresholds — less visual clutter while still informative
- 1–3 star calculation logic is **unchanged**

### Checkpoint State Cleanup
- `checkpointFlashTimer` is now **zeroed on level clear** so the green checkpoint flash never bleeds into the LEVEL CLEAR overlay
- All three checkpoint variables (`checkpointReached`, `checkpointActivated`, `checkpointFlashTimer`) continue to reset correctly in `resetGame()`, covering: game-over restart, level-clear restart, and title-screen start
- Verified respawn-at-checkpoint flow (lives > 0) remains intact with wider enemy clear radius

### Checkpoint vs Flagpole Guard
- Checkpoint collision check now also requires `!levelCleared`, preventing any theoretical checkpoint activation during the flagpole slide-down animation
- Flagpole and checkpoint are far apart (2500 vs 5000 world-X) so this is a safety guard, not a bug fix

### Version

Updated `GAME_VERSION` from `v0.6.1` → **`v0.6.2`**.

**Star rating + checkpoint main trunk: complete.**

---

## v0.7.0 Step 2 — UI Flow Unification (Mobile-First)

### UI Full-Chain Consistency
- Unified font sizes across Title / HUD / LEVEL CLEAR screens:
  - Title `h1`: `bold 28px` with `clamp(20px, 5vw, 28px)` floor
  - LEVEL CLEAR title: `bold 28px` (was `bold 32px`) — matches title overlay
  - HUD primary (time, score): `clamp(16px, 4.5vw, 22px)`
  - HUD secondary (level, coin, life): `clamp(13px, 3.5vw, 16px)`
- DAILY label now consistently `12px #8cf` across HUD, title overlay, and clear screen (was 11/13/12px)
- Section label unified to `12px` (was `11px`)
- Score/time format unified to uppercase (`SCORE: / TIME:`) across HUD, LEVEL CLEAR, and Game Over
- `HIGH SCORE:` label unified to uppercase on game-over overlay
- Version (`GAME_VERSION`) now shown on game-over screen as well as title — useful for bug reports

### Interaction Rhythm Unification
- Added `RESTART_GUARD_MS` (500 ms) delay before accepting restart input on both game-over and level-clear screens — prevents accidental taps during screen transitions
- All restart paths (jump, left, right) now go through unified `_canRestart()` guard
- Clear screen restart prompt updated: "Tap or press any key to restart" (was keyboard-only wording)

### Small-Screen Readability
- Overlay container: `max-width: 92vw; max-height: 88vh; overflow-y: auto` — prevents clipping on narrow viewports
- Overlay padding reduced from `32px 48px` to `28px 40px`, gap from `16px` to `12px` for tighter mobile fit
- Leaderboard and achievement font sizes use `clamp(10px, 2.5vw, 12px)` / `clamp(10px, 2.5vw, 11px)` — readable floor on small screens
- LEVEL CLEAR overlay: regularized vertical spacing with uniform `rowH = 24px` between elements (was irregular 30/32/18/20/20)
- Criteria line font bumped from `11px` to `12px` for consistency; "No death" capitalized to "No Death"

### Fallback Text Standardization
- Empty leaderboard: "No runs yet" (unchanged)
- Leaderboard error: "No data" (was "Leaderboard unavailable")
- No rank on clear: "No rank data" (was "Not ranked today")
- All fallback text uses `#888` grey — no color/format variance

### Version
Updated `GAME_VERSION` from `v0.6.9` → **`v0.7.0`**.

---

## v0.7.2 Step 2 — Memory / Object Pool Micro-Optimizations

### Object Pools (GC pressure reduction)
- **Lightweight `createPool()` utility**: generic acquire/release pool with `drainTo()` for free-list capping. Zero dependencies, ~20 LOC
- **Pooled particle systems**: `scorePopups`, `timeBonusPopups`, `fragments` (brick debris), `hintSparks`, and `coinPops` now recycle objects instead of creating new ones each spawn. Dead objects are released back to their pool on removal
- **Pooled collision rects**: `gatherCollisionRects()` (called every frame) now reuses a pre-allocated array and pooled rect objects — eliminates the largest per-frame allocation (previously ~20–40 new objects/frame)
- **Swap-remove instead of splice**: all particle update loops now use swap-and-truncate removal (`arr[i] = arr[--n]; arr.length = n;`) instead of `Array.splice()`, avoiding O(n) shifts
- **Pool cleanup on reset**: `resetGame()` releases all active pooled objects back to free-lists and trims pools to bounded sizes to prevent unbounded memory growth

### Per-Frame Allocation Reduction
- **In-place pipe/brick cleanup**: replaced `pipes.filter()` and `bricks.filter()` (every frame) with in-place compaction loops — zero array allocation
- **Inlined `getPipeRects()` in collision gather**: pipe rect computation is now done directly inside `gatherCollisionRects()`, eliminating 3 intermediate objects per pipe per frame
- **Cached `_timeBonusStr`**: the `+5s` draw string is pre-built once instead of template-literal per popup per frame
- **Hoisted `_fragColors` array**: brick debris color palette moved to module scope (was re-created per `spawnBrickFragments()` call)

### Observability (debug only)
- Added **pool stats line** to `?debug=1` overlay: shows active counts (popups, fragments, sparks, collision rects) and pool free-list sizes — useful for verifying pool reuse without external tooling

### Version
Updated `GAME_VERSION` from `v0.7.1` → **`v0.7.2`**.

---

## v0.7.1 Step 1 — Performance & Smoothness Micro-Optimizations

### Performance (mobile-first)
- **Theme color caching**: `lerpColor()` now short-circuits when `t <= 0` or `t >= 1` (avoids hex parsing when not transitioning). Sky/ground/hill color results are cached per-frame by key — eliminates ~5 redundant `parseInt` + `toString(16)` calls per frame during steady state
- **Sky gradient caching**: `createLinearGradient()` is only called when sky colors actually change, not every frame
- **Off-screen culling**: Pipes, bricks, mushrooms, and turtles are skipped in `draw()` when outside the camera viewport (±64 px margin). Reduces draw calls proportionally to world size
- **HUD DOM throttling**: `textContent` writes are now guarded — only assigned when the value actually changes. Avoids unnecessary DOM layout invalidation for score, coin, life, time, level, theme, and section labels
- **Ground brick loop**: replaced `Math.ceil()` divisions with integer arithmetic for row/column counts
- **Debug turtle stats**: replaced 5 `filter()` allocations with a single-pass loop (only affects `?debug=1` mode)

### Smoothness
- **Consistent frame timing**: replaced all `Date.now()` calls in `draw()` and overlay guards with the rAF timestamp (`_frameNow`). Overlay start times (`clearOverlayStartTime`, `gameOverStartTime`) now use the same clock — eliminates potential timing drift between `Date.now()` and `performance.now()` on mobile
- **Star measurement cache**: `measureText()` for the clear-overlay star characters is now cached (font is constant) — avoids a font-metric lookup every frame during the level-clear sequence

### Observability (debug only)
- Added **`drawMs`** (EMA-smoothed draw render time in ms) to the existing `?debug=1` panel alongside dt/fps/logicSteps — useful for identifying frame-budget pressure without external tools

### Version
Updated `GAME_VERSION` from `v0.7.0` → **`v0.7.1`**.

---

## v0.6.9 Step 1 — Clear Screen Animation Polish

### LEVEL CLEAR Overlay — Entrance Animations
- All overlay elements now fade/scale in sequentially instead of appearing instantly
- **Background overlay** fades from transparent to 50% black over 200 ms
- **"LEVEL CLEAR!" title** eases in over 0–300 ms (ease-out cubic)
- **Score & time** fades in 150–450 ms
- **Star rating**: each star enters individually with staggered scale+fade (350 ms base, 200 ms stagger per star, scaling from 50%→100%)
- **Criteria summary** fades in after all stars have appeared
- **Daily ranking text** fades in with additional 200 ms delay after criteria
- **Restart prompt** delayed until all info is visible, then soft fade-in over 400 ms

### NEW Badge Unlock — Highlight Pulse
- Newly unlocked badges now enter with a **bright gold flash** that decays to a gentle settled pulse
- Initial entrance includes a subtle **scale pop** (1.15×→1.0×) for tactile feel
- Flash decays over 500 ms then settles into a soft 0.8±0.1 alpha oscillation — not distracting
- Non-intrusive: no overlay, no blocking, fits within existing layout flow

### Timing & Feel
- Clear-to-restart flow is smoother: elements cascade in naturally over ~1.5 s
- Restart prompt only appears after all information has settled (varies by badge count)
- No changes to core gameplay timing, balance, or enemy rules

### Stability
- New `clearOverlayStartTime` variable tracks overlay entrance; reset in `resetGame()`
- No lingering timers or requestAnimationFrame — all animation driven by elapsed-time delta
- All existing localStorage fallbacks preserved
- Works correctly across start / restart / game-over flows

### Version
Updated `GAME_VERSION` from `v0.6.8` → **`v0.6.9`**.

---

## v0.6.8 Step 3 — Achievement System Final Polish + Clear Screen Layout

### Achievement System Polish
- Verified all 4 badge conditions match their descriptions and are correctly triggered:
  | Badge | Condition | Code check |
  |---|---|---|
  | **First Clear** | Clear the level for the first time | `unlockAchievement('FIRST_CLEAR')` on every clear |
  | **Three Stars** | Earn 3 stars in a single run | `levelClearStars === 3` |
  | **No Death** | Clear with 0 deaths | `deathsThisRun === 0` |
  | **No Checkpoint** | Clear without using checkpoint | `!checkpointActivated` |
- **Save compatibility**: old `SPEED_RUNNER` key (from v0.6.6) is silently removed on load — no stale badges
- `getUnlockedCount()` now filters against `ACHIEVEMENTS` keys, preventing phantom counts from legacy data
- All localStorage operations remain fully try/catch wrapped — storage failure never blocks gameplay

### LEVEL CLEAR Screen — Layout Overhaul (Mobile-First)
- Replaced fixed `cy +/- offset` layout with a `ly` (layout-Y) cursor that flows top-to-bottom
- Increased vertical spacing between each info block (stars → criteria → rank → badges → prompt)
- Slightly darker overlay backdrop (`0.5` alpha) for better text contrast on bright levels
- "Press any key" prompt now auto-positions after the last visible element — no overlap with badge line
- Restart prompt dimmed to `#aaa` to avoid competing with the gold badge notification

### Title Screen Badge Area Polish
- Unlocked badges now use ★ (filled star) in gold `#ffd700` instead of ✓
- Locked badges use ☆ (hollow star) in `#777` with em-dash separator for description
- When all 4 badges are unlocked, summary turns gold with "★ All 4 Badges Unlocked!" text
- Increased `line-height` from 1.5 → 1.7 and top margin from 6 → 8 px for better readability
- Summary-to-list gap increased from 2 → 4 px

### Stability
- No changes to core gameplay, balance, or level generation
- All existing localStorage fallbacks preserved
- `newlyUnlockedBadges` reset paths unchanged

### Version
Updated `GAME_VERSION` from `v0.6.7` → **`v0.6.8`**.

**Achievement system main trunk: complete.**

---

## v0.6.7 Step 2 — 4th Badge Challenge + Unlock Feedback

### 4th Badge → No Checkpoint
- Replaced **Speed Runner** (≤90s) with a more challenging badge: **No Checkpoint** — clear the level without activating the checkpoint flag
- Updated badge table:
  | Badge | Condition |
  |---|---|
  | **First Clear** | Clear the level for the first time |
  | **Three Stars** | Earn 3 stars in a single run |
  | **No Death** | Clear with 0 deaths |
  | **No Checkpoint** | Clear without using checkpoint |

### Badge Unlock Feedback on LEVEL CLEAR
- When new badges are unlocked during a clear, a gold pulsing text line shows on the clear screen (e.g. "🏅 NEW: No Death, No Checkpoint")
- Gentle opacity pulse animation; restart prompt shifts down to make room
- If no new badges, nothing is shown — no clutter

### Title Screen Badge Display
- Unlocked badges now shown in **gold** (`#ffd700`) with ✓ prefix
- Locked badges shown in **dark grey** (`#666`) with ☐ prefix and description hint
- Makes it easy to distinguish earned vs remaining at a glance

### Stability
- `newlyUnlockedBadges` properly reset in `resetGame()`
- All localStorage operations remain try/catch wrapped
- No changes to core gameplay or balance

### Version
Updated `GAME_VERSION` from `v0.6.6` → **`v0.6.7`**.

---

## v0.6.6 Step 1 — Clear Screen Ranking + Local Achievement Badges

### Level Clear Screen — Ranking Info
- After touching the flagpole, the LEVEL CLEAR overlay now shows **today's rank** (e.g. "Today #2") and the **score gap from #1**
- If the run didn't make the top 5, shows "Not ranked today"
- Layout shifted to accommodate the new line while remaining readable on mobile

### Local Achievement Badges (localStorage)
- 4 verifiable badges stored in `localStorage` (`plumber_runner_ach`):
  | Badge | Condition |
  |---|---|
  | **First Clear** | Clear the level for the first time |
  | **Three Stars** | Earn 3 stars in a single run |
  | **No Death** | Clear with 0 deaths |
  | **Speed Runner** | Clear in ≤90 seconds |
- Badges persist across sessions; unlocked once and never lost
- Title screen shows "Badges: X/4 unlocked" summary with a per-badge checklist

### Stability
- All achievement read/write operations wrapped in try/catch — storage failure never blocks gameplay
- `clearRankInfo` properly reset in `resetGame()` to prevent stale data

### Version
Updated `GAME_VERSION` from `v0.6.5` → **`v0.6.6`**.

---

## v0.6.5 Step 3 — Daily Seed + Local Leaderboard Final Integration

### Daily Seed Polish
- `DAILY_DATE` / `DAILY_SEED` are now `let` — if the browser tab stays open past midnight, `refreshDailyIfNeeded()` detects the date change and updates the seed before the next game starts
- HUD and title overlay always display the current `DAILY_DATE`, never a stale value
- Same-day determinism and cross-day variation verified end-to-end

### Leaderboard UI Polish
- Bumped leaderboard font from 11 → 12 px and line-height from 1.5 → 1.6 for better mobile readability
- Clear Today button padding and font increased slightly for easier tap targets
- `renderTitleLeaderboard()` now validates each entry (`score` must be a number, `stars` clamped 0–3, `time` coerced safely)
- If all entries are invalid, shows "No runs yet" instead of an empty list

### localStorage Fallback
- `addLeaderboardEntry()` fully wrapped in try/catch — storage failure never blocks gameplay
- `renderTitleLeaderboard()` catches any exception and displays "Leaderboard unavailable" gracefully
- Existing guards in `loadLeaderboard`, `saveLeaderboard`, `clearTodayLeaderboard` preserved

### Version

Updated `GAME_VERSION` from `v0.6.4` → **`v0.6.5`**.

**Daily Seed + local leaderboard main trunk: complete.**

---

## v0.6.4 Step 2 — Leaderboard UI & Clear Today

### Leaderboard UI (Title Screen)
- Title screen now shows **Today Top 5** entries with rank, score, time, and star rating
- Uses compact monospace layout (`#1  1234pts  02:15  ★★☆`)
- When no runs exist for today, shows "No runs yet" in gray
- Positioned between the daily date and START button; does not obscure gameplay controls

### Clear Today's Leaderboard
- A small **"Clear Today"** button appears below the leaderboard when entries exist
- Clicking it removes only the current day's (`YYYY-MM-DD`) data from `localStorage`
- Other days' data is unaffected; UI refreshes immediately after clearing
- Button is hidden when there are no entries

### Stability
- `loadLeaderboard()` now validates parsed data type (rejects non-object/array corruption)
- All `localStorage` read/write operations wrapped in try/catch — game never crashes on storage failure

### Version

Updated `GAME_VERSION` from `v0.6.3` → **`v0.6.4`**.

---

## v0.6.3 Step 1 — Daily Seed & Local Leaderboard

### Daily Seed (Deterministic RNG)
- Every day generates a **daily seed** from the local date string `YYYY-MM-DD`
- All level generation (chunk types, pipe heights, brick placement, theme/section rotation, boss wave obstacles, missions) uses a **seeded PRNG** (Mulberry32) instead of `Math.random()`
- The RNG is **reset on each game start**, so the same day always produces the same level layout
- Cosmetic effects (brick fragments, screen shake, cloud drift) remain non-deterministic for visual variety
- **HUD** displays `DAILY: YYYY-MM-DD` in the top-left corner
- **Title screen** also shows the current daily date

### Local Leaderboard (localStorage)
- On **level clear**, the player's run is recorded to `localStorage`:
  - Fields: `date`, `score`, `time`, `stars`
- Only the **top 5 entries per day** are kept, sorted by score (desc) then time (asc)
- Old dates are pruned automatically (last 7 days retained)
- The **title screen** shows the current day's #1 score summary (score, time, stars)
- No network calls — fully local and offline

### Version

Updated `GAME_VERSION` from `v0.6.2` → **`v0.6.3`**.

---

## v0.8.3 Step 1 — Set-Piece Readability Cue Micro-Enhancement

### Design Intent
Adds lightweight visual cues so players can faster read **what each set-piece segment is testing** — without changing any difficulty, collision, or enemy parameters. Follows two principles: (1) cues hint at structure, never spoil the answer, and (2) nothing should obscure the play area on mobile screens.

### Teach / Remix / Exam Role Cues

| Layer | What's Added | Purpose |
|-------|-------------|---------|
| **HUD announcement** | Sub-text hint line below the `★ ROLE: FAMILY ★` banner — "LEARN THE PATTERN" (teach), "MIXED SIGNALS" (remix), "PROVE IT" (exam) | Instantly communicates the pedagogical intent of the segment |
| **Ground edge stripe** | Thin (3px) semi-transparent colored stripe across the full set-piece width on the ground surface — green/orange/red matching role | Peripheral spatial cue marking set-piece boundaries without blocking gameplay |
| **Ground entry symbol** | Small role-specific glyph at the set-piece start: ● (teach), ~ ~ (remix), ▶▶▶ (exam) | Readable at a glance; signals escalation within a sequence |

### Fake-Safe / Anti-Pattern Pre-Warning

| What | Where | Cue |
|------|-------|-----|
| **Anti-pattern zones** (height reversals) | All exam chunks | Small ⚠ triangle at ~15% into the chunk, gold color, 40% opacity |
| **Fake-safe zones** (calm intro → sudden spike) | Precision remix, corridor remix | Same ⚠ triangle — warns "something is off" without revealing the trap |

### Timing
- Announcement duration extended from 75 → 90 frames (~1.25s → ~1.5s) to accommodate the two-line display

### Fairness (Unchanged)
- **No chunk parameters changed** — pipe heights, spacing, widths, speeds all identical to v0.8.2
- **No enemy or collision rule changes**
- **No reachability or difficulty curve changes**
- Ground markers are purely decorative (no gameplay effect)

### Version
Updated `GAME_VERSION` from `v0.8.2` → **`v0.8.3`**.

---

## v0.8.2 Step 3 — Set-Piece Sequence Polish & Failure Hotspot De-Spike

### Design Intent
Finishing pass on the teach → remix → exam sequence system. Focus areas: smoother exam entry/exit transitions (reduces "sudden death" feel), softened failure hotspots where extreme pipe heights + exit turtles created unfair spike combos, and a more stable post-exam breather window that eases players back into normal difficulty. **Core challenge and Lost Levels precision philosophy are preserved** — only the sharpest edges are filed down.

### Exam Transition Polish
- All 4 exam generators (staircase, corridor, precision, ladder) widened from 900 → 950px, giving more entry run-up and exit buffer space
- Entry obstacles pulled slightly inward — first obstacle is further from chunk start
- Exit turtles pushed 30–50px further out — visible earlier, punishes less by ambush

### Failure Hotspot De-Spike
- **Staircase exam**: peak pipe 130 → 120, descent pipe 90 → 85 (more margin from jump cap)
- **Corridor exam**: passage gap widened from 50 → 58px clearance; bottom pipes softened (65/85/60 → 60/80/55)
- **Precision exam**: tallest pipe 130 → 120 (still demands full jump, but not at theoretical max)
- **Ladder exam**: peak1 120 → 115, peak2 140 → 130 (was dangerously close to CHUNK_PLAYER_MAX_JUMP_H=150)

### Post-Exam Breather Stability
- Breather set-piece widened from 700 → 800px with 5 reward bricks (was 4), longer recovery feel
- **Post-breather protection window**: after breather, next 2 normal chunks have suppressed danger weights (pipe_mix ×0.3, double_platform ×0.4, rest/single_platform boosted) — prevents immediate re-spike
- Protection counter (`postBreatherProtection`) auto-decrements and resets on game init

### Fairness Protections (Unchanged)
- Reachability validation still runs on all set-pieces
- Danger counter resets on teach/breather unchanged
- No collision, enemy, or physics rule changes

### Version
Updated `GAME_VERSION` from `v0.8.1` → **`v0.8.2`**.

---

## v0.8.1 Step 2 — Set-Piece Sequence Orchestrator (teach → remix → exam)

### Design Intent
Evolves the v0.8.0 set-piece system from isolated hand-crafted chunks into **structured learning sequences** inspired by Super Mario Bros. 2 (JP) / Lost Levels. Each sequence follows a **teach → remix → exam** arc within a single technique family, creating a rhythm of escalating challenge that rewards player adaptation.

### Sequence Structure
Each run generates **1–2 complete sequences**. A single sequence consists of 4 consecutive set-piece slots:

| Phase | Purpose | Characteristics |
|-------|---------|-----------------|
| **TEACH** | Introduce a single technique with low risk | Generous spacing, gentle heights, no enemies, helper bricks |
| **REMIX** | Same technique with added interference | Tighter spacing, steeper heights, turtle patrols, rhythm disruption |
| **EXAM** | Short combined skill check using the same technique | Anti-pattern heights, minimal helpers, turtle at exit, precision required |
| **BREATHER** | Mandatory recovery after exam | Flat ground, generous brick rewards, no threats |

### Technique Families (4 families × 3 roles)

| Family | TEACH | REMIX | EXAM |
|--------|-------|-------|------|
| **STAIRCASE** | 3 gentle ascending pipes (45/75/105), wide spacing | Steeper pipes (55/90/125), tighter spacing, turtle between steps | 4-step up-then-down reversal (50/90/130/90), turtle at exit |
| **CORRIDOR** | Single bottom+ceiling pipe pair, wide passage | 2 corridor pairs, offset ceilings, turtle between | 3 rapid-fire corridors, anti-pattern heights, reversed middle ceiling |
| **PRECISION** | 2 measured-height pipes with helper brick | Fake-safe intro → sudden tall pipe → rhythm-break pipe, turtle | High-low-high-low alternation (110/50/130/65), Lost Levels signature |
| **LADDER** | Gentle brick staircase to 110px pipe | Steeper ladder to 130px pipe, turtle at base forcing committed timing | Double-peak climb with gap bridge, second peak near jump limit |

### Lost Levels Style Alignment
- **Precision over spectacle**: challenges demand exact jump timing and height reading, not flashy new mechanics
- **Anti-pattern traps**: exam phases use height reversals (tall→short→tall) that punish autopilot
- **Fake-safe elements**: remix phases include calm intros before sudden challenges
- **Rhythm pressure**: turtle placement disrupts comfortable jump cadences
- **No new items/enemies**: difficulty comes purely from obstacle arrangement and timing

### Fairness Protections
- **Mandatory breather**: every exam is followed by a breather set-piece (flat ground, reward bricks)
- **Reachability validation**: all set-pieces pass `validateChunkReachability()` — if validation fails, the set-piece is skipped and normal generation takes over
- **Phase gating**: corridor family requires Phase 1 (60s+) for remix/exam roles
- **Danger counter reset**: teach and breather phases reset the consecutive-danger and chunks-since-safe counters
- **No core rule changes**: collision, enemy behavior, and physics remain identical

### HUD Cue
- Set-piece announcement now shows role prefix: `★ TEACH: STAIRCASE ★`, `★ REMIX: CORRIDOR ★`, `★ EXAM: PRECISION ★`
- Role-specific colors: TEACH = green (#88ee44), REMIX = orange (#ffaa22), EXAM = red (#ff4466), BREATHER = green (#88ee44)
- Same fade pattern as before (75 frames ≈ 1.25s)
- No new art assets

### Scheduling Rules
- **1–2 sequences per run** (randomized at game start)
- **Grace period**: first 5 chunks are set-piece-free
- **Intra-sequence spacing**: 2–3 chunks between teach/remix/exam within a sequence
- **Inter-sequence gap**: 5–7 chunks between sequences
- **Breather immediately follows exam** (1-chunk gap)

### Version
Updated `GAME_VERSION` from `v0.8.0` → **`v0.8.1`**.

---

## v0.8.0 Step 1 — Set-Piece Chunk System (Level Language Upgrade)

### Design Intent
Upgrades the level generation from pure random template sampling to **intentional chunk sequences**. Inspired by Mario-style level design philosophy (teach → remix → exam), hand-crafted "set-piece" chunks are injected periodically into the procedural flow, giving each run recognizable moments and rhythm.

### Set-Piece Types (6 types)

| ID | Name | Description | Unlock Phase |
|----|------|-------------|-------------|
| `staircase_jump` | STAIRCASE | 3 pipes at ascending heights with stepping bricks — teaches reading height differences | Phase 0 (0s) |
| `risk_shortcut` | SHORTCUT | Safe ground path vs optional high path with extra rewards — rewards risk-takers | Phase 0 (0s) |
| `pressure_corridor` | CORRIDOR | Tight section with ceiling + floor pipes creating passages — pressure reading | Phase 1 (60s) |
| `fake_safe` | FAKE SAFE | Looks calm (low bricks, inviting spacing) but hides a mid-height pipe + turtle — teaches attention | Phase 1 (60s) |
| `vertical_ladder` | LADDER | Stepping bricks forming a vertical climb to a tall pipe summit — vertical skill check | Phase 0 (0s) |
| `breather` | BREATHER | Pure flat ground with generous brick row — deliberate pace reset / recovery zone | Phase 0 (0s) |

### Insertion Rules
- **3–5 set-pieces per run** (randomized count at game start)
- **Schedule built at init**: chunk indices are pre-computed with minimum 4-chunk spacing
- **Grace period**: no set-pieces in the first 5 chunks (safe ramp-up)
- **Phase-gated**: each set-piece has a `minPhase` — harder types only appear after the player has survived long enough
- **Reachability validated**: every set-piece passes the same `validateChunkReachability()` check as normal chunks; if it fails, falls through to normal generation
- **Integrates with existing systems**: set-pieces receive theme/section parameter offsets (pipe heights etc.) and respect the theme turtle chance multiplier

### Visual Cue
- Set-piece start triggers a brief HUD announcement: `★ NAME ★` in the set-piece's signature color
- Uses the same fade-out pattern as theme/section announcements (75 frames ≈ 1.25s)
- No new art assets — text-only overlay

### Version
Updated `GAME_VERSION` from `v0.7.2` → **`v0.8.0`**.

---

## Asset & License Information

**The game supports both procedural rendering (code-drawn) and sprite sheet rendering.** The bundled sprite sheet is an original creation matching the procedural character.

- All visual assets are **original pixel art** — either rendered via JavaScript/Canvas code or provided as the bundled sprite sheet
- The player character **"Pippo"** is a fully **original pixel art plumber** with red cap, mustache, and overalls — designed from scratch, not derived from any Nintendo or other copyrighted IP
- **No Nintendo sprites, Super Mario assets, or any third-party copyrighted materials are used anywhere in this project**
- All 5 animation states (idle, run, jump_up, fall, land) are hand-crafted with multi-frame animation
- The game concept (side-scrolling runner with pipe obstacles) is a generic game mechanic not subject to copyright

### License

This project is released under **MIT License**. All code and procedurally generated assets are original work.
