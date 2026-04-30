# The Mirror

A personal notebook by Janhavi Dadhania, published at **[concavemirror.to](https://concavemirror.to)**.

> *World today is loud. Let's write it down.*

The Mirror collects long-form writing on AI architecture (agents, context windows, distributed coordination), reading notes, mathematical models of civilizational dynamics, and the occasional fantasy piece (e.g. how to send a small satellite to the Moon).

---

## What's on the site

| Section | URL | What lives there |
|---|---|---|
| Home | `/` | Hero, embedded video, social row, manually pinned featured posts |
| Blog | `/blog/` | Long-form essays |
| Research | `/research/` | Pieces grounded in math, papers, proof |
| Data | `/data/` | Numbers, charts, the maps behind them |
| Fantasy | `/fantasy/` | Loose threads, dreams, what-ifs |
| Tools | `/tools/` | Things made or used |
| Me | `/me/` | About |
| Kindle | `/kindle/` | Raw text dumps for offline reading on Kindle |

## Tech

Static site built with [Astro](https://astro.build). Content authored in MDX with typed (zod) schemas, scoped Astro components, KaTeX for math posts, self-hosted Apfel Grotezk + EB Garamond + Lora + Dancing Script. Hosted on GitHub Pages with a custom domain via `public/CNAME`.

## Repo structure

```
src/
├── content/            # posts (one folder per collection)
│   ├── config.ts       # zod schemas
│   ├── blog/*.mdx
│   ├── research/*.{mdx,md}
│   ├── data/*.mdx
│   ├── fantasy/*.md
│   └── tools/*.mdx
├── site.config.ts      # featured posts, unfinished posts, social links
├── lib/
│   ├── clusters.ts     # cluster groupings shown on each index page
│   └── collections.ts  # helper for fetching published entries
├── components/         # Section, PostMeta, BackLink, UnfinishedBar, etc.
├── layouts/            # BaseLayout, PageLayout, PostLayout, IndexLayout, ComingSoonLayout
├── pages/              # routes (one file per URL; [slug].astro for dynamic)
└── styles/             # tokens.css (design tokens) + fonts.css + global.css

public/                 # static assets copied as-is to the build output
├── CNAME               # concavemirror.to
├── fonts/              # Apfel Grotezk woff2 (OFL, by Collletttivo)
├── images/             # post images grouped by slug
├── llms.txt            # LLM-readable site index
└── robots.txt          # crawler directives + sitemap pointer
```

## Develop

```bash
npm install
npm run dev      # local server at http://localhost:4321
npm run build    # build to dist/
npm run preview  # serve the production build locally
```

## Deploy

Pushed automatically by GitHub Actions on every push to `main` (`.github/workflows/deploy.yml` → `withastro/action` → `actions/deploy-pages`). Repo Pages settings must be set to source = **GitHub Actions** (one-time toggle in repo Settings → Pages).

## Editing content

- **Add a post** — drop a new `.mdx` in `src/content/<collection>/`. It appears at `/<collection>/<slug>/` automatically and shows up on the collection's index page.
- **Pin a post on the home page** — add `'<collection>/<slug>'` to `featured_slugs` in `src/site.config.ts`. Up to 8 fit in the journal block.
- **Mark a post as unfinished** — add `'<collection>/<slug>'` to `unfinished_slugs` in `src/site.config.ts`. A maroon warning bar appears at the top of the post.
- **Group posts on an index page** — edit `src/lib/clusters.ts`. Posts not in any cluster auto-fall into a synthetic `rest` cluster.
