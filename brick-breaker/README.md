# Breakout - 敲磚塊遊戲

A classic Breakout game built with pure HTML5 Canvas and JavaScript. No external dependencies.

## How to Play

- Use the **paddle** to bounce the **ball** and destroy all **bricks**.
- Each brick awards points based on its color (top rows = more points).
- You have **3 lives**. Losing the ball off the bottom costs one life.
- Clear all bricks to win!

### Scoring

| Color | Points |
|-------|--------|
| Red | 30 |
| Orange | 20 |
| Yellow | 20 |
| Green | 10 |
| Cyan | 10 |
| Purple | 10 |

## Controls

| Platform | Action | Control |
|----------|--------|---------|
| Desktop | Move paddle | Arrow keys (Left/Right) or A/D |
| Desktop | Launch ball | Space or Arrow Up |
| Desktop | Move paddle | Mouse movement |
| Mobile | Move paddle | Touch and drag |
| Mobile | Launch ball | Tap anywhere |

## Run Locally

Open `index.html` in any modern browser. No server required.

```bash
# or use a simple server
python3 -m http.server 8000
# then visit http://localhost:8000
```

## Deploy to GitHub Pages

1. Push this folder to a GitHub repository.
2. Go to **Settings > Pages**.
3. Under **Source**, select the branch (e.g. `main`) and folder (e.g. `/` or `/docs`).
4. Click **Save**. Your game will be live at `https://<username>.github.io/<repo>/brick-breaker/`.

If this folder is inside a larger repo (e.g. `games/brick-breaker/`), the URL will be:
```
https://<username>.github.io/games/brick-breaker/
```
