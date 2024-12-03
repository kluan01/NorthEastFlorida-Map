# This file will contain functions to get the time and previous nodes in finding shortest paths
import shortest_paths
import map_generator
import time
import networkx as nx
import osmnx as ox
import random

G = map_generator.load_map("maps/final_graph.graphml")

def is_valid_path(G, path):
    # Check if all nodes in the path exist in the graph
    for node in path:
        if node not in G.nodes:
            return False, f"Node {node} does not exist in the graph."

    # Check if edges between consecutive nodes exist
    for i in range(len(path) - 1):
        u, v = path[i], path[i + 1]
        if not G.has_edge(u, v):
            return False, f"No edge exists between {u} and {v}."

    return True, "Path is valid."


def time_dijkstras(G, start, target):
    start_time = time.time()
    shortest_distances, previous_nodes = shortest_paths.dijkstra(G, start, target)
    end_time = time.time()

    time_taken = end_time - start_time

    if shortest_distances[target] == float('inf'):
        print("No path between the two nodes exists!")
        return time_taken, None, None
    total_distance = shortest_distances[target]
    final_path = shortest_paths.reconstruct_path(previous_nodes, start, target)

    return time_taken, total_distance, final_path

    """
    validity, message = is_valid_path(G, path)
    print(f"Is the path valid: {is_it}")
    """
def time_a_star(G, start, target):
    start_time = time.time()
    shortest_distances, previous_nodes = shortest_paths.a_star(G, start, target)
    end_time = time.time()

    time_taken = end_time - start_time

    if shortest_distances[target] == float('inf'):
        print("No path between the two nodes exists!")
        return time_taken, None, None
    total_distance = shortest_distances[target]
    final_path = shortest_paths.reconstruct_path(previous_nodes, start, target)

    return time_taken, total_distance, final_path

    """
    validity, message = is_valid_path(G, path)
    print(f"Is the path valid: {is_it}")
    """

# create random nodes
nodes = list(G.nodes)
start, target = random.sample(nodes, 2)

# Testing Dijkstras Alg
print(f"From node {start} to node {target}")
print(f"Path exists: {nx.has_path(G, start, target)}")

total_time, total_distance, final_path = time_dijkstras(G,start, target)
if total_distance != None and total_time != None:
    print(f"Dijkstras alg took {total_time:.2f} seconds to run")
    print(f"The shortest path is {total_distance:.2f} meters long")
    # Visualize the path
    if final_path:
        fig, ax = ox.plot_graph_route(G, final_path, route_color="blue", node_size=10)
        print(f"Visualized Dijkstra's path from {start} to {target}.")

# Testing A* Alg
print(f"From node {start} to node {target}")
print(f"Path exists: {nx.has_path(G, start, target)}")

total_time, total_distance, final_path = time_a_star(G,start, target)
if total_distance != None and total_time != None:
    print(f"A* alg took {total_time:.2f} seconds to run")
    print(f"The shortest path is {total_distance:.2f} meters long")
    # Visualize the path
    if final_path:
        fig, ax = ox.plot_graph_route(G, final_path, route_color="green", node_size=10)
        print(f"Visualized A* path from {start} to {target}.")

# IMPORTANT FOR TESTING NOTES:
# To continue seeing visualations of graphs - you must exit out of generated Figure Map before moving onto testing.