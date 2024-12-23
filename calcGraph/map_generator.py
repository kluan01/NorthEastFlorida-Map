import osmnx as ox
import matplotlib.pyplot as plt
import networkx as nx
import os

def save_map_location(location, filepath):
    # Downloads a road network graph for a specified location and saves it as a GraphML file.
    # If the file already exists, the function skips the download process.

    # if os.path.exists(filepath): # <-- debugging purposes
    #     print("Graph with filepath already exists")
    # else:
    if not os.path.exists(filepath):
        print(f"Downloading {location} graph...")
        G = ox.graph_from_place(location, network_type="drive")
        ox.save_graphml(G, filepath=filepath)
        print(f"Graph successfully downloaded")

def save_generated_map(G, filepath):
    # Saves a pre-generated graph to a specified GraphML file.
    # Checks if the file already exists to prevent overwriting.
    # Returns True if the graph is saved, False if the file already exists.

    # if os.path.exists(filepath):  # <-- debugging purposes
    #     print("Graph with filepath already exists")
    #     return False
    # else:
    if not os.path.exists(filepath):
        print(f"Saving graph to {filepath}...")
        ox.save_graphml(G, filepath=filepath)
        print(f"Graph successfully saved")
        return True

def load_map(filepath:str) -> nx.MultiDiGraph:
    # Loads a road network graph from a GraphML file.
    # If the file does not exist, raises a FileNotFoundError.
    # If there is an issue loading the graph, raises a ValueError.
    if os.path.exists(filepath):
        #print("Loading downloaded graph")  # <-- debugging purposes
        try:
            G = ox.load_graphml(filepath)
            return G
        except Exception as e:
            raise ValueError(f"Failed to load graph from {filepath}: {e}")
    else:
        raise FileNotFoundError(f"Filepath does not exist: {filepath}")

def show_map(G, node_size = 10, edge_linewidth=0.5):
    # Visualizes a road network graph using Matplotlib and OSMnx.
    # Accepts optional parameters for node size and edge line width.

    fig, ax = ox.plot_graph(G, node_size=node_size, edge_linewidth=edge_linewidth)
    plt.show()  

def download_final_map(finalPath):
    # Downloads and saves road network graphs for multiple locations.
    # Combines the graphs into a single graph and saves it to a specified file path.

    location1 = "Alachua County, Florida, USA"
    filepath1 = "maps/alachua_county.graphml"

    location2 = "Marion County, Florida, USA"
    filepath2 = "maps/marion_county.graphml"

    location3 = "Levy County, Florida, USA"
    filepath3 = "maps/levy_county.graphml"

    location4 = "Putnam County, Florida, USA"
    filepath4 = "maps/putnam_county.graphml"

    location5 = "Clay County, Florida, USA"
    filepath5 = "maps/clay_county.graphml"

    location6 = "Bradford County, Florida, USA"
    filepath6 = "maps/bradford_county.graphml"

    location7 = "Union County, Florida, USA"
    filepath7 = "maps/union_county.graphml"

    location8 = "Gilchrist County, Florida, USA"
    filepath8 = "maps/gilchrist_county.graphml"

    save_map_location(location1, filepath1)
    save_map_location(location2, filepath2)
    save_map_location(location3, filepath3)
    save_map_location(location4, filepath4)
    save_map_location(location5, filepath5)
    save_map_location(location6, filepath6)
    save_map_location(location7, filepath7)
    save_map_location(location8, filepath8)

    G_alacua = load_map(filepath1)
    G_marion = load_map(filepath2)
    G_levy = load_map(filepath3)
    G_putnam = load_map(filepath4)
    G_clay = load_map(filepath5)
    G_bradford = load_map(filepath6)
    G_union = load_map(filepath7)
    G_gilchrist = load_map(filepath8)

    Gfirst = nx.compose(G_alacua, G_marion)
    Gsecond = nx.compose(G_levy, G_putnam)

    Gfourth = nx.compose(G_clay, G_bradford)
    Gthird = nx.compose(G_union, G_gilchrist)

    GfirstCom = nx.compose(Gfirst, Gsecond)
    GsecondCom = nx.compose(Gthird, Gfourth)

    Gfinal = nx.compose(GfirstCom, GsecondCom)

    save_generated_map(Gfinal, finalPath)

def get_map_stats(G):
    # Prints the number of nodes and edges in the given graph.
    # Useful for analyzing the size and structure of the graph.
    print(f"Nodes: {len(G.nodes)}, Edges: {len(G.edges)}")

# generates map for new users
def generate_map():
    if os.path.exists("maps/FinalGraph.graphml"):
        print("Successful map generation!\n")
        return
    else:
        print("Generating map...")
        download_final_map("maps/FinalGraph.graphml")
        G = load_map("maps/FinalGraph.graphml")
        if (load_map):
            print("Successful map generation!\n")
