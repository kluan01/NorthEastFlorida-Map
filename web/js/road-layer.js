// A Leaflet layer that hands a padded, viewport-sized <canvas> to a draw
// callback. Full redraw on moveend/resize; between redraws the canvas rides
// the map pane (drags) or is CSS-transformed in step with Leaflet's own zoom
// animation (wheel, double-click, flyTo) — the same scheme L.Renderer uses —
// so the drawing stays visible and glued to the map through animated zooms.
// Mirrors L.Renderer 1.9.4 internals (map._getNewPixelOrigin, _animatingZoom):
// revisit this file if web/vendor/leaflet is ever upgraded.

// padding: fraction of the viewport drawn beyond each edge (drag slack).
export function createCanvasLayer(drawFn, padding = 0.25) {
  const CanvasLayer = L.Layer.extend({
    onAdd(map) {
      this._map = map;
      this._canvas = L.DomUtil.create("canvas", "atlas-canvas leaflet-zoom-animated");
      this._canvas.style.pointerEvents = "none";
      map.getPanes().overlayPane.appendChild(this._canvas);
      // moveend suffices for zoomend/viewreset too: Leaflet always fires it
      // right after both (_moveEnd fires zoomend then moveend; _resetView
      // fires viewreset after _moveEnd), so extra bindings just redraw twice.
      map.on("moveend resize", this.redraw, this);
      map.on("zoom", this._onZoom, this);
      map.on("zoomanim", this._onZoomAnim, this);
      this.redraw();
      return this;
    },
    onRemove(map) {
      map.off("moveend resize", this.redraw, this);
      map.off("zoom", this._onZoom, this);
      map.off("zoomanim", this._onZoomAnim, this);
      L.DomUtil.remove(this._canvas);
    },
    // "zoom" fires per frame during flyTo; "zoomanim" once per animated zoom
    // (the leaflet-zoom-animated class lets CSS transition that one smoothly).
    _onZoom() { this._updateTransform(this._map.getCenter(), this._map.getZoom()); },
    _onZoomAnim(event) { this._updateTransform(event.center, event.zoom); },
    _updateTransform(center, zoom) {
      if (!this._center) return;
      const map = this._map;
      const scale = map.getZoomScale(zoom, this._zoom);
      const viewHalf = map.getSize().multiplyBy(0.5 + padding);
      const currentCenter = map.project(this._center, zoom);
      const offset = viewHalf.multiplyBy(-scale).add(currentCenter)
        .subtract(map._getNewPixelOrigin(center, zoom));
      L.DomUtil.setTransform(this._canvas, offset, scale);
    },
    redraw() {
      const map = this._map;
      if (!map || map._animatingZoom) return;
      const size = map.getSize();
      const min = map.containerPointToLayerPoint(size.multiplyBy(-padding)).round();
      const canvasSize = size.multiplyBy(1 + padding * 2).round();
      this._center = map.getCenter();
      this._zoom = map.getZoom();
      const ratio = window.devicePixelRatio || 1;
      if (this._lastSizeX !== canvasSize.x || this._lastSizeY !== canvasSize.y || this._lastRatio !== ratio) {
        this._canvas.width = canvasSize.x * ratio;
        this._canvas.height = canvasSize.y * ratio;
        this._canvas.style.width = canvasSize.x + "px";
        this._canvas.style.height = canvasSize.y + "px";
        this._lastSizeX = canvasSize.x;
        this._lastSizeY = canvasSize.y;
        this._lastRatio = ratio;
      }
      L.DomUtil.setPosition(this._canvas, min);
      const ctx = this._canvas.getContext("2d");
      // Draw in layer coordinates: shift so the canvas's padded top-left is 0,0.
      ctx.setTransform(ratio, 0, 0, ratio, -min.x * ratio, -min.y * ratio);
      ctx.clearRect(min.x, min.y, canvasSize.x, canvasSize.y);
      // clip: the canvas's extent in layer pixels, for cheap per-point culling
      drawFn(ctx, makeProjector(map), {
        x0: min.x, y0: min.y, x1: min.x + canvasSize.x, y1: min.y + canvasSize.y,
      });
    },
  });
  return new CanvasLayer();
}

// Fast lat/lng -> layer-pixel projector (no per-point allocations).
// Mirrors Leaflet's spherical-mercator math relative to the pixel origin.
function makeProjector(map) {
  const scale = 256 * Math.pow(2, map.getZoom());
  const origin = map.getPixelOrigin();
  const DEG = Math.PI / 180;
  return (lat, lng, out) => {
    const sin = Math.sin(lat * DEG);
    out[0] = scale * (lng / 360 + 0.5) - origin.x;
    out[1] = scale * (0.5 - Math.log((1 + sin) / (1 - sin)) / (4 * Math.PI)) - origin.y;
  };
}
