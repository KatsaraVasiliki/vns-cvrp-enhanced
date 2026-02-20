# -*- coding: utf-8 -*-
"""
Visualization and solution output utilities.
"""

import matplotlib.pyplot as plt
from config import DEFAULT_PLOT_DPI


def plot_solution(coords, solution, title="CVRP Solution", save_filename=None):
    """
    Plot routes on a 2D map.

    Parameters
    ----------
    coords        : list of (x, y) tuples
    solution      : list of routes (each route is a list of node indices)
    title         : plot title
    save_filename : if provided, save the figure to this path
    """
    plt.figure(figsize=(12, 10))

    # Depot
    plt.scatter(
        coords[0][0], coords[0][1],
        c="red", marker="s", s=300,
        label="Depot", zorder=3,
        edgecolors='black', linewidths=2,
    )

    # Customers
    for i in range(1, len(coords)):
        plt.scatter(
            coords[i][0], coords[i][1],
            c="lightblue", s=80, zorder=2,
            edgecolors='black', linewidths=1,
        )

    # Routes
    colors = plt.cm.tab20.colors
    for i, route in enumerate(solution):
        xs = [coords[c][0] for c in route]
        ys = [coords[c][1] for c in route]
        plt.plot(xs, ys, color=colors[i % len(colors)],
                 linewidth=2.5, alpha=0.7, label=f"Route {i + 1}")

    plt.title(title, fontsize=16, fontweight='bold', pad=20)
    plt.xlabel("X coordinate", fontsize=12)
    plt.ylabel("Y coordinate", fontsize=12)
    plt.legend(bbox_to_anchor=(1.05, 1), loc='upper left', fontsize=9)
    plt.grid(True, alpha=0.3, linestyle='--')
    plt.axis('equal')
    plt.tight_layout()

    if save_filename:
        plt.savefig(save_filename, dpi=DEFAULT_PLOT_DPI, bbox_inches='tight')
        print(f"✓ Plot saved as {save_filename}")

    plt.show()


def save_solution(solution, cost, filename):
    """
    Save a solution to a .sol file in standard TSPLIB format.

    Parameters
    ----------
    solution : list of routes
    cost     : total route cost
    filename : output file path
    """
    with open(filename, 'w') as f:
        for i, route in enumerate(solution):
            route_customers = [c + 1 for c in route[1:-1]]
            f.write(f"Route #{i + 1}: {' '.join(map(str, route_customers))}\n")
        f.write(f"Cost {int(round(cost))}\n")

    print(f"✓ Solution saved to {filename}")
