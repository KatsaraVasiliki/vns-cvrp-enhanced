# -*- coding: utf-8 -*-
"""
Shaking mechanisms for Variable Neighborhood Search (VNS).

These perturbation operators escape local optima by introducing
controlled randomness into the current best solution.

Shaking neighborhoods:
- Shake_N1: Random relocate (move k random customers to random positions)
- Shake_N2: Random swap (swap k random customer pairs between routes)
- Shake_N3: Double bridge / random 2-opt (perform k random 2-opt reversals)
"""

import random
from src.utils import route_demand


def Shake_N1_random_relocate(solution, demands, capacity, k):
    """
    Shaking N1: Perform k random customer relocations.

    Picks a random customer from a valid route and moves it to a random
    feasible position in a different route.
    """
    sol = [r[:] for r in solution]

    for _ in range(k):
        if len(sol) < 2:
            break

        valid_routes = [i for i, r in enumerate(sol) if len(r) > 2]
        if not valid_routes:
            break

        r1_idx = random.choice(valid_routes)
        c_idx = random.randint(1, len(sol[r1_idx]) - 2)
        customer = sol[r1_idx][c_idx]

        r2_idx = random.randint(0, len(sol) - 1)

        if route_demand(sol[r2_idx], demands) + demands[customer] <= capacity:
            sol[r1_idx].pop(c_idx)
            pos = random.randint(1, len(sol[r2_idx]) - 1)
            sol[r2_idx].insert(pos, customer)

    sol = [r for r in sol if len(r) > 2]
    return sol


def Shake_N2_random_swap(solution, demands, capacity, k):
    """
    Shaking N2: Perform k random customer swaps between routes.

    Selects two different routes and swaps a random customer from each,
    if the capacity constraints remain satisfied after the swap.
    """
    sol = [r[:] for r in solution]

    for _ in range(k):
        if len(sol) < 2:
            break

        valid_routes = [i for i, r in enumerate(sol) if len(r) > 2]
        if len(valid_routes) < 2:
            break

        r1_idx, r2_idx = random.sample(valid_routes, 2)

        c1_idx = random.randint(1, len(sol[r1_idx]) - 2)
        c2_idx = random.randint(1, len(sol[r2_idx]) - 2)

        c1 = sol[r1_idx][c1_idx]
        c2 = sol[r2_idx][c2_idx]

        load1 = route_demand(sol[r1_idx], demands) - demands[c1] + demands[c2]
        load2 = route_demand(sol[r2_idx], demands) - demands[c2] + demands[c1]

        if load1 <= capacity and load2 <= capacity:
            sol[r1_idx][c1_idx] = c2
            sol[r2_idx][c2_idx] = c1

    return sol


def Shake_N3_double_bridge(solution, demands, capacity, k):
    """
    Shaking N3: Perform k random intra-route 2-opt reversals.

    Selects a random route and reverses a random segment within it.
    Inspired by the double-bridge move used in TSP perturbation.
    """
    sol = [r[:] for r in solution]

    for _ in range(k):
        valid_routes = [i for i, r in enumerate(sol) if len(r) > 4]
        if not valid_routes:
            break

        r_idx = random.choice(valid_routes)
        route = sol[r_idx]

        i = random.randint(1, len(route) - 3)
        j = random.randint(i + 1, len(route) - 2)

        sol[r_idx] = route[:i] + route[i:j + 1][::-1] + route[j + 1:]

    return sol
