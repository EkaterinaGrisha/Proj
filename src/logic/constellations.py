import math
from dataclasses import dataclass
from typing import Dict, List, Optional, Tuple


@dataclass(frozen=True)
class Star:
    name: str
    x: float
    y: float
    z: float


def distance(a: Star, b: Star) -> float:
    dx = a.x - b.x
    dy = a.y - b.y
    dz = a.z - b.z
    return math.sqrt(dx * dx + dy * dy + dz * dz)


def connected_components(stars: List[Star], max_neighbor_distance: float) -> List[List[int]]:
    n = len(stars)
    if n == 0:
        return []

    adjacency = [[] for _ in range(n)]
    for i in range(n):
        for j in range(i + 1, n):
            if distance(stars[i], stars[j]) <= max_neighbor_distance:
                adjacency[i].append(j)
                adjacency[j].append(i)

    visited = [False] * n
    components: List[List[int]] = []
    for start in range(n):
        if visited[start]:
            continue
        stack = [start]
        visited[start] = True
        component = []
        while stack:
            node = stack.pop()
            component.append(node)
            for neighbor in adjacency[node]:
                if not visited[neighbor]:
                    visited[neighbor] = True
                    stack.append(neighbor)
        components.append(component)

    return components


def build_mst(stars: List[Star], component: List[int]) -> List[Tuple[int, int, float]]:
    size = len(component)
    if size <= 1:
        return []

    in_mst = [False] * size
    min_edge = [float("inf")] * size
    parent = [-1] * size
    min_edge[0] = 0.0
    edges: List[Tuple[int, int, float]] = []

    for _ in range(size):
        u = -1
        for i in range(size):
            if not in_mst[i] and (u == -1 or min_edge[i] < min_edge[u]):
                u = i

        in_mst[u] = True
        if parent[u] != -1:
            left_global = component[parent[u]]
            right_global = component[u]
            edges.append((left_global, right_global, min_edge[u]))

        for v in range(size):
            if in_mst[v]:
                continue
            d = distance(stars[component[u]], stars[component[v]])
            if d < min_edge[v]:
                min_edge[v] = d
                parent[v] = u

    return edges


def build_tree(n: int, edges: List[Tuple[int, int, float]]) -> Tuple[List[List[int]], Dict[Tuple[int, int], float]]:
    adjacency = [[] for _ in range(n)]
    edge_lengths: Dict[Tuple[int, int], float] = {}
    for u, v, w in edges:
        adjacency[u].append(v)
        adjacency[v].append(u)
        edge_lengths[(u, v)] = w
        edge_lengths[(v, u)] = w
    return adjacency, edge_lengths


def has_order_conflict(assigned_pairs: List[Tuple[float, float]], new_pair: Tuple[float, float]) -> bool:
    td_new, cd_new = new_pair
    for td_old, cd_old in assigned_pairs:
        if td_old < td_new and not (cd_old < cd_new):
            return True
        if td_old > td_new and not (cd_old > cd_new):
            return True
    return False


def find_mapping(
    target_adj: List[List[int]],
    candidate_adj: List[List[int]],
    target_len: Dict[Tuple[int, int], float],
    candidate_len: Dict[Tuple[int, int], float],
) -> Optional[List[int]]:
    n = len(target_adj)
    target_order = sorted(range(n), key=lambda x: len(target_adj[x]), reverse=True)

    mapping = [-1] * n
    used_candidate = [False] * n
    assigned_edge_pairs: List[Tuple[float, float]] = []

    def select_next_vertex() -> int:
        best = -1
        best_domain = 10**9
        for t in target_order:
            if mapping[t] != -1:
                continue

            mapped_neighbors = 0
            domain_size = 0
            for c in range(n):
                if used_candidate[c] or len(candidate_adj[c]) != len(target_adj[t]):
                    continue
                ok = True
                for nt in target_adj[t]:
                    mc = mapping[nt]
                    if mc == -1:
                        continue
                    mapped_neighbors += 1
                    if mc not in candidate_adj[c]:
                        ok = False
                        break
                if ok:
                    domain_size += 1

            if domain_size < best_domain or (domain_size == best_domain and mapped_neighbors > 0):
                best = t
                best_domain = domain_size
        return best

    def dfs(mapped_count: int) -> bool:
        if mapped_count == n:
            return True

        t = select_next_vertex()
        if t == -1:
            return False

        candidates = [c for c in range(n) if not used_candidate[c] and len(candidate_adj[c]) == len(target_adj[t])]
        candidates.sort(key=lambda node: len(candidate_adj[node]), reverse=True)

        for c in candidates:
            ok = True
            newly_added_pairs: List[Tuple[float, float]] = []

            for nt in target_adj[t]:
                mc = mapping[nt]
                if mc == -1:
                    continue
                if mc not in candidate_adj[c]:
                    ok = False
                    break
                pair = (target_len[(t, nt)], candidate_len[(c, mc)])
                if has_order_conflict(assigned_edge_pairs, pair) or has_order_conflict(newly_added_pairs, pair):
                    ok = False
                    break
                newly_added_pairs.append(pair)

            if not ok:
                continue

            mapping[t] = c
            used_candidate[c] = True
            assigned_edge_pairs.extend(newly_added_pairs)

            if dfs(mapped_count + 1):
                return True

            for _ in newly_added_pairs:
                assigned_edge_pairs.pop()
            mapping[t] = -1
            used_candidate[c] = False

        return False

    if dfs(0):
        return mapping
    return None


def solve_task_3(request_data) -> dict:
    stars = [Star(name=s.name, x=s.x, y=s.y, z=s.z) for s in request_data.stars]
    components = connected_components(stars, request_data.cluster_params.max_neighbor_distance)

    target_n = len(request_data.target_constellation.edges) + 1
    target_edges = [
        (edge.from_node, edge.to, edge.distance)
        for edge in request_data.target_constellation.edges
    ]
    target_adj, target_lengths = build_tree(target_n, target_edges)

    matches: List[List[str]] = []

    for component in components:
        if not (request_data.cluster_params.min_size <= len(component) <= request_data.cluster_params.max_size):
            continue
        if len(component) != target_n:
            continue

        mst_edges_global = build_mst(stars, component)

        local_index = {global_idx: i for i, global_idx in enumerate(component)}
        mst_edges_local = [
            (local_index[u], local_index[v], w)
            for u, v, w in mst_edges_global
        ]

        candidate_adj, candidate_lengths = build_tree(target_n, mst_edges_local)
        mapping = find_mapping(target_adj, candidate_adj, target_lengths, candidate_lengths)
        if mapping is None:
            continue

        matched_names = [stars[component[mapping[i]]].name for i in range(target_n)]
        matches.append(matched_names)

        if len(matches) > 1:
            return {"found": False}

    if len(matches) == 1:
        return {"found": True, "matched_stars": matches[0]}
    return {"found": False}
