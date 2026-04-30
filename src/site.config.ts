// Site-wide config. Edit values here to change content surfaced on home and in nav.

export const site = {
  title: 'The Mirror',
  tagline: "World today is loud. Let's write it down.",
  subtagline: 'come along as we document history in the making',

  // Posts featured on the homepage's journal lines, in display order.
  // Each entry is '<collection>/<slug>'. Add a slug here to surface a post
  // on the home page; remove to hide. Up to 8 fit in the journal block —
  // anything beyond that is silently ignored.
  featured_slugs: [
    'blog/zoo-animals-and-context-windows',
  ] as string[],

  // Posts that show the "this writing is not finished yet" warning bar
  // at the top. Add a slug to flag a post as unfinished; remove to hide
  // the bar. Format: '<collection>/<slug>'.
  unfinished_slugs: [
    'blog/the-next-ai-wave-computers-get-bodies',
    'blog/redesign-of-superhuman-workflows-now-that-ai-is-here',
    'blog/the-map-of-the-agent-universe',
    'blog/my-thinking-assistants-design',
    'research/are-agents-turing-machine',
    'research/seldon-framework',
    'research/ai-neuroscience',
    'data/areas-of-ai',
    'fantasy/me-and-moon',
  ] as string[],

  // External subscribe URL (homepage button).
  subscribe_url: 'https://janhavidadhania.substack.com/subscribe',

  // Embedded video on home (Google Drive preview URL or any iframe-embeddable URL).
  hero_video_url: 'https://drive.google.com/file/d/1KjM9wwvNOyKcFdAgj0BHfsuz7EfqJGJ-/preview',

  social: {
    instagram: 'https://www.instagram.com/janhavidadhania_/',
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
    { label: 'Kindle Reads', href: '/kindle/' },
  ],
} as const;
