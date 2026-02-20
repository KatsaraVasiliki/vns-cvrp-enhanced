# CVRP — Variable Neighborhood Search

A Python implementation of an Enhanced Variable Neighborhood Search (VNS) for the **Capacitated Vehicle Routing Problem (CVRP)**.

---

## Project Structure

```
cvrp-vns/
├── main.py                  # Entry point — configure and run here
├── config.py                # Algorithm parameters
├── requirements.txt
├── data/
│   ├── instances/           # .vrp input files (TSPLIB format)
│   └── solutions/           # .sol best-known solution files (optional)
├── results/                 # Auto-created — output .sol, .png, .mp4
└── src/
    ├── parser.py            # parse_vrp, parse_sol
    ├── utils.py             # Distance matrix, cost helpers
    ├── construction.py      # Initial solution heuristics
    ├── neighborhoods.py     # N1–N6 local search operators
    ├── shaking.py           # VNS shaking perturbations
    ├── vnd.py               # Variable Neighborhood Descent
    ├── vns.py               # VNS solver (main algorithm)
    ├── animation.py         # MP4 recorder (requires ffmpeg)
    └── visualization.py     # Static plot + .sol writer
```

---

## Installation

```bash
pip install -r requirements.txt
```

For animation export, **ffmpeg** must be installed and on your PATH:
- macOS: `brew install ffmpeg`
- Ubuntu: `sudo apt install ffmpeg`
- Windows: download from https://ffmpeg.org or from PowerShell or Command Prompt `winget install Gyan.FFmpeg`

---

## Usage

1. Place your `.vrp` file in `data/instances/` and (optionally) the best-known `.sol` in `data/solutions/`.
2. Edit the `instances` list and flags at the top of `main.py`.
3. Run:

```bash
python main.py
```

Output files are written to `results/`.

---

## Configuration (`main.py`)

| Flag | Default | Description |
|---|---|---|
| `CONSTRUCTION_METHOD` | `Clarke-Wright` | Initial solution heuristic |
| `USE_OR_OPT` | `False` | Enable Or-opt in VND (slower but stronger) |
| `ENABLE_ANIMATION` | `False` | Record MP4 of improvement steps |

**Construction methods:** `Clarke-Wright`, `nearest_neighbor`, `greedy`, `cheapest_insertion`, `random`

---

## Algorithm Overview

### VNS Loop
```
1. Build initial solution (construction heuristic)
2. Apply VND (Variable Neighborhood Descent)
3. Repeat until budget exhausted:
   a. Shake current best solution (perturbation)
   b. Check tabu list — skip if already visited
   c. Apply VND to shaken solution
   d. Accept if cost improves or fewer routes with same cost
   e. Add accepted solution to tabu list
```

### Neighborhoods (VND order)
| ID | Name | Type |
|---|---|---|
| N1 | 2-opt | Intra-route |
| N5 | Merge routes | Inter-route |
| N2 | Relocate | Inter-route |
| N3 | Swap | Inter-route |
| N4 | 2-opt | Inter-route |
| N6 | Or-opt (optional) | Both |

### Shaking Operators
| ID | Name | Effect |
|---|---|---|
| S1 | Random Relocate | Move k random customers |
| S2 | Random Swap | Swap k random customer pairs |
| S3 | Double Bridge | Reverse k random segments |

---

## Instance Format (TSPLIB)

```
NAME : example
COMMENT : Example instance
TYPE : CVRP
DIMENSION : 5
CAPACITY : 100
NODE_COORD_SECTION
1 0 0
2 10 5
...
DEMAND_SECTION
1 0
2 30
...
DEPOT_SECTION
1
EOF
```


