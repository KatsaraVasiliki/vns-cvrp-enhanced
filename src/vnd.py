# -*- coding: utf-8 -*-
"""
Variable Neighborhood Descent (VND) for CVRP.

Applies a sequence of neighborhood structures in order.
Restarts from the first neighborhood whenever an improvement is found.
Terminates when no neighborhood produces an improvement.
"""

from src.utils import solution_cost
from src.neighborhoods import (
    N1_two_opt_intra,
    N2_relocate_inter,
    N3_swap_inter,
    N4_two_opt_inter,
    N5_merge_routes,
    N6_or_opt,
)


def VND(solution, demands, capacity, dist, use_or_opt=False, recorder=None):
    """
    Variable Neighborhood Descent.

    Neighborhood order:
        1. 2-opt intra-route
        2. Merge routes
        3. Relocate (inter-route)
        4. Swap (inter-route)
        5. 2-opt inter-route
        6. Or-opt (optional)

    Parameters
    ----------
    solution : list of routes
    demands : list of customer demands (index 0 = depot)
    capacity : vehicle capacity
    dist : precomputed distance matrix
    use_or_opt : bool, enable Or-opt neighborhood (expensive)
    recorder : VNSAnimationRecorder or None

    Returns
    -------
    Locally optimal solution.
    """
    neighborhoods = [
        ("2-opt intra",  N1_two_opt_intra),
        ("Merge routes", N5_merge_routes),
        ("Relocate",     N2_relocate_inter),
        ("Swap",         N3_swap_inter),
        ("2-opt inter",  N4_two_opt_inter),
    ]

    if use_or_opt:
        neighborhoods.append(("Or-opt", N6_or_opt))

    sol = [r[:] for r in solution]
    k = 0

    while k < len(neighborhoods):
        old_cost = solution_cost(sol, dist)
        old_routes = len(sol)

        name, func = neighborhoods[k]

        # N1 only needs dist; the rest also need demands, capacity
        if k == 0:
            sol_new = func(sol, dist)
        else:
            sol_new = func(sol, demands, capacity, dist)

        new_cost = solution_cost(sol_new, dist)
        new_routes = len(sol_new)

        cost_improved = new_cost < old_cost - 1e-6
        routes_reduced = abs(new_cost - old_cost) < 1e-6 and new_routes < old_routes

        if cost_improved or routes_reduced:
            sol = sol_new
            if recorder and cost_improved:
                improvement = old_cost - new_cost
                recorder.add_frame(
                    sol, new_cost,
                    f"VND: {name}",
                    f"Improvement: -{improvement:.2f}"
                )
            k = 0  # restart from first neighborhood
        else:
            k += 1

    return sol
