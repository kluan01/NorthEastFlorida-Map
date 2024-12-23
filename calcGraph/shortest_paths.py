# This file is to provide the implementations of each search algorithm
import heapq
import math

# reconstructs the path returned by the algorithms
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

# implementation of Dijkstra's algorithm
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
                distance = currDistance + weight

                if distance < shortest_distances[neighbor]:
                    shortest_distances[neighbor] = distance
                    previous_nodes[neighbor] = currNode
                    heapq.heappush(priority_queue, (distance, neighbor))
            
    return shortest_distances, previous_nodes

# heuristic function to estimate cost in A* (straight-line distance)
def heuristic(G, node, target):
    x1, y1 = G.nodes[node]['x'], G.nodes[node]['y']
    x2, y2 = G.nodes[target]['x'], G.nodes[target]['y']
    return math.sqrt((x2 - x1)**2 + (y2 - y1)**2)

# implementation of A* algorithm
def a_star(G, start, target):
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
                tentative_g = shortest_distances[currNode] + weight

                if tentative_g < shortest_distances[neighbor]:
                    shortest_distances[neighbor] = tentative_g
                    previous_nodes[neighbor] = currNode

                    f_value = tentative_g + heuristic(G, neighbor, target)
                    heapq.heappush(priority_queue, (f_value, neighbor))
            
    return shortest_distances, previous_nodes