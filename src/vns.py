# -*- coding: utf-8 -*-
"""
Variable Neighborhood Search (VNS) solver for CVRP.

Orchestrates:
- Initial solution construction
- VND local search
- Shaking perturbations
- Tabu list to prevent cycling
- Optional animation recording
"""

import time
from copy import deepcopy

from src.utils import compute_distance_matrix, solution_cost
from src.construction import (
    savings_algorithm,
    nearest_neighbor_vrp,
    greedy_vrp,
    cheapest_insertion_vrp,
    random_initial_solution,
)
from src.shaking import (
    Shake_N1_random_relocate,
    Shake_N2_random_swap,
    Shake_N3_double_bridge,
)
from src.vnd import VND
from src.animation import VNSAnimationRecorder
from config import (
    K_MAX,
    TABU_TENURE_MIN,
    TABU_TENURE_MAX,
    PATIENCE_MIN,
    PATIENCE_MAX,
)


def _build_initial_solution(method, coords, demands, capacity, dist):
    """Select and run the chosen construction heuristic."""
    method_map = {
        'Clarke-Wright':       (savings_algorithm,        True,  "Clarke-Wright Savings"),
        'nearest_neighbor':    (nearest_neighbor_vrp,     True,  "Nearest Neighbor"),
        'greedy':              (greedy_vrp,               True,  "Greedy Algorithm"),
        'cheapest_insertion':  (cheapest_insertion_vrp,   True,  "Cheapest Insertion"),
        'random':              (random_initial_solution,  False, "Random"),
    }

    if method not in method_map:
        print(f"Unknown method '{method}', falling back to Clarke-Wright.")
        method = 'Clarke-Wright'

    func, needs_dist, label = method_map[method]

    if needs_dist:
        solution = func(coords, demands, capacity, dist)
    else:
        solution = func(coords, demands, capacity)

    return solution, label


def _solution_hash(sol):
    """Canonical hash for tabu list membership check."""
    return tuple(sorted([tuple(sorted(r[1:-1])) for r in sol]))


def VNS_solver(coords, demands, capacity,
               max_iter=1000, max_time=600,
               construction_method='Clarke-Wright',
               use_or_opt=False,
               enable_animation=False):
    """
    Enhanced Variable Neighborhood Search for CVRP.

    Parameters
    ----------
    coords            : list of (x, y) tuples, index 0 = depot
    demands           : list of demands, index 0 = depot (value 0)
    capacity          : vehicle capacity
    max_iter          : maximum number of VNS iterations
    max_time          : wall-clock time limit in seconds
    construction_method : one of 'Clarke-Wright', 'nearest_neighbor',
                          'greedy', 'cheapest_insertion', 'random'
    use_or_opt        : enable Or-opt neighborhood in VND (slower)
    enable_animation  : record improvements for video export

    Returns
    -------
    best_solution, best_cost, recorder (None if animation disabled)
    """
    dist = compute_distance_matrix(coords)
    n = len(coords)

    print(f"Instance: {n} customers, capacity: {capacity}")
    print(f"Construction method: {construction_method}")
    print(f"Or-opt enabled: {use_or_opt}")
    print(f"Animation enabled: {enable_animation}")

    # --- Initial solution ---
    s, method_label = _build_initial_solution(construction_method, coords, demands, capacity, dist)
    init_cost = solution_cost(s, dist)
    print(f"Initial solution ({method_label}): {len(s)} routes, cost = {init_cost:.2f}")

    # --- Animation recorder ---
    recorder = VNSAnimationRecorder(coords, s, init_cost) if enable_animation else None

    # --- Apply VND to initial solution ---
    s = VND(s, demands, capacity, dist, use_or_opt=use_or_opt, recorder=recorder)
    best = deepcopy(s)
    best_cost = solution_cost(best, dist)
    print(f"After initial VND: {len(best)} routes, cost = {best_cost:.2f}")

    # --- Shaking neighborhoods ---
    shake_neighborhoods = [
        ("Random Relocate", Shake_N1_random_relocate),
        ("Random Swap",     Shake_N2_random_swap),
        ("Double Bridge",   Shake_N3_double_bridge),
    ]

    # --- Tabu list ---
    tabu_list = []
    tabu_tenure = min(TABU_TENURE_MAX, max(TABU_TENURE_MIN, n // 20))

    # --- VNS parameters ---
    k_max = K_MAX
    k = 1
    iteration = 0
    last_improvement = 0
    tabu_skips = 0
    start_time = time.time()

    patience = min(PATIENCE_MAX, max(PATIENCE_MIN, n // 5))
    min_iterations = max(50, n // 10)

    print(f"\nStarting VNS (max_iter={max_iter}, max_time={max_time}s, patience={patience})")
    print(f"Tabu tenure: {tabu_tenure}, k_max: {k_max}")
    print(f"{'Iter':<8} {'k':<4} {'Cost':<12} {'Routes':<8} {'Best':<12} {'Tabu':<6} {'Status':<20}")
    print("-" * 90)

    while iteration < max_iter and (time.time() - start_time) < max_time:

        # --- Shaking ---
        shake_idx = (k - 1) % len(shake_neighborhoods)
        shake_name, shake_func = shake_neighborhoods[shake_idx]
        s_shaken = shake_func(best, demands, capacity, k)

        # --- Tabu check ---
        if _solution_hash(s_shaken) in tabu_list:
            tabu_skips += 1
            k = k % k_max + 1
            iteration += 1
            continue

        # --- Local search ---
        s_local = VND(s_shaken, demands, capacity, dist,
                      use_or_opt=use_or_opt, recorder=recorder)
        cost_local = solution_cost(s_local, dist)
        routes_local = len(s_local)

        # --- Acceptance ---
        accept = False
        status = ""
        improvement = 0.0

        if cost_local < best_cost - 1e-6:
            accept = True
            improvement = best_cost - cost_local
            status = f"IMPROVED (-{improvement:.2f})"
        elif abs(cost_local - best_cost) < 1e-6 and routes_local < len(best):
            accept = True
            status = "FEWER ROUTES"

        if accept:
            best = deepcopy(s_local)
            best_cost = cost_local
            last_improvement = iteration
            k = 1

            tabu_list.append(_solution_hash(s_local))
            if len(tabu_list) > tabu_tenure:
                tabu_list.pop(0)

            print(f"{iteration:<8} {k:<4} {cost_local:<12.2f} {routes_local:<8} "
                  f"{best_cost:<12.2f} {len(tabu_list):<6} {status:<20}")

            if recorder and improvement > 0:
                recorder.add_frame(
                    best, best_cost,
                    f"VNS Improvement — Iter {iteration}",
                    f"{status}\nΔ Cost: -{improvement:.2f}"
                )
        else:
            k = k % k_max + 1

        iteration += 1

        # --- Early stopping ---
        if iteration > min_iterations and (iteration - last_improvement) > patience:
            elapsed = time.time() - start_time
            print(f"\n{'='*90}")
            print(f"Early stopping: No improvement for {patience} iterations")
            print(f"Total iterations: {iteration}, Time: {elapsed:.1f}s")
            print(f"Tabu skips: {tabu_skips}")
            print(f"{'='*90}")
            break

    elapsed_time = time.time() - start_time

    if iteration >= max_iter or elapsed_time >= max_time:
        print(f"\n{'='*90}")
        print(f"Limit reached (iter={iteration}, time={elapsed_time:.1f}s)")
        print(f"Tabu skips: {tabu_skips}")
        print(f"{'='*90}")

    print(f"Final solution: {len(best)} routes, cost = {best_cost:.2f}")
    return best, best_cost, recorder
