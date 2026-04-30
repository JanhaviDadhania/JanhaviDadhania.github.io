/*
 * Cluster config for collection index pages.
 *
 * Each collection's `clusters` array defines spatial groupings on the index
 * page (clusters are arrayed left-to-right; slugs within a cluster stack
 * top-to-bottom). Posts not listed in any cluster auto-fall into a synthetic
 * "rest" cluster appended at the end — so adding a post never breaks the
 * build, you just won't have placed it deliberately yet.
 *
 * To re-group: edit the arrays below. No frontmatter changes, no schema
 * changes. Slugs are post filenames without the .mdx/.md extension.
 */

import type { CollectionEntry } from 'astro:content';

export type ClusterCollection = 'blog' | 'research' | 'data' | 'fantasy' | 'tools';

export interface ClusterDef {
  /** Internal id — used as a stable React-style key, not displayed. */
  id: string;
  /** Slugs of posts belonging to this cluster, in display order. */
  slugs: string[];
}

export const clusters: Record<ClusterCollection, ClusterDef[]> = {
  blog: [
    {
      id: 'left',
      slugs: [
        'the-next-ai-wave-computers-get-bodies',
        'redesign-of-superhuman-workflows-now-that-ai-is-here',
        'the-map-of-the-agent-universe',
      ],
    },
    {
      id: 'right',
      slugs: [
        'my-thinking-assistants-design',
        'zoo-animals-and-context-windows',
      ],
    },
  ],

  // No deliberate clustering yet — everything falls into "rest".
  // Add cluster definitions here when you want explicit grouping.
  research: [],
  data: [],
  fantasy: [],
  tools: [],
};

/* ─── Grouping helper ─────────────────────────────────────────────────── */

export interface ClusteredGroup<T> {
  id: string;
  posts: T[];
}

/**
 * Group a collection's posts into the clusters defined above.
 * Untagged posts fall into a synthetic "rest" cluster at the end.
 */
export function groupIntoClusters<T extends CollectionEntry<ClusterCollection>>(
  collection: ClusterCollection,
  posts: T[],
): ClusteredGroup<T>[] {
  const defs = clusters[collection] ?? [];
  const bySlug = new Map(posts.map((p) => [p.slug, p]));
  const used = new Set<string>();

  const groups: ClusteredGroup<T>[] = defs.map((def) => {
    const groupPosts: T[] = [];
    for (const slug of def.slugs) {
      const post = bySlug.get(slug);
      if (post) {
        groupPosts.push(post);
        used.add(slug);
      }
    }
    return { id: def.id, posts: groupPosts };
  });

  const rest = posts.filter((p) => !used.has(p.slug));
  if (rest.length > 0) {
    groups.push({ id: 'rest', posts: rest });
  }

  return groups.filter((g) => g.posts.length > 0);
}
