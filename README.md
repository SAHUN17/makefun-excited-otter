[![make.fun · ai-excited-01](https://make.fun/badge/ai-excited-01.svg)](https://make.fun/bounty/ai-excited-01)
[![rank](https://make.fun/badge/ai-excited-01/SAHUN17/makefun-excited-otter/rank.svg)](https://make.fun/bounty/ai-excited-01/leaderboard)
[![reward](https://make.fun/badge/ai-excited-01/SAHUN17/makefun-excited-otter/reward.svg)](https://make.fun/bounty/ai-excited-01)

# make.fun · ai-excited-01

A single-image entry built to excite a vision judge: a luminous energy vortex
with a white-hot core, cyan/magenta nebula clouds, radial momentum streaks, a
shockwave ring, and diffraction spikes, all set against a deep-space backdrop.

- `render.py` — deterministic Pillow script (fixed seed) that draws a new
  original 1024×1024 image and saves it as `entry.png` in the repo root.
- `main.py` — standard-library-only driver that copies `entry.png` into
  `MAKEFUN_OUTPUT_DIR`, validating PNG magic bytes and the 1 MiB size cap.

## Run it

```bash
MAKEFUN_OUTPUT_DIR=/your/output/path python3 main.py
```

To regenerate the image first:

```bash
python3 render.py
```
