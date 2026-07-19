# Integration tests on the real baked Gainesville graph. Skipped when the
# data file hasn't been built yet.
import gzip
import json
import pathlib
import random
import pytest
import shortest_paths

from graph_shim import AtlasGraph

DATA = pathlib.Path(__file__).resolve().parent.parent / "web" / "data" / "gainesville.json.gz"

pytestmark = pytest.mark.skipif(not DATA.exists(), reason="run tools/build_graph.py first")


@pytest.fixture(scope="module")
def G():
    with gzip.open(DATA, "rt", encoding="utf-8") as f:
        return AtlasGraph(json.load(f))


@pytest.fixture(scope="module")
def pairs(G):
    rng = random.Random(42)
    node_count = len(G.nodes)
    return [tuple(rng.sample(range(node_count), 2)) for _ in range(5)]


def test_both_algorithms_agree_on_distance(G, pairs):
    for start, target in pairs:
        d_dist, d_prev, d_order = shortest_paths.dijkstra(G, start, target)
        a_dist, a_prev, a_order = shortest_paths.a_star(G, start, target)
        assert d_dist[target] != float("inf"), "SCC trim should guarantee reachability"
        assert a_dist[target] == pytest.approx(d_dist[target], rel=1e-9)


def test_a_star_explores_no_more_than_dijkstra(G, pairs):
    for start, target in pairs:
        _, _, d_order = shortest_paths.dijkstra(G, start, target)
        _, _, a_order = shortest_paths.a_star(G, start, target)
        # consistent heuristic => A* settles a subset of Dijkstra's nodes
        # (small tolerance for tie-breaking)
        assert len(a_order) <= len(d_order) * 1.05


def test_heuristic_admissible_on_real_graph(G, pairs):
    for start, target in pairs:
        d_dist, _, _ = shortest_paths.dijkstra(G, start, target)
        assert shortest_paths.heuristic(G, start, target) <= d_dist[target] + 1e-6


def test_paths_follow_real_edges(G, pairs):
    for start, target in pairs:
        _, previous, _ = shortest_paths.dijkstra(G, start, target)
        path = shortest_paths.reconstruct_path(previous, start, target)
        assert path[0] == start and path[-1] == target
        for u, v in zip(path, path[1:]):
            assert v in G[u], f"no edge {u}->{v}"
