# Toronto Millworks · build specification

This is the contract the site is built and checked against. `scripts/audit.py`
enforces the checkable parts and fails the build when any of them break.

## 1. Architecture

| Layer | Where | Notes |
|---|---|---|
| Content model | `scripts/site_content.py`, `scripts/locations.py`, `scripts/guides.py` | Single source of truth for every fact, page and line of copy |
| Generator | `scripts/build_site.py` | Static HTML, sitemap, robots, llms files, redirects, headers |
| Drawings | `scripts/drawings.py` | Inline SVG shop drawings, one per service and process stage |
| Maps | `scripts/maps.py` + `scripts/data/lakes_km.json` | Service radius map and one unique map per location page |
| Imagery | `scripts/build_library.py` | Art directed crops, wide and tall, with blur-up placeholders |
| Social cards | `scripts/og_cards.mjs` | 1200x630 JPEG per page, rendered by headless Chrome |
| Quality gate | `scripts/audit.py` | SEO, accessibility, links, security and copy checks |
| Deploy check | `scripts/smoke.mjs` | Crawls the live site: status codes, canonicals, redirects, 404, headers, private files |
| Styles | `css/src/*.css` built into `css/style.css` | One sheet, tokens first, components in page order |
| Behaviour | `js/main.js`, `js/scenes.js` | Progressive enhancement only; Three.js loaded on demand |
| Hosting | Vercel, from `main` | `vercel.json` carries redirects and security headers |

No framework, no bundler, no runtime dependency other than self-hosted GSAP and
Three.js. Every page is complete HTML before any script runs.

## 2. Design system

- **Palette** paper `#FFFFFF`, paper-2 `#F7F5F1`, ink `#17140F`, ink-70, ink-45,
  brass `#C08A3C`, deep brass footer. Nothing else is introduced.
- **Type** Instrument Sans, self-hosted variable woff2. Display at weight 400
  with negative tracking; UI at 500 to 600.
- **Shape** pill chips with a brass dot, one corner radius token, hairlines.
- **Signature** hairline shop drawings: the way a millwork job really starts.
  They stand in where photography does not exist yet and draw themselves in.
- **Motion** one easing family. Reveals are once only, transforms and opacity
  only, and everything collapses under `prefers-reduced-motion`.
- **Never** numbered lists of the 01 / 02 kind, decorative rules that carry no
  structure, gradients for their own sake, glass beyond the hero chip, cards
  inside cards.
- **Untouchable** the scroll-scrubbed fit-out sequence on the home page.

## 3. Pages

| Type | Count | URL |
|---|---|---|
| Home | 1 | `/` |
| Services hub + services | 1 + 7 | `/services/`, `/services/{slug}/` |
| Service areas hub + locations | 1 + 50 | `/service-areas/`, `/service-areas/{slug}/` |
| Guides hub + guides | 1 + 6 | `/guides/`, `/guides/{slug}/` |
| Projects, About, Contact, FAQ, Privacy | 5 | `/{slug}/` |
| Search (noindex) | 1 | `/search/` |
| 404 (noindex, real 404 status) | 1 | any missing path |

Location pages cover every major municipality within 120 km straight-line of
the shop at 2585 Drew Rd, Mississauga. Each carries its own map, distance,
neighbourhoods, local copy and nearest-neighbour links, so none is a doorway.

## 4. Acceptance criteria (enforced by `scripts/audit.py`)

1. Every indexable page has a unique `<title>` of 30 to 60 characters.
2. Every indexable page has a unique meta description of 120 to 160 characters.
3. Exactly one `<h1>` per page; headings never skip a level.
4. Self-referencing absolute canonical on every page except the 404, which is
   served at any address and declares none; noindex pages excluded from the sitemap.
5. Open Graph and Twitter tags complete, with a 1200x630 JPEG that exists.
6. Every JSON-LD block parses; required types present per page type.
7. Every internal link and asset reference resolves to a built file.
8. Every `<img>` has alt text and intrinsic width and height.
9. External links carry `rel="noopener"`; no `href="#"`; no inline handlers.
10. No em dashes, placeholder text, TODOs, lorem ipsum or invented statistics.
11. Sitemap, robots.txt, llms.txt and llms-full.txt exist and agree with pages.
12. Security headers present in `vercel.json`: CSP, HSTS, nosniff,
    frame-ancestors, referrer and permissions policies.
13. Location pages: unique copy per page, distance under 120 km.
14. Only the generated site is deployed: every top-level path is site output or
    listed in `seo.PRIVATE`, which writes `.vercelignore` and the matching Apache
    and Netlify rules. `scripts/smoke.mjs` confirms it on the live site.

## 5. Facts that must come from the business

These are deliberately left empty rather than invented. The generator omits
anything blank instead of guessing.

- Phone number, founding year, social profiles, real reviews.
- The enquiry email is unconfirmed and must be checked before launch.
- A form endpoint (`FORM_ENDPOINT` in `site_content.py`); until it is set the
  quote form composes an email in the visitor's mail app.
