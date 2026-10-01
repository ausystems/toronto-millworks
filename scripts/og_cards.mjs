// Social cards: one 1200x630 JPEG per page, rendered by headless Chrome so the
// type is the real Instrument Sans and the drawings are the real drawings.
//
//   node scripts/og_cards.mjs            render cards whose spec changed
//   node scripts/og_cards.mjs --all      render every card
//
// Reads scripts/data/og_spec.json (written by build_site.py), writes
// assets/og/<slug>.jpg and remembers what it rendered in assets/og/.hashes.json.
// Needs Google Chrome; CI does not run it, the cards are committed.
import { spawn } from "node:child_process";
import { createHash } from "node:crypto";
import { existsSync, mkdirSync, readFileSync, writeFileSync, rmSync } from "node:fs";
import { dirname, join } from "node:path";
import { fileURLToPath, pathToFileURL } from "node:url";
import { tmpdir } from "node:os";

const ROOT = join(dirname(fileURLToPath(import.meta.url)), "..");
const OUT = join(ROOT, "assets", "og");
const CHROME = process.env.CHROME || "/Applications/Google Chrome.app/Contents/MacOS/Google Chrome";
const PORT = 9800 + Math.floor(Math.random() * 150);
const PROFILE = join(tmpdir(), "og-cards-" + PORT);
const sleep = (ms) => new Promise((r) => setTimeout(r, ms));
const all = process.argv.includes("--all");

const spec = JSON.parse(readFileSync(join(ROOT, "scripts", "data", "og_spec.json"), "utf8"));
const css = ["10-base.css", "90-drawings.css", "91-maps.css"]
  .map((f) => readFileSync(join(ROOT, "css", "src", f), "utf8")).join("\n");
