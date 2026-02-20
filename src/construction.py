# -*- coding: utf-8 -*-
"""
Initial solution construction heuristics for CVRP.

Available methods:
- Clarke-Wright Savings Algorithm
- Nearest Neighbor
- Greedy (edge-based)
- Cheapest Insertion
- Random
"""

import random
from src.utils import route_demand


def savings_algorithm(coords, demands, capacity, dist):
    """
    Clarke-Wright savings algorithm.
    Reference: https://web.mit.edu/urban_or_book/www/book/chapter6/6.4.12.html

    Builds routes by merging single-customer routes based on a savings score
    s(i,j) = d(0,i) + d(0,j) - d(i,j), prioritizing the largest savings.
    """
    n = len(demands)
    routes = [[0, i, 0] for i in range(1, n)]

    savings = []
    for i in range(1, n):
        for j in range(i + 1, n):
            s = dist[0][i] + dist[0][j] - dist[i][j]
            savings.append((s, i, j))

    savings.sort(reverse=True)

    for _, i, j in savings:
        route_i = route_j = None
        for r in routes:
            if i in r:
                route_i = r
            if j in r:
                route_j = r

        if not route_i or not route_j or route_i == route_j:
            continue

        pos_i = route_i.index(i)
        pos_j = route_j.index(j)

        if (pos_i in (1, len(route_i) - 2)) and (pos_j in (1, len(route_j) - 2)):
            if route_demand(route_i, demands) + route_demand(route_j, demands) <= capacity:
                if pos_i == len(route_i) - 2 and pos_j == 1:
                    new_route = route_i[:-1] + route_j[1:]
                elif pos_i == 1 and pos_j == len(route_j) - 2:
                    new_route = route_j[:-1] + route_i[1:]
                elif pos_i == len(route_i) - 2 and pos_j == len(route_j) - 2:
                    new_route = route_i[:-1] + route_j[-2:0:-1] + [0]
                elif pos_i == 1 and pos_j == 1:
                    new_route = [0] + route_i[-2:0:-1] + route_j[1:]
                else:
                    continue

                routes.remove(route_i)
                routes.remove(route_j)
                routes.append(new_route)

    return routes


def nearest_neighbor_vrp(coords, demands, capacity, dist):
    """
    Nearest Neighbor constructive heuristic.

    Builds routes greedily by repeatedly visiting the nearest feasible
    unvisited customer, starting from the depot, until vehicle capacity
    is reached, then opens a new route.
    """
    n = len(coords)
    unvisited = set(range(1, n))
    routes = []

    while unvisited:
        route = [0]
        current = 0
        route_load = 0

        while unvisited:
            best_dist = float('inf')
            best_customer = None

            for customer in unvisited:
                if route_load + demands[customer] <= capacity:
                    d = dist[current][customer]
                    if d < best_dist:
                        best_dist = d
                        best_customer = customer

            if best_customer is None:
                break

            route.append(best_customer)
            current = best_customer
            route_load += demands[best_customer]
            unvisited.remove(best_customer)

        if len(route) > 1:
            route.append(0)
            routes.append(route)

    return routes


