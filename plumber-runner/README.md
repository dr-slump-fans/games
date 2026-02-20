# Plumber Runner

A retro-style side-scrolling runner game playable in the browser (desktop & mobile).

## How to Play

The screen scrolls automatically to the right. Your character runs forward on their own — your only control is **jumping**.

- **Tap / hold** to jump higher (variable jump height)
- You can **stand on top of pipes** — pipe tops are platforms!
- **Side collisions push you back** instead of killing you instantly
- You die when you get **crushed/squeezed** between obstacles:
  - Pushed off the left edge of the screen by a pipe
  - Squeezed between a bottom pipe and a ceiling pipe
  - Pinned between a ceiling pipe and the ground
- Your score increases each time you clear a pipe
- The game speeds up over time!

## Obstacle Types

| Type | Description |
|------|-------------|
| Bottom pipe | Rises from the ground — you can jump over **or stand on top** |
| Ceiling pipe | Hangs from the top — duck under or time your jump carefully |
| Pipe pair | Bottom + ceiling pipe together — navigate through the gap |

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
| Desktop  | `Space` or `Arrow Up` — hold for higher jump |
| Mobile   | Touch & hold anywhere on screen |

## Running

Open `index.html` in any modern browser. No build step, no server, no CDN required.

Works on GitHub Pages — just push and visit:
```
https://<username>.github.io/<repo>/plumber-runner/
```

## Asset & License Information

**All game assets (character, pipes, ground, clouds, hills) are drawn programmatically on the HTML5 Canvas at runtime.** No external sprite sheets, images, or fonts are used.

- All visual assets are **original pixel art** rendered via JavaScript/Canvas code
- The player character is an **original goggle-wearing adventurer** — not derived from any Nintendo or other copyrighted IP
- No Nintendo, Super Mario, or other copyrighted materials are used
- The game concept (side-scrolling runner with pipe obstacles) is a generic game mechanic not subject to copyright

### License

This project is released under **MIT License**. All code and procedurally generated assets are original work.