const font = pathToFileURL(join(ROOT, "assets", "fonts", "instrument-sans-latin.woff2")).href;
const fileUrl = (p) => pathToFileURL(join(ROOT, p.replace(/^\//, ""))).href;
const esc = (s) => String(s).replace(/[&<>"]/g, (c) => ({ "&": "&amp;", "<": "&lt;", ">": "&gt;", '"': "&quot;" })[c]);

mkdirSync(OUT, { recursive: true });
const hashFile = join(OUT, ".hashes.json");
const hashes = existsSync(hashFile) ? JSON.parse(readFileSync(hashFile, "utf8")) : {};
const TEMPLATE_VERSION = "3";

function card(c) {
  const visual =
    c.kind === "photo" ? `<div class="v v--photo"><img src="${fileUrl(c.img)}" alt=""></div>` :
    c.kind === "map"   ? `<div class="v v--map">${c.svg}</div>` :
                         `<div class="v v--draw">${c.svg}</div>`;
  return `<!doctype html><html><head><meta charset="utf-8"><style>
@font-face{font-family:"Instrument Sans";font-weight:400 700;src:url("${font}") format("woff2");}
${css}
html,body{margin:0;width:1200px;height:630px;overflow:hidden;background:#fff;}
body{font-family:"Instrument Sans",system-ui,sans-serif;color:var(--ink);}
.c{position:relative;display:grid;grid-template-columns:600px 1fr;gap:44px;width:1200px;height:630px;box-sizing:border-box;padding:52px 52px 48px 64px;}
.l{display:flex;flex-direction:column;min-width:0;}
.brand{display:flex;align-items:center;gap:12px;font-size:21px;font-weight:600;letter-spacing:-.02em;}
.brand svg{width:34px;height:34px;color:var(--ink);}
.k{margin-top:auto;display:inline-flex;align-self:flex-start;align-items:center;gap:10px;padding:10px 18px 10px 15px;border:1px solid var(--line);border-radius:999px;font-size:17px;letter-spacing:.005em;}
.k i{width:8px;height:8px;border-radius:50%;background:var(--brass);}
.t{margin:22px 0 0;font-size:${c.title.length > 46 ? 54 : c.title.length > 30 ? 62 : 70}px;font-weight:400;line-height:1.02;letter-spacing:-.045em;text-wrap:balance;}
.f{margin-top:30px;padding-top:16px;border-top:1px solid var(--line);font-size:15px;letter-spacing:.12em;text-transform:uppercase;color:var(--ink-45);}
.v{border-radius:28px;overflow:hidden;height:100%;min-height:0;display:grid;place-items:center;}
.v--photo img{width:100%;height:100%;object-fit:cover;display:block;}
.v--draw{background:var(--paper-2);border:1px solid var(--line-soft);padding:26px;box-sizing:border-box;}
.v--map{border:1px solid var(--line-soft);}
.v svg{width:100%;height:100%;}
.v--map svg{height:100%;}
</style></head><body><div class="c"><div class="l">
<div class="brand"><svg viewBox="0 0 32 32" fill="none"><rect width="32" height="32" rx="9.5" fill="currentColor"/><path d="M7.5 22.6h17M10.4 18.9h14.1M13.3 15.2h11.2M16.2 11.5h8.3" stroke="#C08A3C" stroke-width="1.7" stroke-linecap="round"/></svg>Toronto Millworks</div>
<span class="k"><i></i>${esc(c.kicker)}</span>
<h1 class="t">${esc(c.title)}</h1>
<p class="f">Custom millwork · Toronto and the GTA</p>
</div>${visual}</div>
<script>
document.querySelectorAll(".v--map svg").forEach(function(s){s.setAttribute("preserveAspectRatio","xMidYMid slice");});
document.querySelectorAll("svg.dw, svg.mp").forEach(function(s){var vb=s.viewBox.baseVal;s.style.setProperty("--dws",(s.getBoundingClientRect().width/vb.width).toFixed(4));});
</script></body></html>`;
}

const chrome = spawn(CHROME, [
  "--headless=new", `--remote-debugging-port=${PORT}`, `--user-data-dir=${PROFILE}`,
  "--no-first-run", "--no-default-browser-check", "--hide-scrollbars", "--allow-file-access-from-files",
  "--force-color-profile=srgb", "about:blank"], { stdio: "ignore" });

async function ready() {
  for (let i = 0; i < 100; i++) {
    try { if ((await fetch(`http://127.0.0.1:${PORT}/json/version`)).ok) return; } catch {}
    await sleep(100);
  }
  throw new Error("Chrome did not start");
}

function connect(ws) {
  const sock = new WebSocket(ws);
  let id = 0; const wait = new Map(), events = [];
  sock.onmessage = (e) => {
    const m = JSON.parse(e.data);
    if (m.id && wait.has(m.id)) { const { res, rej } = wait.get(m.id); wait.delete(m.id); m.error ? rej(new Error(m.error.message)) : res(m.result); }
    else if (m.method) events.forEach((f) => f(m));
  };
  return {
    open: new Promise((r) => (sock.onopen = r)),
    send: (method, params = {}) => new Promise((res, rej) => { const i = ++id; wait.set(i, { res, rej }); sock.send(JSON.stringify({ id: i, method, params })); }),
    once: (name) => new Promise((r) => { const f = (m) => { if (m.method === name) { events.splice(events.indexOf(f), 1); r(m.params); } }; events.push(f); }),
    close: () => sock.close(),
  };
}

try {
  await ready();
  const tab = await (await fetch(`http://127.0.0.1:${PORT}/json/new?about:blank`, { method: "PUT" })).json();
  const s = connect(tab.webSocketDebuggerUrl);
  await s.open;
  await s.send("Page.enable");
  await s.send("Emulation.setDeviceMetricsOverride", { width: 1200, height: 630, deviceScaleFactor: 1, mobile: false });
  const tmp = join(tmpdir(), "og-card-" + PORT + ".html");
  let made = 0, skipped = 0;
  for (const c of spec) {
    const html = card(c);
    const h = createHash("sha256").update(TEMPLATE_VERSION + html).digest("hex").slice(0, 16);
    const dest = join(OUT, `${c.slug}.jpg`);
    if (!all && hashes[c.slug] === h && existsSync(dest)) { skipped++; continue; }
    writeFileSync(tmp, html);
    const loaded = s.once("Page.loadEventFired");
    await s.send("Page.navigate", { url: pathToFileURL(tmp).href });
    await loaded;
    await s.send("Runtime.evaluate", { expression: "document.fonts.ready.then(()=>new Promise(r=>requestAnimationFrame(()=>requestAnimationFrame(r))))", awaitPromise: true });
    await sleep(60);
    const shot = await s.send("Page.captureScreenshot", { format: "jpeg", quality: 86, clip: { x: 0, y: 0, width: 1200, height: 630, scale: 1 } });
    writeFileSync(dest, Buffer.from(shot.data, "base64"));
    hashes[c.slug] = h; made++;
  }
  writeFileSync(hashFile, JSON.stringify(hashes, null, 1));
  rmSync(tmp, { force: true });
  console.log(`social cards: ${made} rendered, ${skipped} unchanged -> assets/og/`);
  s.close();
} finally {
  chrome.kill("SIGKILL");
  try { rmSync(PROFILE, { recursive: true, force: true }); } catch {}
}
