import osmnx as ox
import matplotlib.pyplot as plt
import networkx as nx
import os

def save_map_location(location, filepath):
    # Downloads a road network graph for a specified location and saves it as a GraphML file.
    # If the file already exists, the function skips the download process.

    if os.path.exists(filepath):
        print("Graph with filepath already exists")
    else:
        print(f"Downloading {location} graph...")
        G = ox.graph_from_place(location, network_type="drive")
        ox.save_graphml(G, filepath=filepath)
        print(f"Graph successfully downloaded")

def save_generated_map(G, filepath):
    # Saves a pre-generated graph to a specified GraphML file.
    # Checks if the file already exists to prevent overwriting.
    # Returns True if the graph is saved, False if the file already exists.

    if os.path.exists(filepath):
        print("Graph with filepath already exists")
        return False
    else:
        print(f"Saving graph to {filepath}...")
        ox.save_graphml(G, filepath=filepath)
        print(f"Graph successfully saved")
        return True

def load_map(filepath:str) -> nx.MultiDiGraph:
    # Loads a road network graph from a GraphML file.
    # If the file does not exist, raises a FileNotFoundError.
    # If there is an issue loading the graph, raises a ValueError.
    if os.path.exists(filepath):
        print("Loading downloaded graph")
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

    save_map_location(location1, filepath1)
    save_map_location(location2, filepath2)
    save_map_location(location3, filepath3)
    save_map_location(location4, filepath4)

    G_alacua = load_map(filepath1)
    G_marion = load_map(filepath2)
    G_levy = load_map(filepath3)
    G_putnam = load_map(filepath4)

    Gfirst = nx.compose(G_alacua, G_marion)
    Gsecond = nx.compose(G_levy, G_putnam)
    Gfinal = nx.compose(Gfirst, Gsecond)

    save_generated_map(Gfinal, finalPath)

def get_map_stats(G):
    # Prints the number of nodes and edges in the given graph.
    # Useful for analyzing the size and structure of the graph.
    print(f"Nodes: {len(G.nodes)}, Edges: {len(G.edges)}")

"""
def main():
    # 1. Downloads and combines maps into a final graph.
    # 2. Loads the final graph, prints its statistics, and visualizes it.
    finalMapPath = "maps/final_graph.graphml"
    download_final_map(finalMapPath)
    Gfinal = load_map(finalMapPath)
    get_map_stats(Gfinal)
    show_map(Gfinal)
"""
"""
if __name__ == "__main__":
    main()
"""
