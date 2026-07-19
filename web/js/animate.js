// Replays both explorations at one shared nodes-per-second rate (so the
// faster algorithm visibly finishes first), then traces the final route.
const BASE_DURATION_MS = 4500;
const ROUTE_DURATION_MS = 700;

export function runRace(view, race, options) {
  const anim = view.state.anim;
  view.setRace(race);

  const total = Math.max(race.dijkstra.nodesExplored, race.aStar.nodesExplored);
  // read the slider every frame so speed changes take effect mid-race
  const nodesPerMs = () => total / (BASE_DURATION_MS / options.getSpeed());

  let cancelled = false;
  let phase = "explore";
  let routeStart = 0;
  let last = performance.now();

  function frame(now) {
    if (cancelled) return;
    const dt = Math.min(now - last, 100); // clamp tab-switch jumps
    last = now;

    if (phase === "explore") {
      const step = nodesPerMs() * dt;
      anim.dijkstra.count = Math.min(race.dijkstra.nodesExplored, anim.dijkstra.count + step);
      anim.aStar.count = Math.min(race.aStar.nodesExplored, anim.aStar.count + step);
      options.onTick(Math.floor(anim.dijkstra.count), Math.floor(anim.aStar.count));

      if (anim.dijkstra.count >= race.dijkstra.nodesExplored && anim.aStar.count >= race.aStar.nodesExplored) {
        phase = "route";
        routeStart = now;
      }
    } else {
      anim.routeProgress = Math.min(1, (now - routeStart) / ROUTE_DURATION_MS);
    }

    view.redrawAnim();

    if (phase === "route" && anim.routeProgress >= 1) {
      options.onDone();
      return;
    }

    requestAnimationFrame(frame);
  }

  requestAnimationFrame(frame);
  return { cancel() { cancelled = true; } };
}
