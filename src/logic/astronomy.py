import math
from typing import Dict, List, Optional, Tuple


class StarSystemSimulator:
    def __init__(self, bodies: List, target_star_vector):
        self.bodies_map = {body.id: body for body in bodies}

        vx, vy = target_star_vector.x, target_star_vector.y
        magnitude = math.hypot(vx, vy)
        self.vx = vx / magnitude
        self.vy = vy / magnitude

        self._pos_cache: Dict[str, Tuple[float, float]] = {}
        self._current_t: Optional[float] = None

    def get_pos(self, body_id: str, t: float) -> Tuple[float, float]:
        if self._current_t != t:
            self._pos_cache = {}
            self._current_t = t

        if body_id == "Atlas":
            return 0.0, 0.0

        if body_id in self._pos_cache:
            return self._pos_cache[body_id]

        body = self.bodies_map[body_id]
        if body.type == "star":
            position = (body.position.x, body.position.y)
        else:
            parent_x, parent_y = self.get_pos(body.parent_id, t)
            direction = -1 if body.rotation_clockwise else 1
            angle_deg = (body.initial_angle + (direction * body.angular_velocity * t)) % 360
            angle_rad = math.radians(angle_deg)
            position = (
                parent_x + body.orbit_radius * math.cos(angle_rad),
                parent_y + body.orbit_radius * math.sin(angle_rad),
            )

        self._pos_cache[body_id] = position
        return position

    def is_star_visible(self, t: float) -> bool:
        for body_id, body in self.bodies_map.items():
            center_x, center_y = self.get_pos(body_id, t)
            projection = center_x * self.vx + center_y * self.vy

            if projection <= 0:
                continue

            distance_to_ray = abs(center_x * self.vy - center_y * self.vx)
            if distance_to_ray <= body.radius:
                return False

        return True

    def is_second_fully_visible(self, second: int) -> bool:
        """
        Консервативная проверка непрерывной видимости на интервале [second, second+1).
        Проверяем несколько точек внутри секунды, чтобы отсеять частичные затмения.
        """
        sample_points = (0.0, 0.2, 0.4, 0.6, 0.8, 0.999999)
        for offset in sample_points:
            if not self.is_star_visible(second + offset):
                return False
        return True


def find_transmission_window(
    simulator: StarSystemSimulator,
    required_time: int,
    max_wait: int = 10**9,
):
    """
    Ищет ближайший интервал, где каждая секунда полностью видима.
    """
    t = 0
    inf_threshold = 2 * 10**6

    while t <= max_wait:
        if simulator.is_second_fully_visible(t):
            start_window = t
            duration = 0

            while t <= max_wait and simulator.is_second_fully_visible(t):
                duration += 1
                t += 1
                if duration >= inf_threshold:
                    return start_window, "inf"

            if duration >= required_time:
                return start_window, duration
        else:
            t += 1

    return None, None
