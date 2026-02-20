# -*- coding: utf-8 -*-
"""
Parsers for VRP instance files and solution files.
"""

import re


def parse_vrp(filename):
    """Parse a .vrp file in TSPLIB format."""
    with open(filename, 'r') as f:
        lines = [line.strip() for line in f if line.strip()]

    data = {'coords': [], 'demands': [], 'capacity': 0, 'dimension': 0}
    section = None

    for line in lines:
        if line.startswith('DIMENSION'):
            data['dimension'] = int(line.split(':')[1].strip())
        elif line.startswith('CAPACITY'):
            data['capacity'] = int(line.split(':')[1].strip())
        elif line == 'NODE_COORD_SECTION':
            section = 'coords'
        elif line == 'DEMAND_SECTION':
            section = 'demands'
        elif line == 'DEPOT_SECTION':
            section = 'depot'
        elif line == 'EOF':
            break
        elif section == 'coords':
            parts = line.split()
            if len(parts) >= 3:
                idx = int(parts[0]) - 1
                x, y = float(parts[1]), float(parts[2])
                while len(data['coords']) <= idx:
                    data['coords'].append(None)
                data['coords'][idx] = (x, y)
        elif section == 'demands':
            parts = line.split()
            if len(parts) >= 2:
                idx = int(parts[0]) - 1
                demand = int(parts[1])
                while len(data['demands']) <= idx:
                    data['demands'].append(0)
                data['demands'][idx] = demand

    return data


def parse_sol(filename):
    """Parse a .sol solution file."""
    with open(filename, 'r') as f:
        lines = [line.strip() for line in f if line.strip()]

    routes = []
    cost = None

    for line in lines:
        if line.lower().startswith('cost'):
            match = re.search(r'[\d.]+', line)
            if match:
                cost = float(match.group())
        elif line.lower().startswith('route'):
            route_part = line.split(':')[1] if ':' in line else ''
            nodes = [int(n) - 1 for n in route_part.split() if n.strip().isdigit()]
            if nodes:
                routes.append(nodes)

    return {'routes': routes, 'cost': cost}
