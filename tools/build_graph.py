# Bakes the runtime map data for the Gainesville Pathfinding Atlas.
#
# Run once (or whenever the map should refresh):
#   venv/bin/python tools/build_graph.py
#
# Produces:
#   web/data/gainesville.json.gz  — nodes, edges, and road geometry
import gzip
import json
import pathlib

import networkx as nx
import osmnx as ox

ROOT = pathlib.Path(__file__).resolve().parent.parent
DATA_OUT = ROOT / "web" / "data" / "gainesville.json.gz"

PLACES = [
    "Gainesville, Florida, USA",
    "University of Florida, Gainesville, Florida, USA",
]
GEOMETRY_TOLERANCE = 0.00002  # ~2 m; shaves file size, invisible at street zoom


def _sq_dist(a, b):
    return (a[0] - b[0]) ** 2 + (a[1] - b[1]) ** 2


def build():
    print(f"Downloading drive network for {PLACES}...")
    G = ox.graph_from_place(PLACES, network_type="drive")
    print(f"Downloaded: {len(G.nodes)} nodes, {len(G.edges)} edges")

    # keep only the largest strongly-connected component so any two clicked
    # intersections are always mutually reachable at runtime
    largest = max(nx.strongly_connected_components(G), key=len)
    G = G.subgraph(largest).copy()
    print(f"Largest strongly-connected component: {len(G.nodes)} nodes")

    ids = {osmid: index for index, osmid in enumerate(G.nodes)}
    nodes = [
        [round(G.nodes[osmid]["y"], 6), round(G.nodes[osmid]["x"], 6)]
        for osmid in G.nodes
    ]

    edges = []
    for u, v, data in G.edges(data=True):
        u_point = nodes[ids[u]]
        geometry = data.get("geometry")
        if geometry is not None:
            simplified = geometry.simplify(GEOMETRY_TOLERANCE)
            points = [[round(lat, 6), round(lng, 6)] for lng, lat in simplified.coords]

            # geometry must run u -> v for route stitching; flip if needed
            if _sq_dist(points[0], u_point) > _sq_dist(points[-1], u_point):
                points.reverse()
        else:
            points = [u_point, nodes[ids[v]]]
        edges.append([ids[u], ids[v], round(data["length"]), points])

    lats = [lat for lat, _ in nodes]
    lngs = [lng for _, lng in nodes]
    payload = {
        "meta": {
            "name": "Gainesville, FL + University of Florida",
            "nodeCount": len(nodes),
            "edgeCount": len(edges),
            "bbox": [min(lats), min(lngs), max(lats), max(lngs)],
        },
        "nodes": nodes,
        "edges": edges,
    }

    DATA_OUT.parent.mkdir(parents=True, exist_ok=True)
    with gzip.open(DATA_OUT, "wt", encoding="utf-8", compresslevel=9) as f:
        json.dump(payload, f, separators=(",", ":"))

    size_mb = DATA_OUT.stat().st_size / 1_000_000
    print(f"Wrote {DATA_OUT} ({size_mb:.1f} MB gzipped)")


if __name__ == "__main__":
    build()
