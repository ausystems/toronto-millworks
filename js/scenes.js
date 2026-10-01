/* Toronto Millworks: the two places Three.js earns its weight.

     bench  (about)  a cabinet carcass that assembles as you scroll
     panel  (404)    a panelled wall in raking light, one panel missing

   Loaded on demand by main.js, only where WebGL exists. Each scene renders
   only while it is on screen. The page beneath already shows a drawing of
   the same object, so nothing is lost if this never runs. */
import * as THREE from "/assets/js/three/three.module.min.js";

export function mount (kind, host, opts) {
  try {
    if (kind === "bench") bench(host, opts || {});
    if (kind === "panel") panel(host, opts || {});
  } catch (e) { /* the drawing underneath stays */ }
}

/* ── shared ─────────────────────────────────────────────────────── */
function renderer (canvas) {
  const r = new THREE.WebGLRenderer({ canvas, antialias: true, alpha: true, powerPreference: "high-performance" });
  r.setPixelRatio(Math.min(window.devicePixelRatio || 1, 2));
  r.outputColorSpace = THREE.SRGBColorSpace;
  r.toneMapping = THREE.ACESFilmicToneMapping;
  r.toneMappingExposure = 1.02;
  r.shadowMap.enabled = true;
  r.shadowMap.type = THREE.PCFSoftShadowMap;
  return r;
}

/* procedural grain: long, wandering lines of varied weight, then pores */
function grain (base, ink, seed, w = 1024, h = 512) {
  const c = document.createElement("canvas");
  c.width = w; c.height = h;
  const g = c.getContext("2d");
  let s = seed;
  const rnd = () => (s = (s * 16807) % 2147483647) / 2147483647;
  g.fillStyle = base; g.fillRect(0, 0, w, h);
  for (let i = 0; i < 220; i++) {
    const y0 = rnd() * h, amp = 1.5 + rnd() * 7, f = 0.0018 + rnd() * 0.005, ph = rnd() * 6.283;
    g.strokeStyle = ink;
    g.globalAlpha = 0.03 + rnd() * 0.11;
    g.lineWidth = 0.5 + rnd() * 2.2;
    g.beginPath();
    for (let x = 0; x <= w; x += 6) {
      const y = y0 + Math.sin(x * f + ph) * amp + Math.sin(x * f * 3.3 + ph * 1.7) * amp * 0.22;
      if (x) g.lineTo(x, y); else g.moveTo(x, y);
    }
    g.stroke();
  }
  g.globalAlpha = 0.05;
  g.fillStyle = ink;
  for (let i = 0; i < 3800; i++) g.fillRect(rnd() * w, rnd() * h, 1.5 + rnd() * 5, 0.8);
  g.globalAlpha = 1;
  const t = new THREE.CanvasTexture(c);
  t.colorSpace = THREE.SRGBColorSpace;
  t.wrapS = t.wrapT = THREE.RepeatWrapping;
  t.anisotropy = 8;
  return t;
}

const ease = (x) => (x < 0.5 ? 4 * x * x * x : 1 - Math.pow(-2 * x + 2, 3) / 2);
const clamp = (v, a, b) => Math.max(a, Math.min(b, v));

function onScreen (el, cb) {
  if (!("IntersectionObserver" in window)) return cb(true);
  new IntersectionObserver((es) => cb(es[0].isIntersecting), { rootMargin: "120px 0px" }).observe(el);
}

/* ══════════════════════════════════════════════════════════════════
   BENCH: an exploded carcass that comes together as you scroll
   ══════════════════════════════════════════════════════════════════ */
