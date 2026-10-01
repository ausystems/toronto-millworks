// Local server that behaves like production: it applies the headers, redirects,
// clean URLs, trailing slashes and real 404 status declared in vercel.json, in
// the order Vercel applies them, and refuses whatever .vercelignore keeps out of
// the deployment, so a Content-Security-Policy mistake or a leaked source file
// shows up here rather than after deploy.
//
//   node scripts/serve.mjs [port]        default 4180
import { createServer } from "node:http";
import { readFileSync, statSync, createReadStream } from "node:fs";
import { extname, join, normalize } from "node:path";
import { fileURLToPath } from "node:url";

const ROOT = normalize(join(fileURLToPath(import.meta.url), "..", ".."));
const PORT = Number(process.argv[2] || 4180);
const cfg = JSON.parse(readFileSync(join(ROOT, "vercel.json"), "utf8"));
const ignored = readFileSync(join(ROOT, ".vercelignore"), "utf8").split("\n")
  .map((l) => l.trim()).filter((l) => l && !l.startsWith("#"));
const TYPES = { ".html": "text/html; charset=utf-8", ".css": "text/css; charset=utf-8", ".js": "text/javascript; charset=utf-8",
  ".mjs": "text/javascript; charset=utf-8", ".json": "application/json", ".webmanifest": "application/manifest+json",
  ".svg": "image/svg+xml", ".png": "image/png", ".jpg": "image/jpeg", ".webp": "image/webp", ".woff2": "font/woff2",
  ".txt": "text/plain; charset=utf-8", ".xml": "application/xml" };

// vercel source patterns are path-to-regexp; the ones used here are simple
const rx = (src) => new RegExp("^" + src.replace(/\(\.\*\)/g, "(.*)").replace(/\((\w+(?:\|\w+)*)\)/g, "($1)") + "$");
const headerRules = cfg.headers.map((h) => ({ re: rx(h.source), headers: h.headers }));
const redirects = cfg.redirects.map((r) => ({ re: rx(r.source), to: r.destination }));
// a trailing slash in .vercelignore marks a directory
const hidden = (p) => ignored.some((g) => (g.endsWith("/") ? p.startsWith(g) || p === g.slice(0, -1) : p === g));

function file(p) {
  const f = join(ROOT, p);
  if (!f.startsWith(ROOT) || hidden(p)) return null;
  try { return statSync(f).isFile() ? f : null; } catch { return null; }
}

createServer((req, res) => {
  const url = new URL(req.url, "http://x");
  const path = decodeURIComponent(url.pathname);
  const send = (code, f, extra = {}) => {
    const hs = {};
    for (const h of headerRules) if (h.re.test(path)) for (const { key, value } of h.headers) hs[key] = value;
    res.writeHead(code, { ...hs, ...extra, ...(f ? { "Content-Type": TYPES[extname(f)] || "application/octet-stream" } : {}) });
    if (f) createReadStream(f).pipe(res); else res.end();
  };
  const go = (to) => send(308, null, { Location: to + url.search });
  // clean URLs and the trailing slash come first, in one hop...
  if (path.endsWith(".html")) return go(path.replace(/(index)?\.html$/, "").replace(/([^/])$/, "$1/"));
  const asFile = file(path);
  if (asFile && !path.endsWith("/")) return send(200, asFile);
  if (!path.endsWith("/") && !extname(path)) return go(path + "/");
  // ...then the declared redirects, matched against the normalised path...
  for (const r of redirects) if (r.re.test(path)) return go(r.to);
  // ...then the filesystem, where /x/ is x/index.html or x.html
  const page = file(join(path, "index.html")) || (path.length > 1 && file(path.slice(0, -1) + ".html"));
  if (page) return send(200, page);
  return send(404, join(ROOT, "404.html"));
}).listen(PORT, () => console.log(`serving ${ROOT} like production on http://localhost:${PORT}`));
