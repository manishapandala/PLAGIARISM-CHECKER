from __future__ import annotations

import heapq
import os
from collections import defaultdict, deque
from typing import Any

from neo4j import GraphDatabase


class Interface:
    OD_GRAPH_NAME = "tester_od_graph"
    ALLOWED_WEIGHT_PROPERTIES = {"avg_distance", "avg_fare", "trip_count"}

    def __init__(
        self,
        uri: str | None = None,
        user: str | None = None,
        password: str | None = None,
    ) -> None:
        bolt_uri = uri or os.getenv("NEO4J_URI", "bolt://localhost:7687")
        username = user or os.getenv("NEO4J_USER", "neo4j")
        passwd = password or os.getenv("NEO4J_PASSWORD", "graphprocessing")
        self.driver = GraphDatabase.driver(bolt_uri, auth=(username, passwd))

    def close(self) -> None:
        if getattr(self, "driver", None) is not None:
            self.driver.close()

    def __del__(self) -> None:
        try:
            self.close()
        except Exception:
            pass

    def _drop_projection_if_exists(self, session: Any, graph_name: str) -> None:
        exists_result = session.run(
            "CALL gds.graph.exists($graph_name) YIELD exists RETURN exists AS exists",
            graph_name=graph_name,
        ).single()
        if exists_result and bool(exists_result["exists"]):
            session.run("CALL gds.graph.drop($graph_name)", graph_name=graph_name).consume()

    def _validate_weight_property(self, weight_property: str) -> None:
        if weight_property not in self.ALLOWED_WEIGHT_PROPERTIES:
            raise ValueError(
                f"weight_property must be one of {sorted(self.ALLOWED_WEIGHT_PROPERTIES)}"
            )

    def build_od_graph(self) -> dict:
        with self.driver.session() as session:
            self._drop_projection_if_exists(session, self.OD_GRAPH_NAME)

            session.run("MATCH ()-[r:OD]->() DELETE r").consume()

            session.run(
                """
                MATCH (s:Location)-[t:TRIP]->(d:Location)
                WITH s, d,
                     avg(t.distance) AS avg_distance,
                     avg(t.fare) AS avg_fare,
                     count(t) AS trip_count
                CREATE (s)-[:OD {
                    avg_distance: avg_distance,
                    avg_fare: avg_fare,
                    trip_count: trip_count
                }]->(d)
                """
            ).consume()

            node_count = session.run(
                "MATCH (n:Location) RETURN count(n) AS count"
            ).single()["count"]
            rel_count = session.run(
                "MATCH ()-[r:OD]->() RETURN count(r) AS count"
            ).single()["count"]

        return {"nodes": int(node_count), "relationships": int(rel_count)}

    def pagerank(self, max_iterations: int, weight_property: str) -> list[dict]:
        self._validate_weight_property(weight_property)

        with self.driver.session() as session:
            self._drop_projection_if_exists(session, self.OD_GRAPH_NAME)

            session.run(
                """
                CALL gds.graph.project(
                    $graph_name,
                    'Location',
                    {
                        OD: {
                            orientation: 'NATURAL',
                            properties: ['avg_distance', 'avg_fare', 'trip_count']
                        }
                    }
                )
                """,
                graph_name=self.OD_GRAPH_NAME,
            ).consume()

            rows = list(
                session.run(
                    """
                    CALL gds.pageRank.stream(
                        $graph_name,
                        {
                            maxIterations: $max_iterations,
                            relationshipWeightProperty: $weight_property
                        }
                    )
                    YIELD nodeId, score
                    RETURN toInteger(gds.util.asNode(nodeId).name) AS name, score
                    ORDER BY score DESC, name ASC
                    """,
                    graph_name=self.OD_GRAPH_NAME,
                    max_iterations=max_iterations,
                    weight_property=weight_property,
                )
            )

        if not rows:
            return []

        max_row = rows[0]
        min_score = min(float(row["score"]) for row in rows)
        min_name = min(int(row["name"]) for row in rows if float(row["score"]) == min_score)
        min_row = next(
            row for row in rows if int(row["name"]) == min_name and float(row["score"]) == min_score
        )

        return [
            {"name": int(max_row["name"]), "score": float(max_row["score"])},
            {"name": int(min_row["name"]), "score": float(min_row["score"])},
        ]

    def bfs(self, start_node: int, target_node: int) -> dict:
        if start_node == target_node:
            return {"path": [start_node], "hops": 0}

        adjacency: dict[int, list[int]] = defaultdict(list)
        with self.driver.session() as session:
            records = session.run(
                """
                MATCH (s:Location)-[:OD]->(d:Location)
                RETURN toInteger(s.name) AS s, toInteger(d.name) AS d
                """
            )
            for record in records:
                adjacency[int(record["s"])].append(int(record["d"]))

        queue: deque[int] = deque([start_node])
        visited = {start_node}
        parent: dict[int, int] = {}
        found = False

        while queue and not found:
            current = queue.popleft()
            for neighbor in adjacency.get(current, []):
                if neighbor in visited:
                    continue
                visited.add(neighbor)
                parent[neighbor] = current
                if neighbor == target_node:
                    found = True
                    break
                queue.append(neighbor)

        if not found:
            return {"path": [], "hops": None}

        path = [target_node]
        while path[-1] != start_node:
            path.append(parent[path[-1]])
        path.reverse()
        return {"path": path, "hops": len(path) - 1}

    def dijkstra(self, start_node: int, target_node: int, weight_property: str) -> dict:
        self._validate_weight_property(weight_property)

        if start_node == target_node:
            return {"path": [start_node], "total_cost": 0.0}

        adjacency: dict[int, list[tuple[int, float]]] = defaultdict(list)
        with self.driver.session() as session:
            records = session.run(
                """
                MATCH (s:Location)-[r:OD]->(d:Location)
                RETURN toInteger(s.name) AS s,
                       toInteger(d.name) AS d,
                       toFloat(r.avg_distance) AS avg_distance,
                       toFloat(r.avg_fare) AS avg_fare,
                       toFloat(r.trip_count) AS trip_count
                """
            )
            for record in records:
                source = int(record["s"])
                target = int(record["d"])
                weight = float(record[weight_property])
                adjacency[source].append((target, weight))

        heap: list[tuple[float, int]] = [(0.0, start_node)]
        best_cost: dict[int, float] = {start_node: 0.0}
        parent: dict[int, int] = {}
        settled: set[int] = set()

        while heap:
            current_cost, current_node = heapq.heappop(heap)
            if current_node in settled:
                continue
            settled.add(current_node)

            if current_node == target_node:
                break

            for neighbor, edge_weight in adjacency.get(current_node, []):
                if neighbor in settled:
                    continue
                new_cost = current_cost + edge_weight
                if new_cost < best_cost.get(neighbor, float("inf")):
                    best_cost[neighbor] = new_cost
                    parent[neighbor] = current_node
                    heapq.heappush(heap, (new_cost, neighbor))

        if target_node not in best_cost:
            return {"path": [], "total_cost": None}

        path = [target_node]
        while path[-1] != start_node:
            path.append(parent[path[-1]])
        path.reverse()

        return {"path": path, "total_cost": float(best_cost[target_node])}
