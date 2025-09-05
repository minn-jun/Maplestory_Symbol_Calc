import heapq
from symbol_data import ARCANE_SYMBOLS, AUTHENTIC_SYMBOLS

TOP_N_SOLUTIONS = 10

def _calculate_upgrade_cost(area, current_level, target_level, symbol_data_set, cost_cache):
    """심볼 업그레이드 비용을 계산하고 캐시합니다."""
    cache_key = (area, current_level, target_level)
    if cache_key in cost_cache:
        return cost_cache[cache_key]
    
    total_cost = 0
    for level in range(current_level + 1, target_level + 1):
        cost = symbol_data_set.get(area, {}).get(level, 0)
        total_cost += cost
    
    result = total_cost * 10000
    cost_cache[cache_key] = result
    return result

def find_best_solutions(current_symbols, accessible_areas, needed_force, is_arcane):
    """DP와 백트래킹을 사용하여 최적의 심볼 강화 조합을 찾습니다."""
    
    symbol_data_set = ARCANE_SYMBOLS if is_arcane else AUTHENTIC_SYMBOLS
    base_force = 30 if is_arcane else 10
    force_per_level = 10
    max_level = 20 if is_arcane else 11
    
    cost_cache = {}
    upgrade_options = {}
    
    for area in accessible_areas:
        current_level = current_symbols.get(area, {"level": 0})["level"]
        options = []
        start_level = max(current_level, 1)
        
        for target_level in range(start_level, max_level + 1):
            if target_level > current_level:
                cost = _calculate_upgrade_cost(area, current_level, target_level, symbol_data_set, cost_cache)
                added_force = (base_force if current_level == 0 else 0) + (target_level - max(current_level, 1)) * force_per_level
                if current_level == 0:
                    added_force = base_force + (target_level - 1) * force_per_level

                if cost > 0:
                    options.append((target_level, cost, added_force))
        
        options.sort(key=lambda x: x[1])
        upgrade_options[area] = options

    solution_heap = []
    # [FIX] 고유 ID를 위한 카운터 추가
    solution_counter = 0
    
    def backtrack(area_idx, current_force, current_cost, current_plan):
        # [FIX] nonlocal로 외부 카운터 변수를 수정할 수 있도록 선언
        nonlocal solution_counter

        # 가지치기
        if len(solution_heap) >= TOP_N_SOLUTIONS and current_cost > -solution_heap[0][0]:
            return

        # 목표 달성 시 힙에 추가
        if current_force >= needed_force:
            # [FIX] 튜플에 고유 ID(solution_counter)를 추가하여 딕셔너리 비교 방지
            heapq.heappush(solution_heap, (-current_cost, current_force, solution_counter, current_plan.copy()))
            solution_counter += 1 # 다음 해를 위해 카운터 증가
            
            if len(solution_heap) > TOP_N_SOLUTIONS:
                heapq.heappop(solution_heap)
            return

        if area_idx >= len(accessible_areas):
            return
            
        area = accessible_areas[area_idx]

        # 1. 업그레이드하지 않는 경우
        backtrack(area_idx + 1, current_force, current_cost, current_plan)
        
        # 2. 업그레이드하는 경우
        current_level = current_symbols.get(area, {"level": 0})["level"]
        for target_level, cost, added_force in upgrade_options.get(area, []):
            new_cost = current_cost + cost
            
            if len(solution_heap) >= TOP_N_SOLUTIONS and new_cost > -solution_heap[0][0]:
                break

            current_plan[area] = (current_level, target_level, cost)
            backtrack(area_idx + 1, current_force + added_force, new_cost, current_plan)
            del current_plan[area]

    backtrack(0, 0, 0, {})
    
    sorted_solutions = []
    while solution_heap:
        # [FIX] 추가된 고유 ID를 언패킹하지만 사용하지는 않음 (_)
        cost, force, _, plan = heapq.heappop(solution_heap)
        sorted_solutions.append((plan, -cost, force))
    
    return sorted(sorted_solutions, key=lambda x: x[1])