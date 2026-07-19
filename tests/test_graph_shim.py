# Tests that the runtime shim exposes exactly the interface the hand-written
# algorithms expect, so shortest_paths.py runs on it unchanged.
import pytest
import shortest_paths

from graph_shim import AtlasGraph


@pytest.fixture
def data():
    # Same diamond as test_shortest_paths, in the baked JSON format.
    # Node ids are list indices: 0=A, 1=B, 2=C, 3=D.
    def seg(a, b):
        return [a, b]

    n = [
        [29.6500, -82.3500],  # 0: A
        [29.6510, -82.3492],  # 1: B
        [29.6490, -82.3492],  # 2: C
        [29.6500, -82.3484],  # 3: D
    ]
    return {
        "meta": {"nodeCount": 4, "edgeCount": 4},
        "nodes": n,
        "edges": [
            [0, 1, 150, seg(n[0], n[1])],
            [1, 3, 150, seg(n[1], n[3])],
            [0, 2, 140, seg(n[0], n[2])],
            [2, 3, 140, seg(n[2], n[3])],
        ],
    }


def test_nodes_interface(data):
    g = AtlasGraph(data)
    assert list(g.nodes) == [0, 1, 2, 3]          # iteration yields ids
    assert g.nodes[0] == {"x": -82.3500, "y": 29.6500}  # x=lng, y=lat


def test_adjacency_interface(data):
    g = AtlasGraph(data)
    assert g[0][1][0]["length"] == 150            # G[u][v][edge_key]['length']
    assert set(g[0].keys()) == {1, 2}


def test_parallel_edges_get_distinct_keys(data):
    data["edges"].append([0, 1, 90, [data["nodes"][0], data["nodes"][1]]])
    g = AtlasGraph(data)
    lengths = sorted(attrs["length"] for attrs in g[0][1].values())
    assert lengths == [90, 150]


def test_algorithms_run_unchanged_on_shim(data):
    g = AtlasGraph(data)
    d_dist, d_prev, _ = shortest_paths.dijkstra(g, 0, 3)
    a_dist, a_prev, _ = shortest_paths.a_star(g, 0, 3)
    assert d_dist[3] == a_dist[3] == 280
    assert shortest_paths.reconstruct_path(a_prev, 0, 3) == [0, 2, 3]


def test_route_geometry_stitches_without_duplicates(data):
    g = AtlasGraph(data)
    line = g.route_geometry([0, 2, 3])
    assert line == [data["nodes"][0], data["nodes"][2], data["nodes"][3]]


def test_flat_arrays_and_bbox(data):
    g = AtlasGraph(data)
    flat = g.flat_node_coords()
    assert flat[:2] == [29.6500, -82.3500]
    assert len(flat) == 8
    assert len(g.flat_draw_segments()) % 4 == 0
    assert g.bbox() == [29.6490, -82.3500, 29.6510, -82.3484]
