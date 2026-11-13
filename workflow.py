"""Lesson-specific workflow. Read this file before the execution adapter."""
from __future__ import annotations
import asyncio
import json
from pathlib import Path
from runtime import atomic_json, contained_path, in_process_tool

async def run(agent, data):
    from itertools import combinations
    candidates = []
    registry = data['registry']
    if len(registry) > 12 or len({r['id'] for r in registry}) != len(registry) or any(r['cost'] < 0 for r in registry):
        raise ValueError('Use a small registry with unique IDs and nonnegative costs')
    for size in range(1, len(registry) + 1):
        for team in combinations(registry, size):
            skills = set().union(*(set(member['skills']) for member in team))
            cost = sum(member['cost'] for member in team)
            if set(data['required']) <= skills and cost <= data['budget']:
                candidates.append((size, cost, tuple(m['id'] for m in team), team))
    if not candidates:
        return {'status': 'uncovered', 'team': []}
    _, cost, ids, team = min(candidates, key=lambda item: item[:3])
    deliverables = {}
    for member in team:
        deliverables[member['id']] = await agent.ask(member['id'], 'Produce a deliverable within your declared skills.', member, 'Prepared deliverable for ' + ', '.join(member['skills']))
    return {'status': 'covered', 'team': list(ids), 'cost': cost, 'deliverables': deliverables}
