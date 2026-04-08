import math
from typing import Dict, Tuple, List, Union, Optional

class StarSystemSimulator:
    def __init__(self, bodies: List, target_star_vector):
        self.bodies_map = {b.id: b for b in bodies}
        # Нормализуем вектор направления на целевую звезду один раз
        vx, vy = target_star_vector.x, target_star_vector.y
        mag = math.sqrt(vx**2 + vy**2)
        
        # Вектор луча зрения (нормализованный)
        self.vx = vx / mag
        self.vy = vy / mag
        
        # Кэш позиций для текущего момента времени t
        self._pos_cache: Dict[str, Tuple[float, float]] = {}
        self._current_t: Optional[float] = None

    def get_pos(self, body_id: str, t: float) -> Tuple[float, float]:
        """Вычисляет координаты тела с использованием мемоизации для времени t."""
        # Если время изменилось, очищаем кэш
        if self._current_t != t:
            self._pos_cache = {}
            self._current_t = t
            
        if body_id == "Atlas":
            return 0.0, 0.0
        
        if body_id in self._pos_cache:
            return self._pos_cache[body_id]
        
        body = self.bodies_map[body_id]
        
        if body.type == "star":
            res = (body.position.x, body.position.y)
        else:
            # Рекурсивный вызов для родителя
            px, py = self.get_pos(body.parent_id, t)
            
            # Угловой расчет: alpha = initial + (dir * w * t)
            direction = -1 if body.rotation_clockwise else 1
            # Используем fmod для предотвращения огромных значений углов при больших t
            total_angle_deg = (body.initial_angle + (direction * body.angular_velocity * t)) % 360
            angle_rad = math.radians(total_angle_deg)
            
            res = (
                px + body.orbit_radius * math.cos(angle_rad),
                py + body.orbit_radius * math.sin(angle_rad)
            )
        
        self._pos_cache[body_id] = res
        return res

    def is_star_visible(self, t: float) -> bool:
        """Проверяет, не заслоняет ли какое-либо тело луч зрения в момент t."""
        for body_id in self.bodies_map:
            body = self.bodies_map[body_id]
            cx, cy = self.get_pos(body_id, t)
            
            # 1. Проекция центра тела на вектор луча: dot_product = (C * V)
            # Так как V нормализован, proj — это расстояние вдоль луча
            proj = cx * self.vx + cy * self.vy
            
            # Если тело "за спиной" наблюдателя (проекция <= 0), оно не может заслонять
            if proj <= 0:
                continue
                
            # 2. Расстояние от центра тела до прямой (луча)
            # Для нормализованного вектора: d = |cx*vy - cy*vx|
            dist_to_ray = abs(cx * self.vy - cy * self.vx)
            
            # Если кратчайшее расстояние до луча меньше радиуса тела — звезда скрыта
            if dist_to_ray < body.radius:
                return False
                
        return True

def find_transmission_window(simulator: StarSystemSimulator, required_time: int, max_wait: int = 10**9):
    """
    Алгоритм поиска первого подходящего окна.
    Проверка идет строго по целым секундам согласно ТЗ.
    """
    t = 0
    # Предел для определения "бесконечной" видимости
    # Если звезда видна непрерывно более 2 млн секунд, считаем "inf"
    INF_THRESHOLD = 2 * 10**6 

    while t <= max_wait:
        if simulator.is_star_visible(float(t)):
            start_window = t
            duration = 0
            
            # Проверяем, как долго длится это окно
            while t <= max_wait and simulator.is_star_visible(float(t)):
                duration += 1
                t += 1
                if duration >= INF_THRESHOLD:
                    return start_window, "inf"
            
            # Окно закрылось или достигнут предел. Проверяем, хватило ли времени.
            if duration >= required_time:
                return start_window, duration
        else:
            t += 1
            
    return None, None
