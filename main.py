# from graphStuff import map_generator, graph_times <-- console version

# def main():
#     map_generator.generate_map()
#     graph_times.test_algorithms()

# if __name__ == "__main__":
#     main()

from flask import Flask, jsonify, send_file
from calcGraph import map_generator, graph_times
from flask_cors import CORS
import os

app = Flask(__name__)
CORS(app)

@app.route("/api/run-functions", methods=["POST"])
def run_functions():
    try:
        map_generator.generate_map()
        results = graph_times.test_algorithms()
        return jsonify(results), 200
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@app.route("/api/route-image", methods=["GET"])
def get_route_image():
    image_path = "static/route.png"
    if os.path.exists(image_path):
        return send_file(image_path, mimetype='image/png')
    return jsonify({"error": "Route image not found"}), 404

if __name__ == "__main__":
    app.run(debug=True)
