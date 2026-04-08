from pydantic import BaseModel, Field, field_validator, model_validator
from typing import List, Optional

class StarPoint(BaseModel):
    name: str
    x: float
    y: float
    z: float

class ClusterParams(BaseModel):
    min_size: int = Field(..., ge=2)
    max_size: int = Field(..., ge=2)
    max_neighbor_distance: float = Field(..., gt=0)

    @model_validator(mode='after')
    def validate_sizes(self) -> 'ClusterParams':
        if self.min_size > self.max_size:
            raise ValueError("min_size cannot be greater than max_size")
        return self

class TargetEdge(BaseModel):
    from_node: int = Field(..., alias="from", ge=0)
    to: str | int = Field(...) # ТЗ говорит об индексах 0..n-1
    distance: float = Field(..., gt=0)

    @field_validator('to')
    @classmethod
    def validate_to_index(cls, v):
        # Приводим к int, если пришла строка, или валимся
        try:
            val = int(v)
            if val < 0:
                raise ValueError
            return val
        except (ValueError, TypeError):
            raise ValueError("Edge 'to' must be a non-negative integer index")

    class Config:
        populate_by_name = True

class TargetConstellation(BaseModel):
    edges: List[TargetEdge]

    @field_validator('edges')
    @classmethod
    def validate_is_tree(cls, edges: List[TargetEdge]):
        if not edges:
            raise ValueError("Target constellation must have at least one edge")

        # Собираем все вершины
        nodes = set()
        for e in edges:
            nodes.add(e.from_node)
            nodes.add(e.to)
        
        n = len(nodes)
        # У дерева с N вершинами должно быть ровно N-1 ребро
        if len(edges) != n - 1:
            raise ValueError(f"Target graph is not a tree (nodes: {n}, edges: {len(edges)})")

        # Проверка связности (BFS/DFS)
        adj = {node: [] for node in nodes}
        for e in edges:
            adj[e.from_node].append(e.to)
            adj[e.to].append(e.from_node)

        start_node = next(iter(nodes))
        visited = {start_node}
        stack = [start_node]

        while stack:
            curr = stack.pop()
            for neighbor in adj[curr]:
                if neighbor not in visited:
                    visited.add(neighbor)
                    stack.append(neighbor)
        
        if len(visited) != n:
            raise ValueError("Target constellation graph is not connected")
            
        return edges

class ConstellationFinderRequest(BaseModel):
    stars: List[StarPoint]
    cluster_params: ClusterParams
    target_constellation: TargetConstellation

class ConstellationFinderResponse(BaseModel):
    found: bool
    matched_stars: Optional[List[str]] = None
