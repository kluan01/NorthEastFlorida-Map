# Northeast Florida Shortest Path Finder
A web-based application to visualize and compare shortest paths in road networks using Dijkstra's and A* algorithms. The project processes road network data from OpenStreetMap and provides a dynamic, interactive interface.

## Features
- Downloads and processes road network graphs for multiple counties using OSMnx.
- Implements and compares Dijkstra's and A* algorithms for shortest path computation.
- Visualizes road networks and computed shortest paths with detailed metrics.
- Dynamic loading indicators and fun fact messages to improve user experience.

## Requirements
To run this project, you need the following installed on your system:
- **Python**:
  - Version 3.10 or later.
  - Python dependencies are listed in `requirements.txt`.
- **Node.js**:
  - Latest stable version recommended.
  - Includes npm (Node Package Manager) for managing frontend dependencies.

## How to Run
1. Clone the repository
2. Ensure python is installed onto your device or utilize a virtual environment
3. Run the executable script  
 `chmod +x setup.sh`<br>`./setup.sh`  
5. Open the web page at http://localhost:3000 and click "Generate!" to start the process.
