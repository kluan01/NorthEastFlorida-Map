import osmnx as ox
import matplotlib.pyplot as plt
import networkx as nx

# location name

"""
bbox = {29.5, 29.0, -81.0, -82.0}
G = ox.graph_from_bbox(bbox, network_type="drive")

print(f"Nodes: {len(G.nodes)}, Edges: {len(G.edges)}")
"""

"""
bounding_boxes = [
    (29.5, 29.0, -81.0, -82.0),  # Box 1
    (29.5, 29.0, -80.5, -81.0),  # Box 2
    (29.5, 29.0, -80.0, -80.5),  # Box 3
    (29.0, 28.5, -81.0, -82.0),  # Box 4
    (29.0, 28.5, -80.5, -81.0),  # Box 5
    (29.0, 28.5, -80.0, -80.5),  # Box 6
    (28.5, 28.0, -81.0, -82.0),  # Box 7
    (28.5, 28.0, -80.5, -81.0),  # Box 8
    (28.5, 28.0, -80.0, -80.5),  # Box 9
]

G_combined = nx.MultiDiGraph()

for bbox in bounding_boxes:
    G = ox.graph_from_bbox(bbox, network_type="drive")
    G_combined = nx.compose(G_combined, G)  # Merge graphs

"""

location1 = "Alachua County, Florida, USA"
location2 = "Ocala, Florida, USA"

G1 = ox.graph_from_place(location1, network_type="drive")
G2 = ox.graph_from_place(location2, network_type="drive")

G = nx.compose(G1, G2)
fig, ax = ox.plot_graph(G, node_size=10, edge_linewidth=0.5)
plt.show()


# print(f"Nodes: {len(G_combined.nodes)}, Edges: {len(G.edges)}")

