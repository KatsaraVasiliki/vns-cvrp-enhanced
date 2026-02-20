# -*- coding: utf-8 -*-
"""
Entry point for the CVRP Variable Neighborhood Search solver.

Usage:
    python main.py

Edit the `instances` list and flags below to configure a run.
Instance .vrp and .sol files should be placed in data/instances/ and data/solutions/.
"""

import os
import time

from src.parser import parse_vrp, parse_sol
from src.vns import VNS_solver
from src.visualization import plot_solution, save_solution

# ── Configuration ──────────────────────────────────────────────────────────────
USE_OR_OPT         = False           # Or-opt is expensive; keep False for speed
CONSTRUCTION_METHOD = 'Clarke-Wright' # Options: Clarke-Wright | nearest_neighbor |
                                      #          greedy | cheapest_insertion | random
ENABLE_ANIMATION   = True           # Set True to record an MP4 (requires ffmpeg)

# (instance_name, max_iter, max_time_seconds)
instances = [
    ("eil23", 1000, 600),
]
# ───────────────────────────────────────────────────────────────────────────────

INSTANCES_DIR = os.path.join("data", "instances")
SOLUTIONS_DIR = os.path.join("data", "solutions")
RESULTS_DIR   = "results"
os.makedirs(RESULTS_DIR, exist_ok=True)


def run_instance(instance_name, max_iter=1000, max_time=600,
                 construction=CONSTRUCTION_METHOD,
                 use_or_opt=USE_OR_OPT,
                 enable_animation=ENABLE_ANIMATION):
    """
    Load, solve, and report results for a single CVRP instance.

    Parameters
    ----------
    instance_name    : base filename (without extension)
    max_iter         : VNS iteration limit
    max_time         : VNS time limit in seconds
    construction     : initial solution heuristic
    use_or_opt       : enable Or-opt in VND
    enable_animation : record improvement video

    Returns
    -------
    (my_cost, best_known_cost) or (None, None) on error
    """
    vrp_file = os.path.join(INSTANCES_DIR, f"{instance_name}.vrp")
    sol_file = os.path.join(SOLUTIONS_DIR, f"{instance_name}.sol")

    print(f"\n{'='*70}")
    print(f"Instance: {instance_name}")
    print(f"{'='*70}")

    if not os.path.exists(vrp_file):
        print(f"Error: {vrp_file} not found.")
        return None, None

    # Best-known solution (optional)
    if os.path.exists(sol_file):
        best_known = parse_sol(sol_file)
    else:
        print(f"Warning: {sol_file} not found — gap will not be reported.")
        best_known = {'cost': None, 'routes': []}

    instance = parse_vrp(vrp_file)
    coords   = instance['coords']
    demands  = instance['demands']
    capacity = instance['capacity']

    # Solve
    my_solution, my_cost, recorder = VNS_solver(
        coords, demands, capacity,
        max_iter=max_iter,
        max_time=max_time,
        construction_method=construction,
        use_or_opt=use_or_opt,
        enable_animation=enable_animation,
    )

    # Report
    print(f"\n{'='*70}")
    print(f"RESULTS — {instance_name}")
    print(f"{'='*70}")

    if best_known['cost'] is not None:
        print(f"Best-known cost:  {best_known['cost']:.2f}")
        print(f"VNS cost:         {my_cost:.2f}")
        gap = ((my_cost - best_known['cost']) / best_known['cost']) * 100
        print(f"Gap:              {gap:.2f}%")
    else:
        print(f"VNS cost:         {my_cost:.2f}")
        gap = 0.0

    print(f"Number of routes: {len(my_solution)}")
    print(f"{'='*70}\n")

    # Save outputs
    sol_out  = os.path.join(RESULTS_DIR, f"{instance_name}_output.sol")
    plot_out = os.path.join(RESULTS_DIR, f"{instance_name}_solution.png")

    save_solution(my_solution, my_cost, sol_out)
    plot_solution(
        coords, my_solution,
        title=f"{instance_name}  |  VNS = {my_cost:.1f}",
        save_filename=plot_out,
    )

    # Animation
    if enable_animation and recorder:
        anim_out = os.path.join(RESULTS_DIR, f"{instance_name}_animation.mp4")
        recorder.create_animation(filename=anim_out, fps=2)

    return my_cost, best_known['cost']


if __name__ == "__main__":
    results = []
    total_start = time.time()

    for instance_name, max_iter, max_time in instances:
        my_cost, best_cost = run_instance(instance_name, max_iter, max_time)
        if my_cost is not None:
            results.append((instance_name, my_cost, best_cost))

    total_time = time.time() - total_start

    # Summary table
    print(f"\n{'='*70}")
    print("FINAL SUMMARY")
    print(f"{'='*70}")
    print(f"{'Instance':<20} {'Best-Known':<15} {'VNS':<15} {'Gap %':<10}")
    print(f"{'-'*70}")

    gaps = []
    for name, my, best in results:
        if best is not None:
            gap = ((my - best) / best) * 100
            gaps.append(gap)
            print(f"{name:<20} {best:<15.2f} {my:<15.2f} {gap:<10.2f}")
        else:
            print(f"{name:<20} {'N/A':<15} {my:<15.2f} {'N/A':<10}")

    print(f"{'='*70}")
    if gaps:
        print(f"Average gap: {sum(gaps)/len(gaps):.2f}%")
        print(f"Best gap:    {min(gaps):.2f}%")
        print(f"Worst gap:   {max(gaps):.2f}%")
    print(f"Total runtime: {total_time / 60:.1f} minutes")
    print(f"{'='*70}\n")
    print("✓ Solutions saved in results/")