function bench (host, { reduced }) {
  const canvas = host.querySelector(".bench__cv");
  const stage = host.querySelector(".bench__stage");
  if (!canvas || !stage) return;
  const r = renderer(canvas);
  const scene = new THREE.Scene();
  const camera = new THREE.PerspectiveCamera(30, 1, 0.05, 60);

  /* a north window, a warm key from the left, a cool rim behind */
  scene.add(new THREE.HemisphereLight(0xfff5e8, 0xcdbea8, 1.15));
  const key = new THREE.DirectionalLight(0xffecd2, 2.7);
  key.position.set(-2.4, 3.6, 2.4);
  key.castShadow = true;
  key.shadow.mapSize.set(2048, 2048);
  key.shadow.radius = 5;
  key.shadow.bias = -0.0005;
  Object.assign(key.shadow.camera, { left: -1.6, right: 1.6, top: 1.6, bottom: -1.6, near: 0.5, far: 12 });
  scene.add(key);
  const rim = new THREE.DirectionalLight(0xdbe7ff, 0.85);
  rim.position.set(2.6, 1.8, -2.4);
  scene.add(rim);

  const floor = new THREE.Mesh(new THREE.PlaneGeometry(10, 10), new THREE.ShadowMaterial({ opacity: 0.15 }));
  floor.rotation.x = -Math.PI / 2;
  floor.receiveShadow = true;
  scene.add(floor);

  const ply = new THREE.MeshStandardMaterial({ map: grain("#EADCC2", "#B39672", 7), roughness: 0.62 });
  const oak = new THREE.MeshStandardMaterial({ map: grain("#CBA67A", "#7E5C39", 19), roughness: 0.48 });
  const brass = new THREE.MeshStandardMaterial({ color: 0xc08a3c, roughness: 0.3, metalness: 1 });
  const lines = new THREE.LineBasicMaterial({ color: 0x17140f, transparent: true, opacity: 0.26 });

  /* 600 wide, 760 high, 560 deep, in 18 mm stock, in metres */
  const W = 0.6, H = 0.76, D = 0.56, t = 0.018, cy = H / 2;
  const parts = [];
  function part (geo, mat, at, from, rot, win) {
    const m = new THREE.Mesh(geo, mat);
    m.castShadow = true; m.receiveShadow = true;
    m.add(new THREE.LineSegments(new THREE.EdgesGeometry(geo, 20), lines));
    const g = new THREE.Group();
    g.add(m);
    scene.add(g);
    parts.push({ g, at: new THREE.Vector3(...at), from: new THREE.Vector3(...from),
                 q0: new THREE.Quaternion().setFromEuler(new THREE.Euler(...rot)), win });
  }
  const box = (w, h, d) => new THREE.BoxGeometry(w, h, d);
  part(box(t, H, D), ply, [-W / 2 + t / 2, cy, 0], [-0.66, cy + 0.06, 0.08], [0, 0.18, -0.06], [0.00, 0.30]);
  part(box(t, H, D), ply, [W / 2 - t / 2, cy, 0], [0.66, cy + 0.06, 0.08], [0, -0.18, 0.06], [0.04, 0.34]);
  part(box(W - 2 * t, t, D), ply, [0, t / 2, 0], [0, 0.01, 0.64], [0, 0, 0], [0.22, 0.50]);
  part(box(W - 2 * t, t, D), ply, [0, H - t / 2, 0], [0, H + 0.44, 0.04], [0.22, 0, 0], [0.26, 0.54]);
  part(box(W - 2 * t, H - 2 * t, 0.006), ply, [0, cy, -D / 2 + 0.003], [0, cy + 0.04, -0.8], [0, 0, 0], [0.46, 0.74]);
  part(box(W - 2 * t - 0.002, t, D - 0.04), ply, [0, H * 0.52, 0.01], [0, H * 0.52 + 0.1, 0.74], [0, 0, 0.1], [0.62, 0.86]);
  part(box(W - 0.004, H - 0.004, 0.019), oak, [0, cy, D / 2 + 0.0095], [0.06, cy + 0.03, 1.1], [0, -0.5, 0], [0.72, 0.97]);
  const pull = new THREE.CylinderGeometry(0.0065, 0.0065, 0.15, 24);
  part(pull, brass, [W / 2 - 0.055, cy + 0.12, D / 2 + 0.036], [W / 2 - 0.055, cy + 0.12, 1.32], [0, 0, 0], [0.84, 1.0]);

  const target = new THREE.Vector3(0, 0.36, 0.08);
  const ident = new THREE.Quaternion();
  let p = reduced ? 1 : 0, want = p, px = 0, py = 0, mx = 0, my = 0;
  let visible = false, raf = 0, ready = false;

  function progress () {
    const b = host.getBoundingClientRect(), span = b.height - window.innerHeight;
    return span > 0 ? clamp(-b.top / span, 0, 1) : 1;
  }
  function size () {
    const w = stage.clientWidth, h = stage.clientHeight;
    if (!w || !h) return;
    r.setSize(w, h, false);
    camera.aspect = w / h;
    camera.updateProjectionMatrix();
  }
  function frame (now) {
    raf = 0;
    if (!reduced) want = progress();
    p += (want - p) * 0.1;
    if (Math.abs(want - p) < 0.0004) p = want;
    mx += (px - mx) * 0.06; my += (py - my) * 0.06;

    for (const it of parts) {
      const k = ease(clamp((p - it.win[0]) / (it.win[1] - it.win[0]), 0, 1));
      it.g.position.lerpVectors(it.from, it.at, k);
      it.g.quaternion.slerpQuaternions(it.q0, ident, k);
    }
    const breathe = reduced ? 0 : Math.sin((now || 0) / 2400) * 0.015;
    const az = 0.74 - p * 0.24 + mx * 0.08 + breathe;
    const el = 0.36 + my * 0.05;
    const dist = 3.6 - p * 0.95;
    camera.position.set(Math.sin(az) * Math.cos(el) * dist, target.y + Math.sin(el) * dist, Math.cos(az) * Math.cos(el) * dist);
    camera.lookAt(target);
    r.render(scene, camera);
    if (!ready) { ready = true; host.classList.add("is-3d"); }
    if (visible && !reduced) raf = requestAnimationFrame(frame);
  }
  const kick = () => { if (!raf) raf = requestAnimationFrame(frame); };

  size();
  if ("ResizeObserver" in window) new ResizeObserver(() => { size(); kick(); }).observe(stage);
  host.addEventListener("pointermove", (e) => {
    const b = stage.getBoundingClientRect();
    px = clamp(((e.clientX - b.left) / b.width) * 2 - 1, -1, 1);
    py = clamp(((e.clientY - b.top) / b.height) * 2 - 1, -1, 1);
  }, { passive: true });
  onScreen(host, (on) => { visible = on; if (on) kick(); });
  kick();
}

