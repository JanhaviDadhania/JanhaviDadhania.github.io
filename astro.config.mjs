import { defineConfig, passthroughImageService } from 'astro/config';
import mdx from '@astrojs/mdx';
import sitemap from '@astrojs/sitemap';
import remarkMath from 'remark-math';
import rehypeKatex from 'rehype-katex';

// https://astro.build/config
export default defineConfig({
  site: 'https://concavemirror.to',
  integrations: [
    mdx({
      remarkPlugins: [remarkMath],
      rehypePlugins: [rehypeKatex],
    }),
    sitemap(),
  ],
  trailingSlash: 'always',
  build: {
    format: 'directory',
  },
  // Skip sharp-based image optimization — we don't need it (static blog),
  // and sharp lacks prebuilt binaries for some Node versions. Images are
  // served as-is from /public/images/.
  image: {
    service: passthroughImageService(),
  },
});
