# This file will contain functions to get the time and previous nodes in finding shortest paths
from backend import map_generator, shortest_paths
import time
import networkx as nx
import osmnx as ox
import random

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

    # validity, message = is_valid_path(G, path) <--- debugging purposes
    # print(f"Is the path valid: {is_it}")

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

    # validity, message = is_valid_path(G, path) # <--- debugging purposes
    # print(f"Is the path valid: {is_it}")

def test_algorithms():
    # load the map
    G = map_generator.load_map("maps/FinalGraph.graphml")

    # get the largest connected components
    largest_component = max(nx.strongly_connected_components(G), key=len)
    nodes = list(largest_component)

    # create random nodes for testing
    start, target = random.sample(nodes, 2)
    print("Testing Algorithms...\n")

    # print node information
    print(f"From node {start} to node {target}")
    print(f"Path exists: {nx.has_path(G, start, target)}\n")

    # Testing A* Algorithm
    total_time, total_distance, final_path = time_a_star(G,start, target)
    if total_distance != None and total_time != None:
        print(f"A* algorithm took {total_time:.2f} seconds to run")
        print(f"The shortest path calculated is {total_distance:.2f} meters long\n")

    # Testing Dijkstra's Algorithm
    total_time, total_distance, final_path = time_dijkstras(G,start, target)
    if total_distance != None and total_time != None:
        print(f"Dijkstra's algorithm took {total_time:.2f} seconds to run")
        print(f"The shortest path calculated is {total_distance:.2f} meters long\n")

        # visualize the path for the user
        if final_path:
            print(f"Displaying map route...\n")
            fig, ax = ox.plot_graph_route(G, final_path, route_color="blue", node_size=10)
