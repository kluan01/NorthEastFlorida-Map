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

    # the website animates the search frontier and needs the exact sequence.
    visited_order = []

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
            visited_order.append(currNode)
    
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
            
    return shortest_distances, previous_nodes, visited_order

def heuristic(G, node, target):
    x1, y1 = G.nodes[node]['x'], G.nodes[node]['y']
    x2, y2 = G.nodes[target]['x'], G.nodes[target]['y']

    # convert the degree coordinates to radians
    lon1, lat1, lon2, lat2 = map(math.radians, (x1, y1, x2, y2))

    # haversine formula: straight-line distance over the Earth's surface
    a = math.sin((lat2 - lat1) / 2)**2 + math.cos(lat1) * math.cos(lat2) * math.sin((lon2 - lon1) / 2)**2
    return 2 * 6371000 * math.asin(math.sqrt(a)) # 6,371,000 m = Earth radius

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
    visited_order = []

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
            visited_order.append(currNode)
    
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
            
    return shortest_distances, previous_nodes, visited_order
