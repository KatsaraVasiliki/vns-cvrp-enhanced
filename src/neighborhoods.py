# -*- coding: utf-8 -*-
"""
Neighborhood structures for local search in CVRP.

Neighborhoods:
- N1: 2-opt within routes (intra-route)
- N2: Relocate customer between routes (inter-route)
- N3: Swap customers between routes (inter-route)
- N4: 2-opt between routes (inter-route)
- N5: Merge routes
- N6: Or-opt (optional, expensive)
"""

from src.utils import route_cost, solution_cost, route_demand
from config import IMPROVEMENT_THRESHOLD


def N1_two_opt_intra(solution, dist):
    """N1: 2-opt within each route. Reverses segments to reduce intra-route cost."""
    best_sol = [r[:] for r in solution]
    improved = True

    while improved:
        improved = False
        for r_idx, route in enumerate(best_sol):
            if len(route) <= 3:
                continue

            for i in range(1, len(route) - 2):
                for j in range(i + 1, len(route) - 1):
                    delta = (dist[route[i - 1]][route[j]] +
                             dist[route[i]][route[j + 1]] -
                             dist[route[i - 1]][route[i]] -
                             dist[route[j]][route[j + 1]])

                    if delta < -IMPROVEMENT_THRESHOLD:
                        best_sol[r_idx] = route[:i] + route[i:j + 1][::-1] + route[j + 1:]
                        improved = True
                        break
                if improved:
                    break
            if improved:
                break

    return best_sol


def N2_relocate_inter(solution, demands, capacity, dist):
    """N2: Move a single customer from one route to another at the best insertion position."""
    sol = [r[:] for r in solution]

    improved = True
    while improved:
        improved = False
        best_delta = -IMPROVEMENT_THRESHOLD
        best_move = None

        for r1_idx in range(len(sol)):
            if len(sol[r1_idx]) <= 2:
                continue

            for c_idx in range(1, len(sol[r1_idx]) - 1):
                customer = sol[r1_idx][c_idx]

                removal_delta = (dist[sol[r1_idx][c_idx - 1]][sol[r1_idx][c_idx + 1]] -
                                 dist[sol[r1_idx][c_idx - 1]][customer] -
                                 dist[customer][sol[r1_idx][c_idx + 1]])

                for r2_idx in range(len(sol)):
                    if r1_idx == r2_idx:
                        continue
                    if route_demand(sol[r2_idx], demands) + demands[customer] > capacity:
                        continue

                    for pos in range(1, len(sol[r2_idx])):
                        insert_delta = (dist[sol[r2_idx][pos - 1]][customer] +
                                        dist[customer][sol[r2_idx][pos]] -
                                        dist[sol[r2_idx][pos - 1]][sol[r2_idx][pos]])

                        total_delta = removal_delta + insert_delta

                        if total_delta < best_delta:
                            best_delta = total_delta
                            best_move = (r1_idx, c_idx, r2_idx, pos)

        if best_move:
            r1_idx, c_idx, r2_idx, pos = best_move
            customer = sol[r1_idx][c_idx]
            sol[r1_idx].pop(c_idx)
            sol[r2_idx].insert(pos, customer)
            sol = [r for r in sol if len(r) > 2]
            improved = True

    return sol


