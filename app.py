from flask import Flask, render_template
import osmnx as ox
import networkx as nx
import os

app = Flask(__name__)

@app.route('/')
def index():
    # Serve the main page with node options
    return render_template('index.html')

if __name__ == '__main__':
    # Ensure templates folder exists
    os.makedirs('templates', exist_ok=True)
    app.run(debug=True)
