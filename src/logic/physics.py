from typing import Tuple

# Константа точности для сравнения float
EPS = 1e-9


def compute_launch_cost(mass_shuttle: float, fuel_consumption: float) -> float:
    """
    Стоимость вывода шаттла на орбиту в единицах топлива.
    По условию fuel_consumption задает расход на 1 единицу массы.
    """
    return mass_shuttle * fuel_consumption

def compute_mass(mass_shuttle: float, fuel_units: float, mass_fuel_unit: float) -> float:
    """Вычисляет полную массу системы. Масса не может быть меньше массы пустого шаттла."""
    safe_fuel = max(0.0, fuel_units)
    return mass_shuttle + safe_fuel * mass_fuel_unit

def compute_acceleration(power_per_unit: float, mass_shuttle: float, 
                         fuel_units: float, mass_fuel_unit: float) -> float:
    """Расчет ускорения a = F / m."""
    total_mass = compute_mass(mass_shuttle, fuel_units, mass_fuel_unit)
    if total_mass < EPS:
        return 0.0
    return power_per_unit / total_mass

def engine_tick(velocity: float, fuel_left: float, mass_shuttle: float, 
                mass_fuel_unit: float, power_per_unit: float, direction: int) -> Tuple[float, float]:
    """
    Моделирует 1 секунду работы двигателя.
    Согласно условию: расход 1 ед. происходит мгновенно, затем 1 сек. идет ускорение.
    """
    if fuel_left < 1.0:
        return velocity, fuel_left

    accel = compute_acceleration(power_per_unit, mass_shuttle, fuel_left, mass_fuel_unit)
    new_velocity = velocity + (direction * accel)
    
    # При торможении скорость не может стать отрицательной
    if direction == -1 and new_velocity < 0:
        new_velocity = 0.0
        
    return new_velocity, fuel_left - 1.0

def simulate_acceleration(dist_limit: float, fuel_at_start: float, mass_shuttle: float, 
                         mass_fuel_unit: float, power_per_unit: float) -> Tuple[float, float, int, int]:
    """Фаза разгона: лимитирована 50% топлива и 50% пути."""
    v, s, t, spent = 0.0, 0.0, 0, 0
    max_fuel_to_burn = int(fuel_at_start // 2)

    for _ in range(max_fuel_to_burn):
        v_next, _ = engine_tick(v, fuel_at_start - spent, mass_shuttle, 
                                mass_fuel_unit, power_per_unit, direction=1)
        
        # Условие "не более половины пути"
        if s + v_next > dist_limit / 2:
            break
            
        v = v_next
        s += v
        t += 1
        spent += 1
        
    return v, s, t, spent

def simulate_braking(v_start: float, fuel_remaining: float, mass_shuttle: float, 
                     mass_fuel_unit: float, power_per_unit: float) -> Tuple[int, int, bool]:
    """Фаза торможения: попытка погасить скорость до EPS."""
    v, t, spent = v_start, 0, 0
    fuel_pool = int(fuel_remaining)

    while v > EPS and spent < fuel_pool:
        v, _ = engine_tick(v, fuel_remaining - spent, mass_shuttle, 
                           mass_fuel_unit, power_per_unit, direction=-1)
        t += 1
        spent += 1
        
    return t, spent, v <= EPS