def greedy_vrp(coords, demands, capacity, dist):
    """
    Greedy edge-based constructive heuristic.

    Sorts all edges by increasing distance and incrementally builds
    route fragments by connecting endpoints, while respecting
    degree and vehicle capacity constraints.
    """
    n = len(coords)

    edges = []
    for i in range(n):
        for j in range(i + 1, n):
            edges.append((dist[i][j], i, j))
    edges.sort()

    connections = {i: [] for i in range(n)}
    customer_degree = {i: 0 for i in range(1, n)}

    customer_to_fragment = {}
    fragments = []
    fragment_loads = []

    for cost, i, j in edges:
        if i != 0 and customer_degree[i] >= 2:
            continue
        if j != 0 and customer_degree[j] >= 2:
            continue

        frag_i = customer_to_fragment.get(i)
        frag_j = customer_to_fragment.get(j)

        if frag_i is None and frag_j is None:
            if i == 0 or j == 0:
                customer = j if i == 0 else i
                if demands[customer] <= capacity:
                    frag_idx = len(fragments)
                    fragments.append([i, j])
                    fragment_loads.append(demands[customer])
                    if customer != 0:
                        customer_to_fragment[customer] = frag_idx
                    connections[i].append(j)
                    connections[j].append(i)
                    if i != 0:
                        customer_degree[i] += 1
                    if j != 0:
                        customer_degree[j] += 1
            else:
                if demands[i] + demands[j] <= capacity:
                    frag_idx = len(fragments)
                    fragments.append([i, j])
                    fragment_loads.append(demands[i] + demands[j])
                    customer_to_fragment[i] = frag_idx
                    customer_to_fragment[j] = frag_idx
                    connections[i].append(j)
                    connections[j].append(i)
                    customer_degree[i] += 1
                    customer_degree[j] += 1

        elif frag_i is not None and frag_j is None:
            fragment = fragments[frag_i]
            new_load = fragment_loads[frag_i] + (demands[j] if j != 0 else 0)

            if new_load <= capacity:
                if i == fragment[0] or i == fragment[-1]:
                    if i == fragment[0]:
                        fragment.insert(0, j)
                    else:
                        fragment.append(j)
                    connections[i].append(j)
                    connections[j].append(i)
                    if i != 0:
                        customer_degree[i] += 1
                    if j != 0:
                        customer_degree[j] += 1
                        customer_to_fragment[j] = frag_i
                    fragment_loads[frag_i] = new_load

        elif frag_i is None and frag_j is not None:
            fragment = fragments[frag_j]
            new_load = fragment_loads[frag_j] + (demands[i] if i != 0 else 0)

            if new_load <= capacity:
                if j == fragment[0] or j == fragment[-1]:
                    if j == fragment[0]:
                        fragment.insert(0, i)
                    else:
                        fragment.append(i)
                    connections[i].append(j)
                    connections[j].append(i)
                    if i != 0:
                        customer_degree[i] += 1
                        customer_to_fragment[i] = frag_j
                    if j != 0:
                        customer_degree[j] += 1
                    fragment_loads[frag_j] = new_load

        elif frag_i != frag_j:
            frag1 = fragments[frag_i]
            frag2 = fragments[frag_j]
            new_load = fragment_loads[frag_i] + fragment_loads[frag_j]

            if new_load <= capacity:
                i_at_end = (i == frag1[0] or i == frag1[-1])
                j_at_end = (j == frag2[0] or j == frag2[-1])

                if i_at_end and j_at_end:
                    if i == frag1[-1] and j == frag2[0]:
                        merged = frag1 + frag2
                    elif i == frag1[0] and j == frag2[-1]:
                        merged = frag2 + frag1
                    elif i == frag1[-1] and j == frag2[-1]:
                        merged = frag1 + frag2[::-1]
                    elif i == frag1[0] and j == frag2[0]:
                        merged = frag1[::-1] + frag2
                    else:
                        continue

                    fragments[frag_i] = merged
                    fragment_loads[frag_i] = new_load
                    fragments[frag_j] = []
                    fragment_loads[frag_j] = 0

                    for customer in frag2:
                        if customer != 0:
                            customer_to_fragment[customer] = frag_i

                    connections[i].append(j)
                    connections[j].append(i)
                    if i != 0:
                        customer_degree[i] += 1
                    if j != 0:
                        customer_degree[j] += 1

    routes = []
    for fragment in fragments:
        if not fragment:
            continue
        if fragment[0] != 0:
            fragment.insert(0, 0)
        if fragment[-1] != 0:
            fragment.append(0)
        if len(fragment) > 2:
            routes.append(fragment)

    for customer in range(1, n):
        if customer not in customer_to_fragment:
            if demands[customer] <= capacity:
                routes.append([0, customer, 0])

    return routes


def cheapest_insertion_vrp(coords, demands, capacity, dist):
    """
    Cheapest Insertion constructive heuristic with farthest-node initialization.

    Starts from the farthest customer and repeatedly inserts the customer
    whose insertion causes the minimum increase in total route cost,
    subject to vehicle capacity constraints.
    """
    n = len(coords)
    unvisited = set(range(1, n))

    farthest = max(unvisited, key=lambda c: dist[0][c])
    routes = [[0, farthest, 0]]
    route_loads = [demands[farthest]]
    unvisited.remove(farthest)

    while unvisited:
        best_cost_increase = float('inf')
        best_customer = None
        best_route = None
        best_position = None

        for customer in unvisited:
            for r_idx, route in enumerate(routes):
                if route_loads[r_idx] + demands[customer] > capacity:
                    continue

                for pos in range(1, len(route)):
                    increase = (dist[route[pos - 1]][customer] +
                                dist[customer][route[pos]] -
                                dist[route[pos - 1]][route[pos]])

                    if increase < best_cost_increase:
                        best_cost_increase = increase
                        best_customer = customer
                        best_route = r_idx
                        best_position = pos

        if best_customer is None:
            customer = unvisited.pop()
            if demands[customer] <= capacity:
                routes.append([0, customer, 0])
                route_loads.append(demands[customer])
        else:
            routes[best_route].insert(best_position, best_customer)
            route_loads[best_route] += demands[best_customer]
            unvisited.remove(best_customer)

    return routes


def random_initial_solution(coords, demands, capacity):
    """
    Random constructive heuristic.

    Generates a random feasible solution by randomly ordering customers
    and inserting them sequentially into routes while respecting
    vehicle capacity constraints.
    """
    n = len(coords)
    customers = list(range(1, n))
    random.shuffle(customers)

    routes = []
    current_route = [0]
    current_load = 0

    for customer in customers:
        if current_load + demands[customer] <= capacity:
            current_route.append(customer)
            current_load += demands[customer]
        else:
            if len(current_route) > 1:
                current_route.append(0)
                routes.append(current_route)
            current_route = [0, customer]
            current_load = demands[customer]

    if len(current_route) > 1:
        current_route.append(0)
        routes.append(current_route)

    return routes
