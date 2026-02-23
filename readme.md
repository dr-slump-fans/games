test 2

## Plumber Runner - Bug Fixes

### Fix: Player cannot recenter at high scroll speeds
- Recenter lerp factor and minimum recovery speed now scale with `scrollSpeed / SCROLL_SPEED_BASE`.
- At base speed the behavior is identical (factor 0.12, min 0.5px/frame).
- At higher difficulties the recovery is proportionally faster (capped at factor 0.45) so the player reliably returns to the ~40% target position.

### Fix: Double jump fails when jumping from brick/pipe platforms
- Added `justJumped` flag that is set on the frame a ground jump initiates.
- Swept AABB collision and depenetration skip re-grounding (`onGround = true`) during that frame, ensuring the player properly transitions to airborne.
- This guarantees that a subsequent air press correctly triggers the double jump from any surface (ground, pipe top, brick top) when the mushroom buff is active.

### Mushroom feel restored to early version + anti-instant-eat protection
- Mushroom pop velocity restored to `-3` (from `-7`) for the original gentle arc.
- Physics collisions (pipe/brick bounce, ground) now always active — no longer skipped during grace.
- Grace period reduced to 12 frames (~0.2s) and only blocks pickup, preventing instant collection on spawn.
- Random spawn direction (v1) instead of player-seeking direction.
- Removed aggressive spawn-position shifting that pushed mushroom far from brick.
- Retained enlarged + swept pickup detection (v2) for reliable collection at speed.
