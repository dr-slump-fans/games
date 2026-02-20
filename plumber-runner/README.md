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

## Animation States

The player character has a state machine that drives distinct visual poses based on physics:

| State | Trigger | Visual |
|-------|---------|--------|
| `run` | On ground, not landing | 4-frame run cycle — arms and legs alternate |
| `jump_up` | Airborne with upward velocity (`vy < -0.5`) | Arms raised, legs tucked, hair blown upward |
| `fall` | Airborne with downward velocity (`vy >= -0.5`) | Arms spread wide, legs dangling |
| `land` | Just touched ground after being airborne | 6-frame squash pose with dust puffs |

Transitions happen automatically every frame in `updateAnimState()`:
- **Ground → Air**: jump sets `onGround = false` → state becomes `jump_up`
- **Rising → Falling**: when `vy` crosses the threshold → state becomes `fall`
- **Air → Ground**: landing detected via `wasOnGround` flag → state becomes `land` for 6 frames
- **Land → Run**: after land timer expires → state becomes `run`

## Controls

| Platform | Action |
|----------|--------|
| Desktop  | `Space` or `Arrow Up` — tap for small jump, hold for high jump |
| Mobile   | Touch anywhere — tap for small jump, hold for high jump |

## Running

Open `index.html` in any modern browser. No build step, no server, no CDN required.

Works on GitHub Pages — just push and visit:
```
https://<username>.github.io/<repo>/plumber-runner/
```

## Asset & License Information

**All game assets (character, pipes, ground, clouds, hills, breakable bricks, debris fragments) are drawn programmatically on the HTML5 Canvas at runtime.** No external sprite sheets, images, or fonts are used.

- All visual assets are **original pixel art** rendered via JavaScript/Canvas code
- The player character is an **original goggle-wearing adventurer** — not derived from any Nintendo or other copyrighted IP
- No Nintendo, Super Mario, or other copyrighted materials are used
- The game concept (side-scrolling runner with pipe obstacles) is a generic game mechanic not subject to copyright

### License

This project is released under **MIT License**. All code and procedurally generated assets are original work.
