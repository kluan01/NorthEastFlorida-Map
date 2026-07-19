// Web worker: boots Pyodide, loads the hand-written Python algorithms and the
// Gainesville graph, and runs races off the main thread.
const PYODIDE_BASE = "https://cdn.jsdelivr.net/pyodide/v0.26.4/full/";

let pyodide = null;

self.onmessage = (event) => {
  const msg = event.data;
  if (msg.type === "init") init(msg.baseUrl).catch((err) => fail("init", err));
  else if (msg.type === "race") race(msg.startId, msg.endId, msg.generation).catch((err) => fail("race", err, msg.generation));
};

function post(message, transfer) { self.postMessage(message, transfer || []); }
function fail(stage, err, generation) {
  post({ type: "error", stage, generation, message: String((err && err.message) || err) });
}

async function fetchWithRetry(url) {
  for (let attempt = 0; attempt < 2; attempt++) {
    try {
      const resp = await fetch(url);
      if (!resp.ok) throw new Error(`HTTP ${resp.status} for ${url}`);
      return resp;
    } catch (err) {
      if (attempt === 1) throw err;
    }
  }
}

function pyList(expression) {
  const proxy = pyodide.runPython(expression);
  const arr = proxy.toJs({ create_proxies: false });
  proxy.destroy();
  return arr;
}

async function init(baseUrl) {
  post({ type: "progress", stage: "pyodide", message: "Waking the Python interpreter (first visit only takes a moment)…" });
  importScripts(PYODIDE_BASE + "pyodide.js");
  pyodide = await loadPyodide({ indexURL: PYODIDE_BASE });

  post({ type: "progress", stage: "python", message: "Unpacking the survey instruments…" });
  const [algoResp, shimResp] = await Promise.all([
    fetchWithRetry(baseUrl + "py/shortest_paths.py"),
    fetchWithRetry(baseUrl + "py/graph_shim.py"),
  ]);
  pyodide.FS.writeFile("shortest_paths.py", await algoResp.text());
  pyodide.FS.writeFile("graph_shim.py", await shimResp.text());

  post({ type: "progress", stage: "data", message: "Unrolling the Gainesville charts…" });
  const dataResp = await fetchWithRetry(baseUrl + "data/gainesville.json.gz");
  const stream = dataResp.body.pipeThrough(new DecompressionStream("gzip"));
  const rawJson = await new Response(stream).text();

  post({ type: "progress", stage: "graph", message: "Charting the intersections…" });
  pyodide.globals.set("RAW_JSON", rawJson);
  pyodide.runPython([
    "import json",
    "import shortest_paths",
    "from graph_shim import AtlasGraph",
    "G = AtlasGraph(json.loads(RAW_JSON))",
  ].join("\n"));
  pyodide.globals.delete("RAW_JSON");

  const nodes = new Float64Array(pyList("G.flat_node_coords()"));
  const segments = new Float32Array(pyList("G.flat_draw_segments()"));
  const bbox = pyList("G.bbox()");
  const nodeCount = pyodide.runPython("len(G.nodes)");
  const edgeCount = pyodide.runPython("G.meta.get('edgeCount', 0)");

  post(
    { type: "ready", nodeCount, edgeCount, bbox, nodes, segments },
    [nodes.buffer, segments.buffer],
  );
}

async function race(startId, endId, generation) {
  pyodide.globals.set("START_ID", startId);
  pyodide.globals.set("END_ID", endId);
  const raw = pyodide.runPython(`
    import json, time

    _results = {}
    for _name, _fn in (("dijkstra", shortest_paths.dijkstra), ("aStar", shortest_paths.a_star)):
        _t0 = time.perf_counter()
        _distances, _previous, _visited_order = _fn(G, START_ID, END_ID)
        _elapsed_ms = (time.perf_counter() - _t0) * 1000.0
        _path = shortest_paths.reconstruct_path(_previous, START_ID, END_ID)
        _reachable = _distances[END_ID] != float("inf") and _path is not None
        _results[_name] = {
            "distance": _distances[END_ID] if _reachable else None,
            "timeMs": _elapsed_ms,
            "nodesExplored": len(_visited_order),
            "visitedOrder": _visited_order,
            "path": _path if _reachable else [],
        }

    _route = []
    if _results["aStar"]["path"]:
        for _lat, _lng in G.route_geometry(_results["aStar"]["path"]):
            _route.append(_lat)
            _route.append(_lng)
    _results["routeLine"] = _route

    json.dumps(_results)
    `);

  const parsed = JSON.parse(raw);
  const pack = (algo) => ({
    distance: algo.distance,
    timeMs: algo.timeMs,
    nodesExplored: algo.nodesExplored,
    visitedOrder: new Int32Array(algo.visitedOrder),
    path: new Int32Array(algo.path),
  });

  const result = {
    dijkstra: pack(parsed.dijkstra),
    aStar: pack(parsed.aStar),
    routeLine: new Float64Array(parsed.routeLine),
  };

  post({ type: "result", race: result, generation }, [
    result.dijkstra.visitedOrder.buffer, result.dijkstra.path.buffer,
    result.aStar.visitedOrder.buffer, result.aStar.path.buffer,
    result.routeLine.buffer,
  ]);
}
