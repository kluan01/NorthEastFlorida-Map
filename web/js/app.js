// Orchestrates the atlas: worker lifecycle, controls, and page state.
// State machine: idle -> loading -> ready -> racing -> finished -> (ready)
import { initPlate, snapToNode } from "./map.js";
import { runRace } from "./animate.js";

const el = (id) => document.getElementById(id);
const ui = {
  veil: el("veil"), veilMessage: el("veil-message"), heroStatus: el("hero-status"),
  hint: el("hint"), race: el("btn-race"), reset: el("btn-reset"),
  preset: el("select-preset"), speed: el("input-speed"),
  modePlace: el("mode-place"), modePan: el("mode-pan"),
  verdict: el("verdict"),
  statTimeD: el("stat-time-d"), statTimeA: el("stat-time-a"),
  statNodesD: el("stat-nodes-d"), statNodesA: el("stat-nodes-a"),
  statDistance: el("stat-distance"), statReduction: el("stat-reduction"),
};

const atlas = { bundle: null, view: null, state: "idle", worker: null };
window.__atlas = atlas; // test/debug handle

boot();

function boot() {
  if (typeof WebAssembly === "undefined" || typeof DecompressionStream === "undefined" || !window.Worker) {
    showVeilError("This demo needs a modern browser (WebAssembly + streams). The code and story below still read fine!");
    return;
  }

  atlas.state = "loading";
  atlas.worker = new Worker("./js/worker.js");
  atlas.worker.onmessage = (event) => handleWorkerMessage(event.data);
  atlas.worker.onerror = (err) => showVeilError(`The survey crew hit a snag: ${err.message || "worker failed to start"}`);
  atlas.worker.postMessage({ type: "init", baseUrl: new URL("./", document.baseURI).href });
}

function handleWorkerMessage(msg) {
  if (msg.type === "progress") {
    ui.veilMessage.textContent = msg.message;
    ui.heroStatus.textContent = msg.message;
  } else if (msg.type === "ready") {
    onReady(msg);
  } else if (msg.type === "result") {
    onRaceResult(msg.race, msg.generation);
  } else if (msg.type === "error") {
    if (msg.stage === "race") {
      if (msg.generation !== raceGeneration) return; // superseded race — Reset or a newer race moved on
      // A failed race shouldn't take down the whole app — recover and let the user retry.
      ui.hint.textContent = "Something went wrong running that race — try different points.";
      atlas.state = "ready";
      ui.race.disabled = false;
      ui.preset.disabled = false;
    } else {
      showVeilError(`Could not load the atlas: ${msg.message}`);
    }
  }
}

function onReady(msg) {
  atlas.bundle = { nodes: msg.nodes, segments: msg.segments, bbox: msg.bbox,
                   nodeCount: msg.nodeCount, edgeCount: msg.edgeCount };

  ui.heroStatus.textContent = `${msg.nodeCount.toLocaleString()} intersections charted · ${msg.edgeCount.toLocaleString()} road segments`;
  ui.veil.classList.add("veil-hidden");
  ui.hint.textContent = "Click (or tap) a start point on the map.";
  ui.reset.disabled = false;
  ui.preset.disabled = false;
  atlas.state = "ready";
  initMapView();
  initPresets();
}

// ---- endpoints / race flow ------------------------------------------------
const picked = { startId: null, endId: null };
let raceGeneration = 0; // bumped on every race start AND reset; the worker echoes it so stale results are dropped

function clearRaceReadouts() {
  ui.verdict.textContent = "Choose two points on the map.";
  for (const key of ["statTimeD", "statTimeA", "statNodesD", "statNodesA", "statDistance", "statReduction"]) ui[key].textContent = "—";
}

function onPick(latlng) {
  if (atlas.state !== "ready" && atlas.state !== "finished") return;
  const nodeId = snap(latlng);
  if (nodeId === null) { ui.hint.textContent = "No road nearby — try closer to a street."; return; }
  if (picked.startId === null) {
    picked.startId = nodeId;
    ui.hint.textContent = "Now click (or tap) a destination.";
  } else if (picked.endId === null) {
    if (nodeId === picked.startId) { ui.hint.textContent = "Start and destination are the same corner — pick somewhere else."; return; }
    picked.endId = nodeId;
    ui.hint.textContent = "Ready — press ▶ Race!";
    ui.race.disabled = false;
  } else {
    // Both endpoints already set — start a fresh selection from this click.
    // Deliberately no resetView(): the map stays right where the user is looking.
    if (atlas.view) atlas.view.clearRace();
    picked.startId = nodeId;
    picked.endId = null;
    ui.race.disabled = true;
    ui.hint.textContent = "Now click (or tap) a destination.";
    clearRaceReadouts();
  }

  if (atlas.view) atlas.view.setEndpoints(picked.startId, picked.endId);
}

function startRace() {
  if (picked.startId === null || picked.endId === null) return;
  atlas.state = "racing";
  ++raceGeneration;
  ui.race.disabled = true;
  ui.preset.disabled = true;
  ui.hint.textContent = "The surveyors are working…";

  if (atlas.view) atlas.view.resetView(); // pull back to the full city so the search is visible
  atlas.worker.postMessage({ type: "race", startId: picked.startId, endId: picked.endId, generation: raceGeneration });
}

function onRaceResult(race, generation) {
  if (generation !== raceGeneration) return; // stale result (Reset or a newer race arrived first)
  if (atlas.cancelRace) atlas.cancelRace(); // never let two replays mutate the shared animation state
  const controller = runRace(atlas.view, race, {
    getSpeed: () => parseFloat(ui.speed.value) || 1,
    onTick(dijkstraCount, aStarCount) {
      // the ledger's intersections row IS the live race counter
      ui.statNodesD.textContent = dijkstraCount.toLocaleString();
      ui.statNodesA.textContent = aStarCount.toLocaleString();
    },
    onDone() { finishRace(race); },
  });

  atlas.cancelRace = () => controller.cancel();
}

