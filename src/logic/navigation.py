import heapq
from .physics import simulate_acceleration, simulate_braking, compute_launch_cost

def find_optimal_path(data):
    # Построение графа
    graph = {}
    for edge in data.edges:
        graph.setdefault(edge.from_node, []).append((edge.to, edge.distance))
    
    bodies_map = {b.id: b for b in data.bodies}
    
    # Ресурсный старт
    launch_cost = compute_launch_cost(data.mass_shuttle, data.fuel_consumption)
    initial_fuel = data.total_fuel - launch_cost
    if initial_fuel < 0:
        return {"can_reach": False}

    # Dijkstra: (time, node, fuel, velocity, path)
    queue = [(0.0, "start_point", float(initial_fuel), 0.0, ["start_point"])]
    visited = {}

    while queue:
        curr_t, curr_node, fuel, vel, path = heapq.heappop(queue)

        # 1. Проверка цели (с торможением)
        if curr_node == "rescue_point":
            t_brake, _, success = simulate_braking(
                vel, fuel, data.mass_shuttle, data.mass_fuel_unit, data.power_per_unit
            )
            if success and (curr_t + t_brake) <= data.oxygen_time:
                return {
                    "can_reach": True,
                    "min_flight_time": round(float(curr_t + t_brake), 1),
                    "route": path
                }
            continue

        # 2. Оптимизация состояний (квантуем скорость для visited)
        state = (curr_node, int(fuel), round(vel, 2))
        if visited.get(state, float('inf')) <= curr_t:
            continue
        visited[state] = curr_t

        if curr_node not in graph:
            continue

        # 3. Переходы
        for neighbor, dist in graph[curr_node]:
            if curr_node == "start_point":
                # Первый разгон
                v_seg, s_acc, t_acc, f_spent = simulate_acceleration(
                    dist, fuel, data.mass_shuttle, data.mass_fuel_unit, data.power_per_unit
                )
                if v_seg < 1e-6: continue
                t_seg = t_acc + (dist - s_acc) / v_seg
                f_seg, v_next = fuel - f_spent, v_seg
            else:
                # Полет по инерции
                if vel < 1e-6: continue
                t_seg, f_seg, v_next = dist / vel, fuel, vel

            # Кислородный фильтр
            if curr_t + t_seg > data.oxygen_time:
                continue

            # Гравитационные маневры (Assist)
            options = [(t_seg, f_seg, v_next)]
            if neighbor in bodies_map:
                for assist in bodies_map[neighbor].gravity_assists:
                    if f_seg >= assist.fuel_consumption:
                        options.append((
                            t_seg + assist.time_to_execute,
                            f_seg - assist.fuel_consumption,
                            v_next + assist.velocity_gain
                        ))

            for o_t, o_f, o_v in options:
                if curr_t + o_t <= data.oxygen_time:
                    heapq.heappush(queue, (curr_t + o_t, neighbor, o_f, o_v, path + [neighbor]))

    return {"can_reach": False}
