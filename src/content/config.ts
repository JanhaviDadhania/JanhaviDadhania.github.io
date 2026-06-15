import { defineCollection, z } from 'astro:content';

// Shared schema for long-form post collections (blog, research, data, fantasy).
// Today they share this schema. When research diverges later, replace its
// definition below with `postSchema.extend({ ... })` — only this file changes.
const postSchema = z.object({
  title: z.string(),
  date: z.coerce.date(),
  slug: z.string().optional(),
  tags: z.array(z.string()).max(5).default([]),
  summary: z.string().optional(),
  cover_image: z.string().optional(),
  // Optional list of image paths rendered as a fixed-position right column
  // at ~30% viewport width on the post page. Experimental — first used on
  // /blog/leaflet-my-autoresearcher/ as an alternative to a bg collage.
  side_images: z.array(z.string()).optional(),
  draft: z.boolean().default(false),
  meta: z.object({
    is_finished: z.boolean(),
    opinion_strength: z.number().int().min(0).max(10),
    evidence_strength: z.number().int().min(0).max(10),
  }),
});

const blog = defineCollection({ type: 'content', schema: postSchema });
const research = defineCollection({ type: 'content', schema: postSchema });
const data = defineCollection({ type: 'content', schema: postSchema });

// Fantasy diverges: entries may be pure external links (e.g. the novel wiki
// at novel.concavemirror.to). Link entries appear on the index but build no
// internal page.
const fantasy = defineCollection({
  type: 'content',
  schema: postSchema.extend({ link: z.string().url().optional() }),
});

// Tools have their own schema: plain-text + images, no opinion/evidence meta,
// optional external "visit" link, and a category label.
const toolSchema = z.object({
  title: z.string(),
  date: z.coerce.date(),
  summary: z.string().optional(),
  category: z.string(),                // e.g. 'agent', 'robot', 'intelligent app', 'workflow'
  link: z.string().url().optional(),   // external URL surfaced as "Visit ↗"
  draft: z.boolean().default(false),
});
const tools = defineCollection({ type: 'content', schema: toolSchema });

export const collections = { blog, research, data, fantasy, tools };
