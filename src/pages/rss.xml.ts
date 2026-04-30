import rss from '@astrojs/rss';
import type { APIContext } from 'astro';
import { site } from '@/site.config';
import { getPublishedEntries } from '@/lib/collections';

export async function GET(context: APIContext) {
  const posts = await getPublishedEntries('blog');
  return rss({
    title: site.title,
    description: site.tagline,
    site: context.site!,
    items: posts.map((post) => ({
      title: post.data.title,
      pubDate: post.data.date,
      description: post.data.summary ?? '',
      link: `/blog/${post.slug}/`,
    })),
  });
}
