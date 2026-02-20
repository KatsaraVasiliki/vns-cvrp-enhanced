# -*- coding: utf-8 -*-
"""
Configuration and default parameters for the VNS-CVRP solver.
"""

# VNS Parameters
K_MAX = 5                    # Maximum shaking neighborhood size
DEFAULT_MAX_ITER = 1000      # Default maximum iterations
DEFAULT_MAX_TIME = 600       # Default maximum time in seconds

# Tabu list
TABU_TENURE_MIN = 10
TABU_TENURE_MAX = 20

# Early stopping
PATIENCE_MIN = 300
PATIENCE_MAX = 300

# Construction method options
CONSTRUCTION_METHODS = [
    'Clarke-Wright',
    'nearest_neighbor',
    'greedy',
    'cheapest_insertion',
    'random'
]

# Neighborhood improvement threshold
IMPROVEMENT_THRESHOLD = 0.001

# Animation
DEFAULT_FPS = 2
DEFAULT_ANIMATION_FILENAME = "vns_animation.mp4"

# Output
DEFAULT_PLOT_DPI = 300
