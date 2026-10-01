// Post-deploy smoke test. Reads the deployed site the way a crawler and a
// visitor would, and exits 1 on anything that would cost a ranking or a visit.
//
//   node scripts/smoke.mjs                         the production origin
//   node scripts/smoke.mjs http://localhost:4180   a local scripts/serve.mjs
//
// Every sitemap URL answers 200, is indexable, names itself as canonical and has
// a social image that loads; every vercel.json redirect lands on its page within
// two hops; a missing path answers a real 404 with the designed page; pages carry
// the security headers; the crawler files are served; nothing in .vercelignore
// can be downloaded.
import { readFileSync, readdirSync, statSync } from "node:fs";
import { join, sep } from "node:path";
import { fileURLToPath } from "node:url";

const ROOT = join(fileURLToPath(import.meta.url), "..", "..");
const local = (p) => readFileSync(join(ROOT, p), "utf8");
const PROD = new URL(local("sitemap.xml").match(/<loc>([^<]+)<\/loc>/)[1]).origin;
const BASE = (process.argv[2] || PROD).replace(/\/$/, "");
const at = (u) => u.replace(PROD, BASE);
const fails = [];
const fail = (m) => fails.push(m);
const pick = (html, re) => (html.match(re) || [])[1];

async function follow(url, max = 5) {
  for (let hops = 0; ; hops++) {
    const r = await fetch(url, { redirect: "manual" });
    if (r.status < 300 || r.status >= 400) return { r, url, hops };
    await r.body?.cancel();
    if (hops === max) throw new Error(`redirect loop at ${url}`);
    url = new URL(r.headers.get("location"), url).href;
  }
}

async function pool(items, n, fn) {
  let i = 0;
  await Promise.all(Array.from({ length: n }, async () => { while (i < items.length) await fn(items[i++]); }));
}

// ── every page in the sitemap
const sitemap = await (await fetch(BASE + "/sitemap.xml")).text();
const locs = [...sitemap.matchAll(/<loc>([^<]+)<\/loc>/g)].map((m) => m[1]);
if (!locs.length) fail("the deployed sitemap lists no pages");
const ogs = new Set();
await pool(locs, 8, async (loc) => {
  const r = await fetch(at(loc), { redirect: "manual" });
  if (r.status !== 200) { await r.body?.cancel(); return fail(`${loc} answered ${r.status}`); }
  const html = await r.text();
  const canon = pick(html, /<link rel="canonical" href="([^"]+)"/);
  if (canon !== loc) fail(`${loc} declares canonical ${canon}`);
  const robots = (pick(html, /<meta name="robots" content="([^"]+)"/) || "") + (r.headers.get("x-robots-tag") || "");
  if (robots.includes("noindex")) fail(`${loc} is in the sitemap but noindex`);
  if (!r.headers.get("content-security-policy")) fail(`${loc} has no Content-Security-Policy`);
  const og = pick(html, /<meta property="og:image" content="([^"]+)"/);
  if (og) ogs.add(og); else fail(`${loc} has no og:image`);
});
await pool([...ogs], 8, async (og) => {
  const r = await fetch(at(og), { method: "HEAD" });
  if (r.status !== 200 || !(r.headers.get("content-type") || "").startsWith("image/")) fail(`${og} answered ${r.status}`);
});

// ── redirects
const { redirects } = JSON.parse(local("vercel.json"));
await pool(redirects, 6, async ({ source, destination }) => {
  const { r, url, hops } = await follow(BASE + source);
  await r.body?.cancel();
  const path = new URL(url).pathname;
  if (r.status !== 200 || path !== destination) fail(`redirect ${source} ends at ${path} (${r.status})`);
  else if (hops > 2) fail(`redirect ${source} takes ${hops} hops`);
});

// ── a missing page is a real 404, and the designed one
{
  const r = await fetch(`${BASE}/smoke-missing-${Date.now()}/`, { redirect: "manual" });
  const html = await r.text();
  if (r.status !== 404) fail(`a missing path answered ${r.status}, not 404`);
  if (!html.includes('class="nf"')) fail("a missing path does not show the designed 404 page");
  if (html.includes('rel="canonical"')) fail("the 404 page declares a canonical");
}

// ── headers and crawler files
{
  const r = await fetch(BASE + "/");
  await r.body?.cancel();
  const need = ["content-security-policy", "x-frame-options", "x-content-type-options", "referrer-policy",
                "permissions-policy", "cross-origin-opener-policy"];
  if (BASE.startsWith("https:")) need.push("strict-transport-security");
  for (const h of need) if (!r.headers.get(h)) fail(`/ is missing the ${h} header`);
}
for (const [p, type] of [["/robots.txt", "text/plain"], ["/llms.txt", "text/plain"], ["/llms-full.txt", "text/plain"],
                         ["/sitemap.xml", "xml"], ["/site.webmanifest", "manifest+json"], ["/search-index.json", "json"]]) {
  const r = await fetch(BASE + p);
  const body = await r.text();
  if (r.status !== 200 || !(r.headers.get("content-type") || "").includes(type)) fail(`${p} answered ${r.status} ${r.headers.get("content-type")}`);
  if (p === "/robots.txt" && !body.includes(`Sitemap: ${PROD}/sitemap.xml`)) fail("robots.txt does not point at the sitemap");
}

// ── sources stay in the repository: probe one real file inside every ignored path
const firstFile = (dir) => {
  const names = readdirSync(dir).filter((n) => !n.startsWith(".") && n !== "__pycache__").sort();
  for (const n of names) if (statSync(join(dir, n)).isFile()) return join(dir, n);
  for (const n of names) { const f = firstFile(join(dir, n)); if (f) return f; }
  return null;
};
const ignored = local(".vercelignore").split("\n").map((l) => l.trim()).filter((l) => l && !l.startsWith("#"));
const probes = ignored.map((g) => {
  if (!g.endsWith("/")) return g;
  try { const f = firstFile(join(ROOT, g)); return f && "/" + f.slice(ROOT.length + 1).split(sep).join("/"); }
  catch { return null; }
}).filter(Boolean);
await pool(probes, 6, async (p) => {
  const { r } = await follow(BASE + p);
  await r.body?.cancel();
  if (r.status !== 404) fail(`${p} can be downloaded (${r.status})`);
});

console.log(`smoke ${BASE}: ${locs.length} pages, ${ogs.size} social images, ${redirects.length} redirects, ` +
            `${probes.length} private paths probed, ${fails.length} failures`);
for (const f of fails) console.log("  FAIL", f);
process.exit(fails.length ? 1 : 0);
