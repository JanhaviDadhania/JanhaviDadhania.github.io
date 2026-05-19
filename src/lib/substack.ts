export interface SubstackPost {
  title: string;
  link: string;
  pubDate: Date;
  description: string;
}

const FEED_URL = 'https://janhavidadhania.substack.com/feed';

function decodeEntities(s: string): string {
  return s
    .replace(/&amp;/g, '&')
    .replace(/&lt;/g, '<')
    .replace(/&gt;/g, '>')
    .replace(/&quot;/g, '"')
    .replace(/&#039;/g, "'")
    .replace(/&apos;/g, "'");
}

function pick(block: string, tag: string): string {
  const re = new RegExp(`<${tag}[^>]*>([\\s\\S]*?)</${tag}>`, 'i');
  const m = block.match(re);
  if (!m) return '';
  let v = m[1].trim();
  const cdata = v.match(/^<!\[CDATA\[([\s\S]*?)\]\]>$/);
  if (cdata) v = cdata[1].trim();
  return decodeEntities(v);
}

export async function fetchSubstackPosts(limit = 20): Promise<SubstackPost[]> {
  try {
    const res = await fetch(FEED_URL, {
      headers: { 'User-Agent': 'concavemirror-build' },
    });
    if (!res.ok) return [];
    const xml = await res.text();
    const items = xml.match(/<item>[\s\S]*?<\/item>/g) ?? [];
    const posts: SubstackPost[] = items.map((block) => ({
      title: pick(block, 'title'),
      link: pick(block, 'link'),
      pubDate: new Date(pick(block, 'pubDate')),
      description: pick(block, 'description'),
    }));
    return posts
      .filter((p) => p.title && p.link)
      .sort((a, b) => b.pubDate.getTime() - a.pubDate.getTime())
      .slice(0, limit);
  } catch {
    return [];
  }
}