def N3_swap_inter(solution, demands, capacity, dist):
    """N3: Swap one customer between two different routes."""
    sol = [r[:] for r in solution]

    improved = True
    while improved:
        improved = False
        best_delta = -IMPROVEMENT_THRESHOLD
        best_move = None

        for r1_idx in range(len(sol)):
            if len(sol[r1_idx]) <= 2:
                continue

            for c1_idx in range(1, len(sol[r1_idx]) - 1):
                c1 = sol[r1_idx][c1_idx]

                for r2_idx in range(r1_idx + 1, len(sol)):
                    if len(sol[r2_idx]) <= 2:
                        continue

                    for c2_idx in range(1, len(sol[r2_idx]) - 1):
                        c2 = sol[r2_idx][c2_idx]

                        load1 = route_demand(sol[r1_idx], demands) - demands[c1] + demands[c2]
                        load2 = route_demand(sol[r2_idx], demands) - demands[c2] + demands[c1]

                        if load1 > capacity or load2 > capacity:
                            continue

                        delta = (dist[sol[r1_idx][c1_idx - 1]][c2] +
                                 dist[c2][sol[r1_idx][c1_idx + 1]] +
                                 dist[sol[r2_idx][c2_idx - 1]][c1] +
                                 dist[c1][sol[r2_idx][c2_idx + 1]] -
                                 dist[sol[r1_idx][c1_idx - 1]][c1] -
                                 dist[c1][sol[r1_idx][c1_idx + 1]] -
                                 dist[sol[r2_idx][c2_idx - 1]][c2] -
                                 dist[c2][sol[r2_idx][c2_idx + 1]])

                        if delta < best_delta:
                            best_delta = delta
                            best_move = (r1_idx, c1_idx, r2_idx, c2_idx)

        if best_move:
            r1_idx, c1_idx, r2_idx, c2_idx = best_move
            c1 = sol[r1_idx][c1_idx]
            c2 = sol[r2_idx][c2_idx]
            sol[r1_idx][c1_idx] = c2
            sol[r2_idx][c2_idx] = c1
            improved = True

    return sol


def N4_two_opt_inter(solution, demands, capacity, dist):
    """N4: 2-opt between two routes — exchange route tails."""
    best_sol = [r[:] for r in solution]
    improved = True

    while improved:
        improved = False

        for r1_idx in range(len(best_sol)):
            if len(best_sol[r1_idx]) <= 2:
                continue

            for r2_idx in range(r1_idx + 1, len(best_sol)):
                if len(best_sol[r2_idx]) <= 2:
                    continue

                for i in range(1, len(best_sol[r1_idx]) - 1):
                    for j in range(1, len(best_sol[r2_idx]) - 1):
                        new_r1 = best_sol[r1_idx][:i + 1] + best_sol[r2_idx][j + 1:]
                        new_r2 = best_sol[r2_idx][:j + 1] + best_sol[r1_idx][i + 1:]

                        if (route_demand(new_r1, demands) <= capacity and
                                route_demand(new_r2, demands) <= capacity):

                            old_cost = (route_cost(best_sol[r1_idx], dist) +
                                        route_cost(best_sol[r2_idx], dist))
                            new_cost = route_cost(new_r1, dist) + route_cost(new_r2, dist)

                            if new_cost < old_cost - IMPROVEMENT_THRESHOLD:
                                new_sol = [r[:] for r in best_sol]
                                new_sol[r1_idx] = new_r1
                                new_sol[r2_idx] = new_r2
                                best_sol = new_sol
                                improved = True
                                break
                    if improved:
                        break
                if improved:
                    break
            if improved:
                break

    return best_sol


def N5_merge_routes(solution, demands, capacity, dist):
    """N5: Merge two routes into one if capacity allows and cost improves."""
    sol = [r[:] for r in solution]
    improved = True

    while improved:
        improved = False
        best_delta = -IMPROVEMENT_THRESHOLD
        best_merge = None

        for r1_idx in range(len(sol)):
            for r2_idx in range(r1_idx + 1, len(sol)):
                total_demand = route_demand(sol[r1_idx], demands) + route_demand(sol[r2_idx], demands)

                if total_demand <= capacity:
                    configs = [
                        sol[r1_idx][:-1] + sol[r2_idx][1:],
                        sol[r2_idx][:-1] + sol[r1_idx][1:],
                        sol[r1_idx][:-1] + sol[r2_idx][-2:0:-1] + [0],
                        sol[r2_idx][:-1] + sol[r1_idx][-2:0:-1] + [0]
                    ]

                    old_cost = route_cost(sol[r1_idx], dist) + route_cost(sol[r2_idx], dist)

                    for merged in configs:
                        new_cost = route_cost(merged, dist)
                        delta = new_cost - old_cost

                        if delta < best_delta:
                            best_delta = delta
                            best_merge = (r1_idx, r2_idx, merged)

        if best_merge:
            r1_idx, r2_idx, merged = best_merge
            new_sol = [route for idx, route in enumerate(sol)
                       if idx != r1_idx and idx != r2_idx]
            new_sol.append(merged)
            sol = new_sol
            improved = True

    return sol


