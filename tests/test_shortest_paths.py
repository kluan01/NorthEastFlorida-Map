# Tests for the hand-written Dijkstra and A* implementations.
import pytest
import shortest_paths

class FakeGraph:
    """Minimal stand-in for the MultiDiGraph interface the algorithms use."""

    def __init__(self):
        self.nodes = {}
        self._adj = {}

    def add_node(self, node, x, y):
        self.nodes[node] = {"x": x, "y": y}
        self._adj[node] = {}

    def add_edge(self, u, v, length):
        edge_dict = self._adj[u].setdefault(v, {})
        edge_dict[len(edge_dict)] = {"length": length}

    def __getitem__(self, node):
        return self._adj[node]


@pytest.fixture
def diamond():
    # Directed diamond in real Gainesville-ish coordinates (x=lng, y=lat).
    # A -> B -> D costs 300; A -> C -> D costs 280 (the better route).
    # Every edge length exceeds the straight-line distance between its
    # endpoints, so a correct (haversine) heuristic must stay admissible.
    g = FakeGraph()
    g.add_node("A", -82.3500, 29.6500)
    g.add_node("B", -82.3492, 29.6510)
    g.add_node("C", -82.3492, 29.6490)
    g.add_node("D", -82.3484, 29.6500)
    g.add_edge("A", "B", 150)
    g.add_edge("B", "D", 150)
    g.add_edge("A", "C", 140)
    g.add_edge("C", "D", 140)
    return g


def test_dijkstra_finds_shortest_distance_and_path(diamond):
    distances, previous, visited_order = shortest_paths.dijkstra(diamond, "A", "D")
    assert distances["D"] == 280
    assert shortest_paths.reconstruct_path(previous, "A", "D") == ["A", "C", "D"]


def test_a_star_matches_dijkstra(diamond):
    d_dist, _, _ = shortest_paths.dijkstra(diamond, "A", "D")
    a_dist, previous, _ = shortest_paths.a_star(diamond, "A", "D")
    assert a_dist["D"] == d_dist["D"] == 280
    assert shortest_paths.reconstruct_path(previous, "A", "D") == ["A", "C", "D"]


def test_heuristic_returns_meters():
    # 0.01 degrees of latitude is ~1,112 m anywhere on Earth. The pre-fix
    # implementation returned 0.01 (degrees) here — off by five orders of
    # magnitude.
    g = FakeGraph()
    g.add_node("A", -82.35, 29.65)
    g.add_node("B", -82.35, 29.66)
    assert shortest_paths.heuristic(g, "A", "B") == pytest.approx(1112, abs=3)


def test_heuristic_is_admissible(diamond):
    distances, _, _ = shortest_paths.dijkstra(diamond, "A", "D")
    assert shortest_paths.heuristic(diamond, "A", "D") <= distances["D"]


def test_visited_order_runs_from_start_to_target(diamond):
    for algorithm in (shortest_paths.dijkstra, shortest_paths.a_star):
        _, _, visited_order = algorithm(diamond, "A", "D")
        assert visited_order[0] == "A"
        assert visited_order[-1] == "D"
        assert len(visited_order) == len(set(visited_order))


def test_parallel_edges_use_the_shorter():
    g = FakeGraph()
    g.add_node("A", -82.3500, 29.6500)
    g.add_node("B", -82.3499, 29.6500)
    g.add_edge("A", "B", 50)
    g.add_edge("A", "B", 30)
    distances, _, _ = shortest_paths.dijkstra(g, "A", "B")
    assert distances["B"] == 30


def test_unreachable_target_reports_infinity():
    g = FakeGraph()
    g.add_node("A", -82.3500, 29.6500)
    g.add_node("B", -82.3499, 29.6500)
    distances, previous, _ = shortest_paths.dijkstra(g, "A", "B")
    assert distances["B"] == float("inf")
    assert shortest_paths.reconstruct_path(previous, "A", "B") is None