function finishRace(race) {
  atlas.state = "finished";
  ui.preset.disabled = false;
  ui.race.disabled = false;
  const d = race.dijkstra, a = race.aStar;
  ui.statTimeD.textContent = `${d.timeMs.toFixed(1)} ms`;
  ui.statTimeA.textContent = `${a.timeMs.toFixed(1)} ms`;
  ui.statNodesD.textContent = d.nodesExplored.toLocaleString();
  ui.statNodesA.textContent = a.nodesExplored.toLocaleString();

  if (a.distance !== null) {
    const km = (a.distance / 1000).toFixed(2);
    const mi = (a.distance / 1609.344).toFixed(2);
    ui.statDistance.textContent = `${km} km (${mi} mi)`;
    const saved = Math.round((1 - a.nodesExplored / d.nodesExplored) * 100);
    if (saved < 1) {
      ui.statReduction.textContent = "about equal";
      ui.verdict.textContent = `Both surveys agree: ${km} km. A* consulted ${a.nodesExplored.toLocaleString()} intersections to Dijkstra's ${d.nodesExplored.toLocaleString()} — about the same work on this route.`;
    } else {
      ui.statReduction.textContent = `${saved}% fewer intersections`;
      ui.verdict.textContent = `Both surveys agree: ${km} km. A* consulted only ${a.nodesExplored.toLocaleString()} intersections — ${saved}% fewer than Dijkstra's ${d.nodesExplored.toLocaleString()}.`;
    }
  } else {
    ui.verdict.textContent = "No route found between those points (this should be impossible — please file an issue!).";
  }

  if (atlas.view) atlas.view.flyToRoute(race.routeLine);
  ui.hint.textContent = "Race again, or Reset to choose new points.";
}

function resetAll() {
  ++raceGeneration; // invalidate any in-flight race so its result is dropped
  picked.startId = null;
  picked.endId = null;
  ui.race.disabled = true;
  clearRaceReadouts();
  ui.hint.textContent = "Click (or tap) a start point on the map.";
  ui.preset.value = "";
  if (atlas.view) { atlas.view.setEndpoints(null, null); atlas.view.clearRace(); atlas.view.resetView(); }
  if (atlas.cancelRace) atlas.cancelRace();
  atlas.state = "ready";
  ui.preset.disabled = false;
}

function showVeilError(message) {
  ui.veil.classList.remove("veil-hidden");
  ui.veil.classList.add("veil-error");
  ui.veil.querySelector(".veil-title").textContent = "The survey is postponed";
  ui.veilMessage.textContent = message;
  ui.heroStatus.textContent = "";
}

ui.race.addEventListener("click", startRace);
ui.reset.addEventListener("click", resetAll);
ui.modePlace.addEventListener("click", () => setMode("place"));
ui.modePan.addEventListener("click", () => setMode("pan"));

function setMode(mode) {
  ui.modePlace.classList.toggle("mode-on", mode === "place");
  ui.modePan.classList.toggle("mode-on", mode === "pan");
  if (atlas.view) atlas.view.setMode(mode);
  // Keep the idle hint truthful for the current mode (never clobber mid-selection or mid-race).
  if ((atlas.state === "ready" || atlas.state === "finished") && picked.startId === null) {
    ui.hint.textContent = mode === "place"
      ? "Click (or tap) a start point on the map."
      : "Pan mode — switch to “Set points” to choose a start.";
  }
}

// ---- map view, presets, code panel ----------------------------------------
function initMapView() {
  atlas.view = initPlate(atlas.bundle, onPick);
  const touch = window.matchMedia("(max-width: 900px)");
  setMode(touch.matches ? "pan" : "place"); // mobile starts safe: pan first, opt into placing
  touch.addEventListener("change", (e) => setMode(e.matches ? "pan" : "place"));
}

function snap(latlng) {
  const isTouch = window.matchMedia("(max-width: 900px)").matches;
  return snapToNode(atlas.bundle, latlng.lat, latlng.lng, isTouch ? 500 : 300);
}

// Landmark coordinates are approximate; each snaps to the nearest charted
// intersection at runtime (800 m budget — parks and stadiums sit back from
// the drive network).
const PRESETS = [
  { name: "The Swamp → Depot Park", from: [29.64994, -82.34858], to: [29.64414, -82.32188] },
  { name: "Butler Plaza → Downtown", from: [29.62563, -82.37659], to: [29.65163, -82.32483] },
  { name: "Airport → Santa Fe College", from: [29.67919, -82.27782], to: [29.68526, -82.37333] },
];

function initPresets() {
  for (const [index, preset] of PRESETS.entries()) {
    const option = document.createElement("option");
    option.value = String(index);
    option.textContent = preset.name;
    ui.preset.appendChild(option);
  }

  ui.preset.addEventListener("change", () => {
    if (ui.preset.value === "") return;
    const index = Number(ui.preset.value);
    const preset = PRESETS[index];
    const startId = snapToNode(atlas.bundle, preset.from[0], preset.from[1], 800);
    const endId = snapToNode(atlas.bundle, preset.to[0], preset.to[1], 800);

    if (startId === null || endId === null || startId === endId) {
      ui.hint.textContent = "That charted route is off this map edition — pick points by hand.";
      return;
    }

    resetAll();
    ui.preset.value = String(index);
    picked.startId = startId;
    picked.endId = endId;
    atlas.view.setEndpoints(startId, endId);
    ui.race.disabled = false;
    ui.hint.textContent = `${preset.name} — press ▶ Race!`;
  });
}
