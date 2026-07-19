// Builds the single atlas plate: ink-drawn roads, both exploration washes
// overlaid on one map, route tracing, endpoint markers, and snapping.
import { createCanvasLayer } from "./road-layer.js";

const INK = "#2b2620";
const ROAD = "rgba(43, 38, 32, 0.5)";
const WASH = { dijkstra: { rgb: "193, 81, 56", alpha: 0.35 }, aStar: { rgb: "30, 110, 100", alpha: 0.5 } };
const SEGMENT_CHUNK = 20000;

export function initPlate(bundle, onPick) {
  const state = {
    mode: "place",
    anim: { race: null, dijkstra: { count: 0 }, aStar: { count: 0 }, routeProgress: 0 },
  };

  const bounds = L.latLngBounds(
    [bundle.bbox[0], bundle.bbox[1]],
    [bundle.bbox[2], bundle.bbox[3]],
  );

  const homeView = bounds.pad(0.02); // the full-city framing: initial fit, reset target, zoom floor
  const map = L.map("plate-map", {
    zoomControl: false,
    attributionControl: false,
    maxBounds: bounds.pad(0.2),
    maxBoundsViscosity: 1.0,
    zoomSnap: 0.25,
  });

  map.fitBounds(homeView);
  // The full-city fit is the floor: never zoom out past the charted area.
  map.setMinZoom(map.getZoom());
  map.on("resize", () => {
    // Drop the floor before measuring: getBoundsZoom clamps to the current
    // minZoom, which would otherwise ratchet the floor up on every resize.
    map.setMinZoom(0);
    map.setMinZoom(map.getBoundsZoom(homeView));
  });

  L.control.zoom({ position: "topright" }).addTo(map);

  // Roads redraw only on move-end, so they get generous drag slack; the anim
  // wash clears every frame during a race, so it stays lean.
  createCanvasLayer((ctx, project) => drawRoads(ctx, project), 0.25).addTo(map);
  const anim = createCanvasLayer(drawAnim, 0.1).addTo(map);
  const markers = { start: null, end: null };
  map.on("click", (event) => {
    if (state.mode !== "place") return;
    onPick(event.latlng);
  });

  function drawRoads(ctx, project) {
    const seg = bundle.segments;
    const p = [0, 0];
    ctx.strokeStyle = ROAD;
    ctx.lineWidth = 0.8;
    for (let start = 0; start < seg.length; start += SEGMENT_CHUNK * 4) {
      const end = Math.min(seg.length, start + SEGMENT_CHUNK * 4);
      ctx.beginPath();
      for (let i = start; i < end; i += 4) {
        project(seg[i], seg[i + 1], p);
        ctx.moveTo(p[0], p[1]);
        project(seg[i + 2], seg[i + 3], p);
        ctx.lineTo(p[0], p[1]);
      }

      ctx.stroke();
    }
  }

  function drawAnim(ctx, project, clip) {
    const a = state.anim;
    if (!a.race) return;
    // Dijkstra's broad flood underneath, A*'s beam on top so the star reads
    drawWash(ctx, project, clip, "dijkstra");
    drawWash(ctx, project, clip, "aStar");
    if (a.routeProgress > 0 && a.race.routeLine.length >= 4) {
      drawRoute(ctx, project, a.race.routeLine, a.routeProgress);
    }
  }

  function drawWash(ctx, project, clip, algo) {
    const a = state.anim;
    const data = a.race[algo];
    const nodes = bundle.nodes;
    const p = [0, 0];
    // Dots grow and deepen with zoom so the two colors stay distinguishable
    // up close; at the full-city floor this matches the original flood look.
    const zoomIn = Math.max(0, map.getZoom() - map.getMinZoom());
    const size = Math.min(11, 3 + zoomIn * 1.6);
    const half = size / 2;
    const alpha = Math.min(0.9, WASH[algo].alpha + zoomIn * 0.12);
    ctx.fillStyle = `rgba(${WASH[algo].rgb}, ${alpha})`;
    const count = Math.min(Math.floor(a[algo].count), data.nodesExplored);
    for (let i = 0; i < count; i++) {
      const id = data.visitedOrder[i];
      project(nodes[id * 2], nodes[id * 2 + 1], p);
      if (p[0] < clip.x0 - half || p[0] > clip.x1 + half || p[1] < clip.y0 - half || p[1] > clip.y1 + half) continue;
      ctx.fillRect(p[0] - half, p[1] - half, size, size);
    }
  }

  function drawRoute(ctx, project, line, progress) {
    const points = Math.max(2, Math.round((line.length / 2) * progress));
    const p = [0, 0];
    ctx.strokeStyle = INK;
    ctx.lineWidth = 3;
    ctx.lineCap = "round";
    ctx.lineJoin = "round";
    ctx.beginPath();
    project(line[0], line[1], p);
    ctx.moveTo(p[0], p[1]);
    for (let i = 1; i < points; i++) {
      project(line[i * 2], line[i * 2 + 1], p);
      ctx.lineTo(p[0], p[1]);
    }

    ctx.stroke();
  }

  // Div-icon markers, not circleMarkers: Leaflet scales the SVG pane during
  // animated zooms (ballooning fixed-radius circles), but repositions icons.
  function endpointIcon(kind) {
    return L.divIcon({
      className: "atlas-endpoint",
      html: `<span class="atlas-endpoint-dot atlas-endpoint-${kind}"></span>`,
      iconSize: [14, 14],
      iconAnchor: [7, 7],
    });
  }

  function setEndpoints(startId, endId) {
    for (const key of ["start", "end"]) {
      if (markers[key]) { markers[key].remove(); markers[key] = null; }
    }

    if (startId !== null && startId !== undefined) {
      markers.start = L.marker(nodeLatLng(startId), {
        icon: endpointIcon("start"), interactive: false, keyboard: false,
      }).addTo(map);
    }

    if (endId !== null && endId !== undefined) {
      markers.end = L.marker(nodeLatLng(endId), {
        icon: endpointIcon("end"), interactive: false, keyboard: false,
      }).addTo(map);
    }
  }

  function nodeLatLng(id) { return [bundle.nodes[id * 2], bundle.nodes[id * 2 + 1]]; }

  return {
    state,
    map, // console/debug handle (window.__atlas.view.map); app code uses the methods below
    setMode(mode) { state.mode = mode; },
    setEndpoints,
    setRace(race) { state.anim.race = race; state.anim.dijkstra.count = 0; state.anim.aStar.count = 0; state.anim.routeProgress = 0; },
    clearRace() { state.anim.race = null; state.anim.dijkstra.count = 0; state.anim.aStar.count = 0; state.anim.routeProgress = 0; this.redrawAnim(); },
    redrawAnim() { anim.redraw(); },
    flyToRoute(routeLine) {
      // cinematic reveal: after the trace, glide in on the found path
      if (!routeLine || routeLine.length < 4) return;
      let south = 90, west = 180, north = -90, east = -180;
      for (let i = 0; i < routeLine.length; i += 2) {
        if (routeLine[i] < south) south = routeLine[i];
        if (routeLine[i] > north) north = routeLine[i];
        if (routeLine[i + 1] < west) west = routeLine[i + 1];
        if (routeLine[i + 1] > east) east = routeLine[i + 1];
      }
      const target = L.latLngBounds([south, west], [north, east]).pad(0.25);
      if (window.matchMedia("(prefers-reduced-motion: reduce)").matches) {
        map.fitBounds(target, { animate: false });
      } else {
        map.flyToBounds(target, { duration: 1.1 });
      }
    },
    resetView() {
      if (window.matchMedia("(prefers-reduced-motion: reduce)").matches) {
        map.fitBounds(homeView, { animate: false });
      } else {
        map.flyToBounds(homeView, { duration: 0.8 });
      }
    },
  };
}

// Nearest graph node to (lat, lng) within maxMeters, else null.
export function snapToNode(bundle, lat, lng, maxMeters) {
  const nodes = bundle.nodes;
  const cosLat = Math.cos((lat * Math.PI) / 180);
  let bestId = -1;
  let bestSq = Infinity;
  for (let id = 0; id * 2 < nodes.length; id++) {
    const dLat = nodes[id * 2] - lat;
    const dLng = (nodes[id * 2 + 1] - lng) * cosLat;
    const sq = dLat * dLat + dLng * dLng;
    if (sq < bestSq) { bestSq = sq; bestId = id; }
  }

  const meters = Math.sqrt(bestSq) * 111320;
  return meters <= maxMeters ? bestId : null;
}
