# The Gainesville Atlas

**Dijkstra** and **A\*** written from scratch in Python, racing
side by side on a map of Gainesville, Florida. The Python is not a backend:
it runs **inside your browser** via [Pyodide](https://pyodide.org) (CPython
compiled to WebAssembly). The site is 100% static.

## Run it locally

```bash
python3 -m http.server 8080 --directory web
# open http://localhost:8080
```

> _macOS/Linux shell syntax. On Windows, use `python` (or `py -3`) instead of `python3`._

No build step, no backend. First load fetches the Pyodide runtime from the jsDelivr CDN, ~7 MB, cached by the browser afterward.

> _If you deploy behind a host that serves `.gz` files with `Content-Encoding: gzip` (some CDNs), rename the data file to end in `.json.bin` or disable that behavior — the app decompresses it itself._

## Repo tour

```
NorthEastFlorida-Map/
│
├── tools/
│   └── build_graph.py            bakes web/data/gainesville.json.gz
│                                  from OpenStreetMap via OSMnx
│
├── web/                          static site (Leaflet + Pyodide worker)
│   └── py/
│       ├── shortest_paths.py     ★ hand-written Dijkstra & A*
│       └── graph_shim.py         browser stand-in for the graph object
│
├── tests/                        pytest suite
│   ├── __init__.py
│   ├── conftest.py
│   ├── test_graph_shim.py
│   ├── test_real_graph.py
│   └── test_shortest_paths.py
│
├── .gitignore
├── LICENSE
├── README.md
└── requirements.txt
```

## Rebuild the map data (maintainers only)

`web/data/gainesville.json.gz` already ships with the repo, so this is **not**
needed to run the site.
<br> The code below only exists to change the source data for the following reasons:

- cover a different area
- refresh the OSM snapshot

It also needs internet access (queries OpenStreetMap/OSMnx live) and a heavier Python environment than the rest of the project.

```bash
python3 -m venv venv && venv/bin/pip install -r requirements.txt
venv/bin/python tools/build_graph.py
venv/bin/python -m pytest tests/
```

> _macOS/Linux shell syntax. On Windows: `python` instead of `python3`, and
> `venv\Scripts\` instead of `venv/bin/`._

## Credits & license

By Kaden Luangsouphom & Devan Parekh, released under the [MIT License](LICENSE).
Map data © [OpenStreetMap](https://www.openstreetmap.org/copyright) contributors
(ODbL). Bundled [Leaflet](https://leafletjs.com) is BSD-2-licensed by its authors.
