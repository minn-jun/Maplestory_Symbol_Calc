from bisect import bisect_left
from dataclasses import dataclass
from itertools import product

from symbol_data import MESO_UNIT, SYMBOL_AREAS


TOP_N_SOLUTIONS = 10


@dataclass(frozen=True)
class UpgradeStep:
    area: str
    current_level: int
    target_level: int
    cost: int
    added_force: int


@dataclass(frozen=True)
class OptimizationResult:
    steps: tuple[UpgradeStep, ...]
    total_cost: int
    added_force: int

    @property
    def upgrade_count(self):
        return len(self.steps)


def calculate_upgrade_cost(area_key, current_level, target_level):
    area = SYMBOL_AREAS[area_key]
    total_cost = sum(area.costs.get(level, 0) for level in range(current_level + 1, target_level + 1))
    return total_cost * MESO_UNIT


def calculate_added_force(area_key, current_level, target_level):
    area = SYMBOL_AREAS[area_key]
    current_force = 0
    if current_level > 0:
        current_force = area.base_force + (current_level - 1) * area.force_per_level
    target_force = area.base_force + (target_level - 1) * area.force_per_level
    return target_force - current_force


def build_upgrade_options(current_symbols, accessible_areas):
    options_by_area = []

    for area_key in accessible_areas:
        area = SYMBOL_AREAS[area_key]
        current_level = int(current_symbols.get(area_key, {}).get("level", 0) or 0)
        area_options = [None]

        for target_level in range(max(current_level + 1, 1), area.max_level + 1):
            cost = calculate_upgrade_cost(area_key, current_level, target_level)
            added_force = calculate_added_force(area_key, current_level, target_level)
            if added_force > 0:
                area_options.append(UpgradeStep(area_key, current_level, target_level, cost, added_force))

        options_by_area.append(area_options)

    return options_by_area


def _combine_options(option_groups):
    combinations = []

    for option_tuple in product(*option_groups):
        steps = tuple(step for step in option_tuple if step is not None)
        combinations.append((
            sum(step.added_force for step in steps),
            sum(step.cost for step in steps),
            steps,
        ))

    return combinations


def _steps_key(steps):
    return tuple((step.area, step.target_level) for step in steps)


def _combo_key(combo):
    force, cost, steps = combo
    return cost, force, len(steps), _steps_key(steps)


def _result_key(result):
    return result.total_cost, result.added_force, result.upgrade_count, _steps_key(result.steps)


def _build_suffix_best(combinations, top_n):
    by_force = {}
    for combo in combinations:
        by_force.setdefault(combo[0], []).append(combo)

    forces = sorted(by_force)
    suffix_best = [None] * len(forces)
    best = []

    for index in range(len(forces) - 1, -1, -1):
        best = sorted(best + by_force[forces[index]], key=_combo_key)[:top_n]
        suffix_best[index] = best

    return forces, suffix_best


def find_best_solutions(current_symbols, accessible_areas, needed_force, top_n=TOP_N_SOLUTIONS):
    if needed_force <= 0:
        return []

    options_by_area = build_upgrade_options(current_symbols, accessible_areas)
    if not options_by_area:
        return []

    middle = len(options_by_area) // 2
    left = _combine_options(options_by_area[:middle])
    right_forces, right_suffix_best = _build_suffix_best(
        _combine_options(options_by_area[middle:]),
        top_n,
    )

    candidates = []
    for left_force, left_cost, left_steps in left:
        min_right_force = needed_force - left_force
        right_index = bisect_left(right_forces, max(0, min_right_force))
        if right_index >= len(right_forces):
            continue

        for right_force, right_cost, right_steps in right_suffix_best[right_index]:
            candidates.append(OptimizationResult(
                steps=tuple(sorted(left_steps + right_steps, key=lambda step: step.area)),
                total_cost=left_cost + right_cost,
                added_force=left_force + right_force,
            ))

    unique = {}
    for candidate in candidates:
        key = tuple((step.area, step.target_level) for step in candidate.steps)
        previous = unique.get(key)
        if previous is None or candidate.total_cost < previous.total_cost:
            unique[key] = candidate

    return sorted(
        unique.values(),
        key=_result_key,
    )[:top_n]
