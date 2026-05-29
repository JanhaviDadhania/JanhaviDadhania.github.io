// Site-wide config. Edit values here to change content surfaced on home and in nav.

export const site = {
  title: 'The Mirror',
  tagline: "World today is loud. Let's hold some of it still.",
  subtagline: 'come, know it with me.',

  // Items featured on the homepage's journal lines, in display order.
  // Each entry is '<collection>/<slug>' (e.g. 'blog/foo', 'tools/bismuth').
  // Up to 8 fit in the journal block — anything beyond that is silently
  // ignored. Slugs that don't match a published entry are silently dropped.
  featured: [
    'tools/robot-io',
    'blog/if-plato-had-notebooklm',
    'tools/bismuth',
    'tools/seldon',
    'blog/zoo-animals-and-context-windows',
  ] as string[],

  // Posts that show the "this writing is not finished yet" warning bar
  // at the top. Add a slug to flag a post as unfinished; remove to hide
  // the bar. Format: '<collection>/<slug>'.
  unfinished_slugs: [
    'blog/the-map-of-the-agent-universe',
    'blog/how-i-organise-my-agents',
    'research/seldon-framework',
    'research/ai-neuroscience',
    'research/consciousness',
    'data/areas-of-ai',
    'fantasy/me-and-moon',
  ] as string[],

  // External subscribe URL (homepage button).
  subscribe_url: 'https://janhavidadhania.substack.com/subscribe',

  // Embedded video on home (Google Drive preview URL or any iframe-embeddable URL).
  hero_video_url: 'https://drive.google.com/file/d/1KjM9wwvNOyKcFdAgj0BHfsuz7EfqJGJ-/preview',

  social: {
    substack: 'https://janhavidadhania.substack.com',
    twitter: 'https://x.com/DadhaniaJanhavi',
    linkedin: 'https://www.linkedin.com/in/janhavi-dadhania-485385166/',
  },

  // Order of top-level page links displayed below socials on home and in nav.
  page_nav: [
    { label: 'Research', href: '/research/' },
    { label: 'Data', href: '/data/' },
    { label: 'Blog', href: '/blog/' },
    { label: 'Tools', href: '/tools/' },
    { label: 'Fantasy', href: '/fantasy/' },
    { label: 'Me', href: '/me/' },
  ],
} as const;
