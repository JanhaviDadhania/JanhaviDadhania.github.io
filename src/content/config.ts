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
  draft: z.boolean().default(false),
  meta: z.object({
    on_coffee: z.boolean(),
    is_finished: z.boolean(),
    opinion_strength: z.number().int().min(0).max(10),
    evidence_strength: z.number().int().min(0).max(10),
  }),
});

const blog = defineCollection({ type: 'content', schema: postSchema });
const research = defineCollection({ type: 'content', schema: postSchema });
const data = defineCollection({ type: 'content', schema: postSchema });
const fantasy = defineCollection({ type: 'content', schema: postSchema });

// Tools have a simpler shape: a card with title, description, optional image(s)
// and an external link.
const tools = defineCollection({
  type: 'content',
  schema: z.object({
    title: z.string(),
    date: z.coerce.date(),
    summary: z.string(),
    images: z.array(z.string()).optional(),
    link: z.string().url().optional(),
    draft: z.boolean().default(false),
  }),
});

export const collections = { blog, research, data, fantasy, tools };
