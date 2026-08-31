# SEO implementation

Everything below is live unless marked **NOT LIVE**. Rebuild after any edit:

```bash
python3 scripts/build_site.py
```

## Fill these in before launch

`scripts/site_content.py` holds every business fact in one place. These are
placeholders and they leak into canonicals, schema, the sitemap and llms.txt:

| Field | Current | Why it matters |
|---|---|---|
| `ORIGIN` | `https://toronto-millworks.vercel.app` | Live Vercel origin. Point a custom domain at Vercel, change this one line, rebuild |
| `email` | `hello@torontomillworks.ca` | Guessed. Used in Organization schema and every CTA |
| `street`, `postal` | empty | Google needs a street address to rank a LocalBusiness in the map pack |
| `phone` | empty | Left empty on purpose. An invented number could reach a real person |
| `founded` | empty | Feeds `foundingDate` |
| `same_as` | empty | Real profile URLs. Emitted only when filled, so no dead links ship |

## Live

| Item | Where |
|---|---|
| XML sitemap with `lastmod` | `sitemap.xml`, 19 URLs |
| `image:image` sitemap data | `sitemap.xml`, 8 image entries on the key pages |
| robots.txt | `robots.txt`, sitemap declared, AI crawlers allowed |
| Canonical tags | every page, self referencing absolute URL |
| llms.txt / llms-full.txt | root, full copy of every service, area and FAQ |
| Organization schema | `#organization`, on every page |
| LocalBusiness schema | same node, typed `HomeAndConstructionBusiness` + `LocalBusiness`, with `geo` and `areaServed` |
| WebSite schema | `#website`, with `publisher` linked to the org |
| SearchAction | points at the real working `/search/` page |
| WebPage schema | per page, typed `CollectionPage` / `AboutPage` / `ContactPage` / `FAQPage` as appropriate |
| BreadcrumbList schema | per page, matching the visible breadcrumb trail |
| Service schema | 5 service pages, each with `hasOfferCatalog` |
| FAQPage schema | home, services, about, contact, FAQ, guide, service pages |
| Article schema | `/guides/how-custom-millwork-is-made/` |
| Open Graph | 10 tags per page including `og:locale` and image dimensions |
| Twitter cards | 5 tags per page, `summary_large_image` |
| Titles | unique per page, all 65 chars or under |
| Meta descriptions | unique per page, all 110 to 170 chars |
| H1 / H2 / H3 | exactly one H1 per page, headings in order |
| Image alt text | descriptive and keyword bearing on every image |
| Image filenames | `toronto-custom-millwork-coffered-ceiling-*`, `toronto-custom-cabinetry-wall-panelling-*`, frames under `assets/millwork-fit-out-sequence/` |
| URL slugs | `/services/custom-kitchens/`, `/service-areas/etobicoke/` and so on |
| Internal linking | breadcrumbs, service cross links, footer index, area to service links |
| Breadcrumb navigation | visible on every page below home |
| hreflang | `en-ca` plus `x-default`, self referencing |
| `<html lang>` | `en-CA` |
| noindex | `/search/` and `404.html` only |
| max-image-preview / max-snippet / max-video-preview | in the robots meta on every indexable page |
| 404 page | `404.html`, real 404 status via the host configs below |
| 301 redirects | `.htaccess`, `netlify.toml`, `vercel.json`, `_redirects` |
| Semantic HTML5 | `header` / `nav` / `main` / `section` / `footer` / `ol` / `dl` |
| FAQ content blocks | visible copy, not schema only |
| Service area pages | 6 GTA pages plus a hub |

Deploy the config that matches your host. All four set the 404 status, force
https, force one canonical host and add the trailing slash so URLs match the
canonicals exactly.

## Not applicable

- **rel="prev" / rel="next"**, nothing is paginated. Google also stopped using
  these as an indexing signal in 2019. Add them only if a paginated archive
  appears later.
- **hreflang beyond en-CA**, single language site. The self referencing tag
  plus `x-default` is the correct implementation for that case.

## NOT LIVE, and why

These four need real world data. Publishing them empty or invented would be
worse than leaving them out: fake `Review` and `AggregateRating` markup is a
Google structured data policy violation and can earn a manual action.

### Person schema
Needs a real name. Add the founder or lead to `site_content.py` as
`SITE["person"]`, then this node into the graph:

```json
{
  "@type": "Person",
  "@id": "https://toronto-millworks.vercel.app/#founder",
  "name": "FULL NAME",
  "jobTitle": "Founder",
  "worksFor": { "@id": "https://toronto-millworks.vercel.app/#organization" },
  "sameAs": ["https://www.linkedin.com/in/PROFILE"]
}
```
Then add `"founder": {"@id": ".../#founder"}` to the Organization node.

### Review and AggregateRating
Only add once you have real, attributable reviews. Mirror what is publicly on
your Google Business Profile:

```json
{
  "@type": "AggregateRating",
  "itemReviewed": { "@id": "https://toronto-millworks.vercel.app/#organization" },
  "ratingValue": "4.9",
  "reviewCount": "37",
  "bestRating": "5"
}
```

### Product schema
`Service` is the correct type for bespoke millwork and is already live. Use
`Product` only if you start selling a defined item with a price and
availability, for example a standard vanity or a stock shelving unit.

## Local SEO next steps

Schema alone will not win the map pack. Claim the Google Business Profile, get
the street address into `site_content.py`, and keep the name, address and phone
identical everywhere they appear.