def N6_or_opt(solution, demands, capacity, dist):
    """
    N6: Or-opt — relocate chains of 1, 2, or 3 consecutive customers within
    or between routes. Expensive but effective. Disabled by default.
    """
    sol = [r[:] for r in solution]
    improved = True

    while improved:
        improved = False
        best_delta = -IMPROVEMENT_THRESHOLD
        best_move = None

        for chain_len in [1, 2, 3]:
            for r_idx in range(len(sol)):
                if len(sol[r_idx]) <= chain_len + 2:
                    continue

                for start in range(1, len(sol[r_idx]) - chain_len):
                    for insert_pos in range(1, len(sol[r_idx]) - 1):
                        if insert_pos >= start and insert_pos <= start + chain_len:
                            continue

                        route = sol[r_idx]
                        old_cost = (dist[route[start - 1]][route[start]] +
                                    dist[route[start + chain_len - 1]][route[start + chain_len]] +
                                    dist[route[insert_pos - 1]][route[insert_pos]])
                        new_cost = (dist[route[start - 1]][route[start + chain_len]] +
                                    dist[route[insert_pos - 1]][route[start]] +
                                    dist[route[start + chain_len - 1]][route[insert_pos]])

                        delta = new_cost - old_cost
                        if delta < best_delta:
                            best_delta = delta
                            best_move = ('intra', r_idx, start, chain_len, insert_pos)

            for r1_idx in range(len(sol)):
                if len(sol[r1_idx]) <= chain_len + 1:
                    continue

                for start in range(1, len(sol[r1_idx]) - chain_len):
                    chain_demand = sum(demands[sol[r1_idx][start + i]] for i in range(chain_len))

                    for r2_idx in range(len(sol)):
                        if r1_idx == r2_idx:
                            continue
                        if route_demand(sol[r2_idx], demands) + chain_demand > capacity:
                            continue

                        for insert_pos in range(1, len(sol[r2_idx])):
                            removal_cost = (dist[sol[r1_idx][start - 1]][sol[r1_idx][start + chain_len]] -
                                            dist[sol[r1_idx][start - 1]][sol[r1_idx][start]])
                            for i in range(chain_len - 1):
                                removal_cost -= dist[sol[r1_idx][start + i]][sol[r1_idx][start + i + 1]]
                            removal_cost -= dist[sol[r1_idx][start + chain_len - 1]][sol[r1_idx][start + chain_len]]

                            insert_cost = (dist[sol[r2_idx][insert_pos - 1]][sol[r1_idx][start]] +
                                           dist[sol[r1_idx][start + chain_len - 1]][sol[r2_idx][insert_pos]] -
                                           dist[sol[r2_idx][insert_pos - 1]][sol[r2_idx][insert_pos]])
                            for i in range(chain_len - 1):
                                insert_cost += dist[sol[r1_idx][start + i]][sol[r1_idx][start + i + 1]]

                            delta = removal_cost + insert_cost
                            if delta < best_delta:
                                best_delta = delta
                                best_move = ('inter', r1_idx, start, chain_len, r2_idx, insert_pos)

        if best_move:
            if best_move[0] == 'intra':
                _, r_idx, start, chain_len, insert_pos = best_move
                chain = sol[r_idx][start:start + chain_len]
                del sol[r_idx][start:start + chain_len]
                if insert_pos > start:
                    insert_pos -= chain_len
                for i, customer in enumerate(chain):
                    sol[r_idx].insert(insert_pos + i, customer)
            else:
                _, r1_idx, start, chain_len, r2_idx, insert_pos = best_move
                chain = sol[r1_idx][start:start + chain_len]
                del sol[r1_idx][start:start + chain_len]
                for i, customer in enumerate(chain):
                    sol[r2_idx].insert(insert_pos + i, customer)
                sol = [r for r in sol if len(r) > 2]
            improved = True

    return sol
