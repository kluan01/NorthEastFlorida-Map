# Loads the pre-baked Gainesville graph and exposes it through the same
# interface networkx's MultiDiGraph gave the hand-written algorithms:
#
#   G.nodes    -> dict of node id -> {'x': longitude, 'y': latitude}
#   G[node]    -> {neighbor: {edge_key: {'length': meters}}}
#
# This lets shortest_paths.py run in the browser byte-for-byte
# unchanged, without shipping networkx itself.


class AtlasGraph:
    def __init__(self, data):
        self.meta = data.get("meta", {})
        self.nodes = {}
        self._adj = {}
        self._geom = {}  # (u, v) -> (length, [[lat, lng], ...]) of shortest parallel edge

        for index, (lat, lng) in enumerate(data["nodes"]):
            self.nodes[index] = {"x": lng, "y": lat}
            self._adj[index] = {}

        for u, v, length, geometry in data["edges"]:
            edge_dict = self._adj[u].setdefault(v, {})
            edge_dict[len(edge_dict)] = {"length": length}
            best = self._geom.get((u, v))
            if best is None or length < best[0]:
                self._geom[(u, v)] = (length, geometry)

    def __getitem__(self, node):
        return self._adj[node]

    def bbox(self):
        # [south, west, north, east] over every node coordinate
        lats = [attrs["y"] for attrs in self.nodes.values()]
        lngs = [attrs["x"] for attrs in self.nodes.values()]
        return [min(lats), min(lngs), max(lats), max(lngs)]

    def flat_node_coords(self):
        # [lat0, lng0, lat1, lng1, ...] — fast transfer to JavaScript
        out = []
        for index in range(len(self.nodes)):
            attrs = self.nodes[index]
            out.append(attrs["y"])
            out.append(attrs["x"])
        return out

    def flat_draw_segments(self):
        # every road geometry flattened into straight segments:
        # [aLat, aLng, bLat, bLng, ...] — used only to draw the base map
        out = []
        for length, geometry in self._geom.values():
            for (a_lat, a_lng), (b_lat, b_lng) in zip(geometry, geometry[1:]):
                out.extend((a_lat, a_lng, b_lat, b_lng))
        return out

    def route_geometry(self, path):
        # stitches per-edge road geometry into one polyline for a full path
        points = []
        for u, v in zip(path, path[1:]):
            segment = self._geom[(u, v)][1]
            if points:
                segment = segment[1:]  # skip the shared intersection point
            points.extend(segment)
        return points
