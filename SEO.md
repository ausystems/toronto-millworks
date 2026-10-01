# SEO status

Every item on the brief, where it lives, and how it is verified. Items marked
"audit" are checked by `scripts/audit.py` on every build and in CI.

| # | Item | Status | Where / how verified |
|---|---|---|---|
| 1 | SEO title tags | Done | Unique, 30 to 60 characters on all 72 indexable pages (audit) |
| 2 | Meta descriptions | Done | Unique, 120 to 160 characters on every indexable page (audit) |
| 3 | One primary H1 per page | Done | Exactly one `<h1>` on all 74 pages (audit) |
| 4 | H2 and H3 hierarchy | Done | Sections open with H2, items use H3, no skipped levels (audit) |
| 5 | Keyword-optimised copy | Done | Primary terms in titles, H1s and opening copy; service and town pairs in anchors |
| 6 | Search intent | Done | Services and towns are transactional with a quote path; guides are informational |
| 7 | Clean URLs | Done | Lowercase, hyphenated, trailing slash; `.html` and missing slashes redirect |
| 8 | Canonical tags | Done | Self-referencing and absolute on every page (audit) |
| 9 | Schema markup | Done | Organization + LocalBusiness + HomeAndConstructionBusiness, WebSite, WebPage types, BreadcrumbList, Service (GeoCircle area), FAQPage, Article, ItemList; all parse (audit) |
| 10 | XML sitemap | Done | 72 URLs with lastmod and image entries for the images each page uses (audit) |
| 11 | robots.txt | Done | Everything crawlable, AI crawlers welcomed, sitemap declared (audit) |
| 12 | Internal linking | Done | Services menu, footer index, hubs, related services, related guides, nearest towns, localised service links |
| 13 | Descriptive anchors | Done | "Custom kitchens in Oakville", "Restaurant and bar millwork"; no "click here" |
| 14 | Breadcrumbs | Done | Visible on every inner page, mirrored in BreadcrumbList (audit) |
| 15 | Semantic HTML | Done | header, nav, main, section, article, aside, footer, address, figure, dl, details |
| 16 | Open Graph | Done | Complete set with a 1200x630 JPEG card per page (audit) |
| 17 | Twitter cards | Done | `summary_large_image` with image and alt (audit) |
| 18 | SEO-friendly 404 | Done | Real 404 status, noindex, search box and links to every section |
| 19 | 301 redirects | Done | Legacy `.html` paths, `/home`, `/areas`, `/quote`, `/privacy` (vercel.json, plus Netlify and Apache equivalents) |
| 20 | Core Web Vitals | Done | Self-hosted fonts with preload, hero preload, intrinsic image sizes, blur-up placeholders, deferred scripts, Three.js on demand |
| 21 | Mobile first | Done | Phone layouts designed separately; full-height menu, quote dock, thumbnailed indexes |
| 22 | Page speed | Done | Pages 4 to 27 KB gzipped, CSS 21 KB, site script 12 KB, long-lived caching on assets |
| 23 | Crawlability and indexability | Done | All content in HTML before script, every link a real `<a href>`, broken links fail the audit |
| 24 | Duplicate content | Done | Canonicals, one host, unique titles and descriptions, unique copy and map per location (audit) |
| 25 | Local SEO signals | Done | Full NAP in footer, schema, contact page and map; geo meta; GeoCircle service area; 50 location pages |
| 26 | llms.txt | Done | `/llms.txt` and `/llms-full.txt` with every service, guide and town (audit) |
| 27 | Creative 404 | Done | A panelled wall in raking light with one panel missing, rendered in Three.js; drawn fallback |
| 28 | Service pages | Done | Seven, each with scope, process, materials, local links, five questions and related guides |
| 29 | Location pages within 120 km | Done | Fifty municipalities, each measured from the shop, each with its own map and copy |

## Deliberately not published

| Schema | Why |
|---|---|
| Review, AggregateRating | No real reviews yet. Fabricated ratings break Google's guidelines. |
| telephone, openingHours | Not supplied. The generator adds them the moment they exist. |
| sameAs | No profile URLs yet. Add the Google Business Profile first. |

## After launch

1. Verify the domain in Google Search Console and Bing Webmaster Tools; submit `/sitemap.xml`.
2. Create or claim the Google Business Profile at 2585 Drew Rd Unit 7 with the same name,
   address and site URL, then add it to `same_as`.
3. Ask finished clients for Google reviews; mark them up only once they are real.
4. If a custom domain is added, change `ORIGIN` in `site_content.py` and rebuild.
