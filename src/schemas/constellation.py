from typing import List, Optional

from pydantic import BaseModel, ConfigDict, Field, model_validator


class StarPoint(BaseModel):
    model_config = ConfigDict(extra="forbid")

    name: str
    x: float
    y: float
    z: float


class ClusterParams(BaseModel):
    model_config = ConfigDict(extra="forbid")

    min_size: int = Field(..., ge=2)
    max_size: int = Field(..., ge=2)
    max_neighbor_distance: float = Field(..., gt=0)

    @model_validator(mode="after")
    def validate_sizes(self) -> "ClusterParams":
        if self.min_size > self.max_size:
            raise ValueError("min_size cannot be greater than max_size")
        return self


class TargetEdge(BaseModel):
    model_config = ConfigDict(extra="forbid", populate_by_name=True)

    from_node: int = Field(..., alias="from", ge=0)
    to: int = Field(..., ge=0)
    distance: float = Field(..., gt=0)


class TargetConstellation(BaseModel):
    model_config = ConfigDict(extra="forbid")

    edges: List[TargetEdge]

    @model_validator(mode="after")
    def validate_is_tree(self) -> "TargetConstellation":
        edges = self.edges

        if not edges:
            raise ValueError("Target constellation must have at least one edge")

        node_set = set()
        undirected_edges = set()
        for edge in edges:
            node_set.add(edge.from_node)
            node_set.add(edge.to)

            a, b = sorted((edge.from_node, edge.to))
            if a == b:
                raise ValueError("Loops are not allowed")
            if (a, b) in undirected_edges:
                raise ValueError("Multiple edges are not allowed")
            undirected_edges.add((a, b))

        n = len(node_set)
        if n < 2 or n > 50:
            raise ValueError("Target constellation vertex count must be within [2, 50]")

        if node_set != set(range(n)):
            raise ValueError("Target vertices must be indexed consecutively from 0 to n-1")

        if len(edges) != n - 1:
            raise ValueError("Target graph is not a tree: number of edges must be n-1")

        adjacency = [[] for _ in range(n)]
        for edge in edges:
            adjacency[edge.from_node].append(edge.to)
            adjacency[edge.to].append(edge.from_node)

        visited = [False] * n
        stack = [0]
        visited[0] = True

        while stack:
            current = stack.pop()
            for neighbor in adjacency[current]:
                if not visited[neighbor]:
                    visited[neighbor] = True
                    stack.append(neighbor)

        if not all(visited):
            raise ValueError("Target constellation graph is not connected")

        return self


class ConstellationFinderRequest(BaseModel):
    model_config = ConfigDict(extra="forbid")

    stars: List[StarPoint] = Field(..., max_length=1000)
    cluster_params: ClusterParams
    target_constellation: TargetConstellation

    @model_validator(mode="after")
    def validate_stars(self) -> "ConstellationFinderRequest":
        star_names = [star.name for star in self.stars]
        if len(star_names) != len(set(star_names)):
            raise ValueError("Star names must be unique")

        target_nodes = len(self.target_constellation.edges) + 1
        if self.cluster_params.max_size < target_nodes:
            raise ValueError("max_size cannot be smaller than target constellation size")

        return self


class ConstellationFinderResponse(BaseModel):
    model_config = ConfigDict(extra="forbid")

    found: bool
    matched_stars: Optional[List[str]] = None
