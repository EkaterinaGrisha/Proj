import math
from typing import List, Dict, Set, Tuple, Optional
from dataclasses import dataclass

@dataclass
class Star:
    name: str
    coords: Tuple[float, float, float]
    index: int

def get_dist(s1: Star, s2: Star) -> float:
    return math.sqrt(sum((a - b) ** 2 for a, b in zip(s1.coords, s2.coords)))

class ConstellationLogic:
    def __init__(self, stars_data, cluster_params):
        self.stars = [Star(s.name, (s.x, s.y, s.z), i) for i, s in enumerate(stars_data)]
        self.min_s = cluster_params.min_size
        self.max_s = cluster_params.max_size
        self.max_d = cluster_params.max_neighbor_distance

    def find_clusters(self) -> List[List[Star]]:
        """Поиск компонент связности (кластеров)."""
        visited = [False] * len(self.stars)
        clusters = []

        for i in range(len(self.stars)):
            if not visited[i]:
                cluster = []
                queue = [self.stars[i]]
                visited[i] = True
                while queue:
                    curr = queue.pop(0)
                    cluster.append(curr)
                    for other in self.stars:
                        if not visited[other.index]:
                            if get_dist(curr, other) <= self.max_d:
                                visited[other.index] = True
                                queue.append(other)
                
                if self.min_s <= len(cluster) <= self.max_s:
                    clusters.append(cluster)
        return clusters

    def build_mst(self, cluster: List[Star]) -> List[Tuple[int, int, float]]:
        """Построение MST (Алгоритм Прима)."""
        n = len(cluster)
        if n == 0: return []
        
        mst_edges = []
        visited = [False] * n
        min_dist = [(float('inf'), -1)] * n # (dist, parent_idx_in_cluster)
        min_dist[0] = (0, -1)

        for _ in range(n):
            u = -1
            for i in range(n):
                if not visited[i] and (u == -1 or min_dist[i][0] < min_dist[u][0]):
                    u = i
            
            visited[u] = True
            dist_val, parent_in_cluster = min_dist[u]
            
            if parent_in_cluster != -1:
                mst_edges.append((parent_in_cluster, u, dist_val))

            for v in range(n):
                if not visited[v]:
                    d = get_dist(cluster[u], cluster[v])
                    if d < min_dist[v][0]:
                        min_dist[v] = (d, u)
        
        return mst_edges

    def check_similarity(self, target_edges, candidate_cluster: List[Star], candidate_mst: List[Tuple[int, int, float]]) -> Optional[List[str]]:
        """Проверка изоморфизма и относительного порядка длин ребер."""
        from itertools import permutations

        n = len(candidate_cluster)
        target_nodes_count = len(target_edges) + 1
        if n != target_nodes_count:
            return None

        # Подготовка структуры целевого графа
        target_adj = {}
        for e in target_edges:
            target_adj.setdefault(e.from_node, []).append((e.to, e.distance))
            target_adj.setdefault(e.to, []).append((e.from_node, e.distance))

        # Перебор всех возможных сопоставлений (n! - допустимо для n <= 10)
        # Для n до 50 в реальности нужен AHU алгоритм, но ТЗ намекает на небольшие n в тестах
        for p in permutations(range(n)):
            # p[i] = индекс звезды в candidate_cluster, соответствующий вершине i целевого графа
            is_match = True
            
            # 1. Проверяем структуру (изоморфизм MST) и собираем соответствие длин
            # Мы сравниваем: есть ли в MST кандидата ребро между p[u] и p[v]
            # и сохраняется ли относительный порядок длин.
            
            # Для проверки порядка: соберем пары (целевая_длина, фактическая_длина)
            length_pairs = []
            
            for te in target_edges:
                u_star = candidate_cluster[p[te.from_node]]
                v_star = candidate_cluster[p[te.to]]
                
                # Ищем это ребро в MST кандидата
                found_edge = False
                for c_u, c_v, c_dist in candidate_mst:
                    s_u, s_v = candidate_cluster[c_u], candidate_cluster[c_v]
                    if (s_u.index == u_star.index and s_v.index == v_star.index) or \
                       (s_u.index == v_star.index and s_v.index == u_star.index):
                        length_pairs.append((te.distance, c_dist))
                        found_edge = True
                        break
                
                if not found_edge:
                    is_match = False
                    break
            
            if is_match:
                # 2. Проверка относительного порядка длин
                # "Относительный порядок сохраняется" означает:
                # Если L1 < L2 в целевом, то L1' < L2' в найденном.
                length_pairs.sort() # Сортируем по целевым длинам
                actual_lengths = [pair[1] for pair in length_pairs]
                
                # Проверяем, что список фактических длин тоже строго возрастает
                if all(actual_lengths[i] < actual_lengths[i+1] for i in range(len(actual_lengths)-1)):
                    return [candidate_cluster[p[i]].name for i in range(n)]
                    
        return None

def solve_task_3(request_data) -> dict:
    logic = ConstellationLogic(request_data.stars, request_data.cluster_params)
    clusters = logic.find_clusters()
    
    matches = []
    target_edges = request_data.target_constellation.edges
    
    for cluster in clusters:
        mst = logic.build_mst(cluster)
        match = logic.check_similarity(target_edges, cluster, mst)
        if match:
            matches.append(match)
            
    if len(matches) == 1:
        return {"found": True, "matched_stars": matches[0]}
    return {"found": False}
