# This file is to provide the implementations of each search alg
import map_generator
import heapq
import networkx as nx
import matplotlib.pyplot as plt
import math

# implementation of dijkstra's alg
def dijkstra(G, start, target):
    # initalize dictionary to store shortest distances from source node
    shortest_distances = {}
    for node in G.nodes:
        shortest_distances[node] = float('inf')
    shortest_distances[start] = 0 # set the source distance to zero

    # create dictionary of previous nodes (for reconstruction)
    previous_nodes = {}
    for node in G.nodes:
        previous_nodes[node] = None
    
    # create a set of visited nodes
    visited = set()

    # create a priority queue to get the next node to explore
    priority_queue = []
    heapq.heappush(priority_queue, (0,start)) # adds start node with distance 0

    while priority_queue:
        # extract the lowest distance node in the queue
        currDistance, currNode = heapq.heappop(priority_queue)
        if currNode in visited:
            continue
        else:
            visited.add(currNode)
    
        if currNode == target:
            break
        for neighbor, edgeDict in G[currNode].items():
            for key, edgeAttributes in edgeDict.items():
                weight = edgeAttributes.get('length')
                #print(f"Weight is: {weight} for node {currNode}")
                distance = currDistance + weight

                if distance < shortest_distances[neighbor]:
                    shortest_distances[neighbor] = distance
                    previous_nodes[neighbor] = currNode
                    heapq.heappush(priority_queue, (distance, neighbor))
            
    return shortest_distances, previous_nodes

# reconstructs the path returned by one of the algs
def reconstruct_path(previous_nodes, source, target):
    path = []
    current_node = target
    while current_node is not None:
        path.append(current_node)
        if current_node == source:
            break
        current_node = previous_nodes.get(current_node)
        if current_node is None:
            return None 
    # makes the path go from start to target
    path.reverse()
    return path

# How to test Dijkstras
"""
Start by selecting a subgraph and ensuring testable edges exist
subgraph = G.subgraph(list(G.nodes)[15:20])

List all edges so you can see the weights and which nodes they connect
print("Edges and their properties in the subgraph:")
for u, v, attributes in subgraph.edges(data=True):
    print(f"Edge from {u} to {v}")
    for key, value in attributes.items():
        print(f"  {key}: {value}")
    print()

choose two nodes connected by more than one intermediate vertex
source = 84714952
target = 84714903

plot the graph
nx.draw(subgraph, with_labels=True, node_size=500)
plt.show()

run dijkstras and it will return path and value
distances, previous = dijkstra(subgraph, source, target)
print("Distance:", distances[target])
endPath = reconstruct_path(previous, source, target)
print(f"Path: {endPath}")

ensure it matches with the output from the edge data
"""

G = map_generator.load_map("maps/final_graph.graphml")

# Heuristic function to estimate cost in a_star (straight-line distance)
def heuristic(G, node, target):
    x1, y1 = G.nodes[node]['x'], G.nodes[node]['y']
    x2, y2 = G.nodes[target]['x'], G.nodes[target]['y']
    return math.sqrt((x2 - x1)**2 + (y2 - y1)**2)

def a_star(G, start, target):
    # initalize dictionary to store shortest distances from source node
    shortest_distances = {node: float('inf') for node in G.nodes}
    shortest_distances[start] = 0

    # create dictionary of previous nodes (for reconstruction)
    previous_nodes = {node: None for node in G.nodes}

    # create visited set
    visited = set()

    # create priority queue for exploring neighboring nodes
    priority_queue = []
    heapq.heappush(priority_queue, (0, start))  # adds starts node as 0 for the source

    while priority_queue:
        # extract node w/ lowest total distance
        current_distance, current_node = heapq.heappop(priority_queue)

        if current_node in visited:
            continue
        visited.add(current_node)

        # stop if the target node is reached
        if current_node == target:
            break

        # explore neighbors
        for neighbor, edgeDict in G[current_node].items():
            for key, edgeAttributes in edgeDict.items():
                weight = edgeAttributes.get('length', float('inf'))
                weighted_distance = shortest_distances[current_node] + weight

                # calculate heuristic & total distance for priority queue
                heuristic_distance = heuristic(G, neighbor, target)
                total_distance = weighted_distance + heuristic_distance

                # determine if replacement is necessary
                if weighted_distance < shortest_distances[neighbor]:
                    shortest_distances[neighbor] = weighted_distance
                    previous_nodes[neighbor] = current_node
                    heapq.heappush(priority_queue, (total_distance, neighbor))

    return shortest_distances, previous_nodes

# # Example usage:
# """
# distances, previous_nodes = a_star(G, source, target)
# path = reconstruct_path(previous_nodes, source, target)
# print("A* Shortest Path:", path)
# print("A* Distance:", distances[target])
# """