/* ══════════════════════════════════════════════════════════════════
   PANEL: a raised panel wall in raking light, with one panel missing
   ══════════════════════════════════════════════════════════════════ */
function panel (host, { reduced }) {
  const canvas = host.querySelector(".nf__cv");
  if (!canvas) return;
  const r = renderer(canvas);
  r.toneMappingExposure = 0.92;
  const scene = new THREE.Scene();
  const camera = new THREE.PerspectiveCamera(30, 1, 0.1, 40);

  const paint = new THREE.MeshStandardMaterial({ color: 0xdcd2c2, roughness: 0.86 });
  const shadowed = new THREE.MeshStandardMaterial({ color: 0x2c261f, roughness: 0.95 });
  const brass = new THREE.MeshStandardMaterial({ color: 0xc08a3c, roughness: 0.34, metalness: 1 });
  const floorMat = new THREE.MeshStandardMaterial({ map: grain("#A88663", "#5E4430", 23, 1024, 1024), roughness: 0.58 });
  floorMat.map.repeat.set(3, 3);

  /* the room: wall, floor, and the panelling on the wall */
  const COLS = 7, CW = 0.86, ST = 0.09;                    /* cell width and stile */
  const LOW = 0.56, UP = 1.24, BASE = 0.16;                /* dado, upper panel, base */
  const wallW = COLS * (CW + ST) + ST;
  const x0 = -wallW / 2;
  const yBase = 0, yLow = yBase + BASE + ST, yRail = yLow + LOW, yUp = yRail + ST, yTop = yUp + UP;

  /* the wall has a real opening where the panel is missing, so the void
     behind it can be deep and take a proper shadow */
  const MISS = { c: 4, row: "up" };
  const mcx = x0 + ST + MISS.c * (CW + ST) + CW / 2, mcy = yUp + UP / 2;
  const ws = new THREE.Shape();
  ws.moveTo(-(wallW + 6) / 2, -1.3); ws.lineTo((wallW + 6) / 2, -1.3);
  ws.lineTo((wallW + 6) / 2, 5.7); ws.lineTo(-(wallW + 6) / 2, 5.7); ws.closePath();
  const hole = new THREE.Path();
  hole.moveTo(mcx - CW / 2, mcy - UP / 2); hole.lineTo(mcx - CW / 2, mcy + UP / 2);
  hole.lineTo(mcx + CW / 2, mcy + UP / 2); hole.lineTo(mcx + CW / 2, mcy - UP / 2); hole.closePath();
  ws.holes.push(hole);
  const wall = new THREE.Mesh(new THREE.ShapeGeometry(ws), paint);
  wall.position.z = -0.001;
  wall.receiveShadow = true;
  scene.add(wall);
  const floor = new THREE.Mesh(new THREE.PlaneGeometry(wallW + 6, 6), floorMat);
  floor.rotation.x = -Math.PI / 2;
  floor.position.set(0, 0, 3);
  floor.receiveShadow = true;
  scene.add(floor);

  function add (geo, mat, x, y, z) {
    const m = new THREE.Mesh(geo, mat);
    m.position.set(x, y, z);
    m.castShadow = true; m.receiveShadow = true;
    scene.add(m);
    return m;
  }
  const B = (w, h, d) => new THREE.BoxGeometry(w, h, d);

  /* frame: base, rails and stiles stand proud of the wall */
  add(B(wallW, BASE, 0.03), paint, 0, BASE / 2, 0.015);
  add(B(wallW + 0.02, 0.022, 0.044), paint, 0, BASE + 0.011, 0.022);
  for (const y of [yLow - ST / 2, yRail + ST / 2, yTop + ST / 2]) add(B(wallW, ST, 0.022), paint, 0, y, 0.011);
  add(B(wallW + 0.06, 0.05, 0.07), paint, 0, yTop + ST + 0.025, 0.035);         /* cap moulding */
  for (let c = 0; c <= COLS; c++) {
    const x = x0 + ST / 2 + c * (CW + ST);
    add(B(ST, yTop - yLow + ST * 2, 0.022), paint, x, (yLow + yTop) / 2, 0.011);
  }

  /* raised fields: a bevelled extrusion is exactly a raised panel */
  function field (w, h) {
    const s = new THREE.Shape();
    s.moveTo(-w / 2, -h / 2); s.lineTo(w / 2, -h / 2); s.lineTo(w / 2, h / 2); s.lineTo(-w / 2, h / 2); s.closePath();
    const bevel = Math.min(w, h) * 0.07;
    const g = new THREE.ExtrudeGeometry(s, { depth: 0.004, bevelEnabled: true, bevelThickness: 0.014,
                                               bevelSize: bevel, bevelSegments: 2, curveSegments: 1 });
    g.translate(0, 0, 0.004);
    return g;
  }
  for (let c = 0; c < COLS; c++) {
    const x = x0 + ST + c * (CW + ST) + CW / 2;
    for (const [row, y0, h] of [["low", yLow, LOW], ["up", yUp, UP]]) {
      const cx = x, cy = y0 + h / 2;
      if (c === MISS.c && row === MISS.row) {
        /* the missing panel: a dark void with its reveal returns, and the code
           routed into the back of it in brass */
        const deep = 0.12;
        add(B(CW, h, 0.006), shadowed, cx, cy, -deep);
        add(B(CW, 0.014, deep), paint, cx, y0 + 0.007, -deep / 2);
        add(B(CW, 0.014, deep), paint, cx, y0 + h - 0.007, -deep / 2);
        add(B(0.014, h, deep), paint, cx - CW / 2 + 0.007, cy, -deep / 2);
        add(B(0.014, h, deep), paint, cx + CW / 2 - 0.007, cy, -deep / 2);
        digits(cx, cy);
        continue;
      }
      add(field(CW - 0.05, h - 0.05), paint, cx, cy, 0);
    }
  }

  /* 4, 0, 4 as extruded outlines, cut from shapes rather than a font file */
  function digits (cx, cy) {
    const k = 0.58;
    const four = new THREE.Shape();
    [[0.180, 0], [0.235, 0], [0.235, 0.110], [0.290, 0.110], [0.290, 0.165], [0.235, 0.165],
     [0.235, 0.420], [0.172, 0.420], [0, 0.180], [0, 0.110], [0.180, 0.110]].forEach(([x, y], i) =>
      i ? four.lineTo(x, y) : four.moveTo(x, y));
    four.closePath();
    const hole = new THREE.Path();
    hole.moveTo(0.068, 0.165); hole.lineTo(0.180, 0.165); hole.lineTo(0.180, 0.325); hole.closePath();
    four.holes.push(hole);
    const zero = new THREE.Shape();
    zero.absellipse(0.13, 0.21, 0.13, 0.21, 0, Math.PI * 2, false, 0);
    const zh = new THREE.Path();
    zh.absellipse(0.13, 0.21, 0.074, 0.152, 0, Math.PI * 2, true, 0);
    zero.holes.push(zh);
    const opts = { depth: 0.018, bevelEnabled: true, bevelThickness: 0.004, bevelSize: 0.003, bevelSegments: 2, curveSegments: 40 };
    const gap = 0.06, widths = [0.29, 0.26, 0.29];
    const total = (widths[0] + widths[1] + widths[2] + gap * 2) * k;
    let x = cx - total / 2;
    [four, zero, four].forEach((shape, i) => {
      const g = new THREE.ExtrudeGeometry(shape, opts);
      g.scale(k, k, 1);
      const m = add(g, brass, x, cy - 0.21 * k, -0.114);
      m.castShadow = true;
      x += (widths[i] + gap) * k;
    });
  }

  /* light: a low raking lamp that follows the pointer, as a joiner tilts a
     light across a surface to read it, over a dim, warm room */
  scene.add(new THREE.HemisphereLight(0xfff3e2, 0x6f5d4b, 0.42));
  const fill = new THREE.DirectionalLight(0xffe9cf, 0.42);
  fill.position.set(-1.5, 3.5, 6);
  scene.add(fill);
  /* the lamp sits off to one side and close to the wall, so its light runs
     across the surface rather than at it: every moulding throws a shadow */
  const lamp = new THREE.SpotLight(0xffdcae, 9, 0, 0.78, 1, 1.35);
  lamp.castShadow = true;
  lamp.shadow.mapSize.set(1024, 1024);
  lamp.shadow.bias = -0.0006;
  lamp.shadow.radius = 4;
  scene.add(lamp);
  scene.add(lamp.target);

  const miss = new THREE.Vector3(x0 + ST + MISS.c * (CW + ST) + CW / 2, yUp + UP / 2, 0);
  let px = null, py = 0, lx = miss.x - 1.2, ly = miss.y + 0.4, visible = true, raf = 0, ready = false;

  function size () {
    const w = host.clientWidth, h = host.clientHeight;
    if (!w || !h) return;
    r.setSize(w, h, false);
    camera.aspect = w / h;
    camera.updateProjectionMatrix();
  }
  function frame (now) {
    raf = 0;
    const t = (now || 0) / 1000;
    /* the pointer slides the lamp along the wall; without one it wanders */
    const tx = px === null || reduced ? miss.x - 1.7 + Math.sin(t * 0.3) * 0.9 : miss.x - 2.1 + px * 1.7;
    const ty = px === null || reduced ? miss.y + 0.2 + Math.cos(t * 0.21) * 0.5 : miss.y + 0.1 + py * 0.7;
    lx += ((reduced ? miss.x - 1.6 : tx) - lx) * 0.06;
    ly += ((reduced ? miss.y + 0.3 : ty) - ly) * 0.06;
    lamp.position.set(lx, ly, 0.58);
    lamp.target.position.set(lx + 2.4, ly - 0.18, 0);

    const portrait = camera.aspect < 1;
    const look = new THREE.Vector3(portrait ? miss.x - 0.2 : miss.x - 1.15, portrait ? miss.y - 1.05 : miss.y - 0.32, 0);
    const pxx = px === null ? 0 : px, pyy = px === null ? 0 : py;
    camera.position.set(look.x - 0.8 + pxx * 0.18, look.y + 0.28 - pyy * 0.08, portrait ? 6.8 : 5.9);
    camera.lookAt(look);
    r.render(scene, camera);
    if (!ready) { ready = true; host.classList.add("is-3d"); }
    if (visible && !reduced) raf = requestAnimationFrame(frame);
  }
  const kick = () => { if (!raf) raf = requestAnimationFrame(frame); };

  size();
  if ("ResizeObserver" in window) new ResizeObserver(() => { size(); kick(); }).observe(host);
  host.addEventListener("pointermove", (e) => {
    if (e.pointerType !== "mouse") return;
    const b = host.getBoundingClientRect();
    px = clamp(((e.clientX - b.left) / b.width) * 2 - 1, -1, 1);
    py = clamp(-(((e.clientY - b.top) / b.height) * 2 - 1), -1, 1);
  }, { passive: true });
  host.addEventListener("pointerleave", () => { px = null; });
  onScreen(host, (on) => { visible = on; if (on) kick(); });
  kick();
}
