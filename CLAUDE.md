# CLAUDE.md

Context for Claude / agents working on this repo.

## What this is

`concavemirror.to` — a personal static site ("The Mirror") owned by Janhavi Dadhania. Repo: `JanhaviDadhania/JanhaviDadhania.github.io`, served from a custom domain (CNAME at `public/CNAME`). Site is **always static, never backend**. Don't propose backend features, databases, server endpoints, or anything beyond what GitHub Pages can serve.

## How to work here

### Hard rules

- **Never push or merge to `main` directly.** Org-level rule. Always work on a feature branch (e.g., `astro-migration` or new ones for distinct work). The user opens and merges PRs themselves.
- **Don't restore deleted artifacts without asking.** A few files (the agent_universe `.py` scripts, CSVs in `theMirror/diary_pages/data/`, root-level `index.html`/`excerpts/`/`substack/`) were intentionally deleted. They live in git history (commit `21a1523`) — recoverable if explicitly requested.
- **Don't render tags on the UI.** The post schema has a `tags: string[]` field but the user explicitly does not want tag chips on post pages, index cards, or anywhere visible. Schema kept for possible future use; UI must stay tag-free until explicitly asked otherwise.
- **No top nav on non-home pages.** `PageNav` is rendered only inside `Hero.astro` on the home page. Index pages, post pages, `/me`, `/kindle`, etc. must not have a top nav. Every non-home page has a fixed bottom-right `BackLink`.

### User collaboration style

- The user does not write frontend code — agents do. They review and ratify, but expect the agent to make structural decisions cleanly.
- Default to **structure-first**: lock content/component shape before visual polish. The user defers detailed design until structure is verified end-to-end.
- The user prefers **planning before large changes**. Use plan mode for non-trivial restructures; for small focused edits (token tweaks, content additions), proceed directly.
- Be terse. Don't summarise after each tool call. End-of-turn summaries: 1–2 sentences max.

## Stack

- **Astro 5** + `@astrojs/mdx` + `@astrojs/sitemap` + `@astrojs/rss`
- **TypeScript** strict, zod for content schemas
- **MDX** for posts (with `<Section>` JSX components for the colored section headers)
- **KaTeX** for math posts via `remark-math` + `rehype-katex`
- **Self-hosted fonts**: Apfel Grotezk (3 weights, OFL by Collletttivo) under `public/fonts/`. Plus Google Fonts: EB Garamond, Lora, Dancing Script.
- **Sharp disabled** via `passthroughImageService()` — prebuilt sharp binaries don't exist for the user's Node 25.x. Don't try to add image optimisation that needs sharp.
- **GitHub Pages** + GitHub Actions (`withastro/action` + `actions/deploy-pages`). Repo Pages settings must be set to source = "GitHub Actions" (one-time toggle by the user, may not be set yet).

## Repo layout

```
src/
├── content/<collection>/*.{mdx,md}   # posts; collections: blog, research, data, fantasy, tools
├── content/config.ts                 # zod schemas
├── site.config.ts                    # featured_slugs, unfinished_slugs, social, hero_video_url
├── lib/clusters.ts                   # per-collection cluster groupings for index pages
├── lib/collections.ts                # getPublishedEntries helper
├── components/                       # Section, PostMeta, BackLink, UnfinishedBar, Hero, etc.
├── layouts/                          # BaseLayout, PageLayout, PostLayout, IndexLayout, ComingSoonLayout
├── pages/                            # routes (file = URL)
├── styles/tokens.css                 # design tokens (colors, fonts, spacing)
└── styles/{global,fonts}.css

public/
├── CNAME                             # concavemirror.to
├── fonts/                            # Apfel Grotezk woff2
├── images/<collection>/<slug>/...    # post-grouped images
├── llms.txt                          # MANUAL — see below
└── robots.txt                        # MANUAL — see below
```

## Layout responsibilities

- `BaseLayout` — `<head>`, fonts, global CSS. Used by every page.
- `PostLayout` — long-form posts. Full-bleed graph paper background, title-left + meta-right with vertical rule, horizontal rule below, per-post random L/R margins (build-time `Math.random()`), `UnfinishedBar` above title when slug is in `site.config.ts` `unfinished_slugs`.
- `IndexLayout` — collection index pages. Full-viewport dotted grid, big bottom-left collection title in Apfel Grotezk, post clusters at top with zigzag offset. Empty clusters → just the title.
- `PageLayout` — generic single pages (`/me`, `/kindle`, `/coming-soon`). Container, no top header. Use this for non-collection pages that don't need the IndexLayout's big-title treatment.
- `ComingSoonLayout` — placeholder for `/coming-soon` and `/404`.

## Conventions

- **Posts share a schema** (`postSchema` in `content/config.ts`) across blog/research/data/fantasy. Tools has its own simpler schema. When research/another collection needs to diverge, fork its schema in `content/config.ts` — don't widen the shared schema.
- **`draft: true` on a post hides it** from indexes, home, and RSS but the post page still builds. Migrated content defaults to `draft: true`; user flips to `false` after review.
- **Featured posts on home are explicit, not auto.** Edit `featured_slugs` in `site.config.ts`. Up to 8 fit on the journal block.
- **Unfinished posts show a maroon warning bar** at the top. Edit `unfinished_slugs` in `site.config.ts`.
- **Index page clustering is explicit.** Edit `lib/clusters.ts`. Posts not in any cluster auto-fall into a synthetic `rest` cluster — won't disappear, but won't be deliberately placed either.
- **Per-post random margins are intentional.** Don't replace with fixed values without asking.
- **MDX + JSX + LaTeX math conflicts.** `remark-math` doesn't always preprocess `$...$` inside JSX children. If a heavily-math post can't compile inside `<Section>` blocks, fall back to `.md` (plain markdown) with `## headings` — `seldon-framework.md` is the precedent. Don't fight the parser.

## Manual updates that are easy to forget

- **`public/llms.txt`** — static llmstxt.org-format index of the site's posts. **Must be updated by hand** when posts are added, removed, renamed, or get a new summary. Currently lists every published post. Could be auto-generated from content collections at build time as a follow-up; not done yet.
- **`public/robots.txt`** — allow-all + sitemap pointer. Rarely needs updating, but if you ever add paths that should be hidden, edit here.
- **`featured_slugs` and `unfinished_slugs`** in `site.config.ts` — silently drop slugs that don't match a published post (intentional, keeps the home resilient). If a featured post seems missing, check the slug + that the post is `draft: false`.
- **Sitemap is auto-generated** by `@astrojs/sitemap` — no manual update needed there.
- **Pages settings on GitHub** — one-time switch from "Deploy from branch" to "GitHub Actions" mode. Without this, the workflow runs but doesn't actually deploy.

## Commands

```bash
npm install
npm run dev      # http://localhost:4321
npm run build    # writes to dist/
npm run preview  # serves the production build locally
```

## Verification before claiming "done"

1. `npm run build` exits 0 (warnings about empty collections like `tools` are fine).
2. Visit changed pages locally with `npm run dev`. The user has explicitly said: type-checking and tests verify code correctness, NOT feature correctness — actually open the page in a browser before claiming a UI change works.
3. For featured/unfinished/cluster changes: spot-check the affected pages render the expected content.
4. Don't push to `main`.
