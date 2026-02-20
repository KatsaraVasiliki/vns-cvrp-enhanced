# -*- coding: utf-8 -*-
"""
Distance and cost utility functions for CVRP.
"""

import math


def euclidean(a, b):
    return math.hypot(a[0] - b[0], a[1] - b[1])


def compute_distance_matrix(coords):
    n = len(coords)
    dist = [[0.0] * n for _ in range(n)]
    for i in range(n):
        for j in range(n):
            dist[i][j] = euclidean(coords[i], coords[j])
    return dist


def route_cost(route, dist):
    return sum(dist[route[i]][route[i + 1]] for i in range(len(route) - 1))


def solution_cost(solution, dist):
    return sum(route_cost(r, dist) for r in solution)


def route_demand(route, demands):
    return sum(demands[c] for c in route if c != 0)
