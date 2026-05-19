#!/usr/bin/env node
// Fetches the Substack RSS feed and writes a static JSON snapshot at
// src/data/substack.json. Run locally (`npm run sync-substack`) whenever
// you want the home page to pick up new Substack posts; commit the file.
// Substack 403s GitHub Actions IPs, so we cannot fetch at build time.

import { writeFile, mkdir } from 'node:fs/promises';
import { dirname, resolve } from 'node:path';
import { fileURLToPath } from 'node:url';

const FEED_URL = 'https://janhavidadhania.substack.com/feed';
const LIMIT = 20;

const __dirname = dirname(fileURLToPath(import.meta.url));
const OUT = resolve(__dirname, '../src/data/substack.json');

function pick(block, tag) {
  const re = new RegExp(`<${tag}[^>]*>([\\s\\S]*?)</${tag}>`, 'i');
  const m = block.match(re);
  if (!m) return '';
  let v = m[1].trim();
  const cdata = v.match(/^<!\[CDATA\[([\s\S]*?)\]\]>$/);
  if (cdata) v = cdata[1].trim();
  return v
    .replace(/&amp;/g, '&')
    .replace(/&lt;/g, '<')
    .replace(/&gt;/g, '>')
    .replace(/&quot;/g, '"')
    .replace(/&#039;/g, "'")
    .replace(/&apos;/g, "'");
}

const res = await fetch(FEED_URL, {
  headers: {
    'User-Agent':
      'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/124.0.0.0 Safari/537.36',
    Accept: 'application/rss+xml, application/xml;q=0.9, */*;q=0.8',
  },
});
if (!res.ok) {
  console.error(`Substack feed fetch failed: ${res.status} ${res.statusText}`);
  process.exit(1);
}

const xml = await res.text();
const blocks = xml.match(/<item>[\s\S]*?<\/item>/g) ?? [];
const posts = blocks
  .map((b) => ({
    title: pick(b, 'title'),
    link: pick(b, 'link'),
    pubDate: new Date(pick(b, 'pubDate')).toISOString(),
    description: pick(b, 'description'),
  }))
  .filter((p) => p.title && p.link)
  .sort((a, b) => new Date(b.pubDate).getTime() - new Date(a.pubDate).getTime())
  .slice(0, LIMIT);

await mkdir(dirname(OUT), { recursive: true });
await writeFile(OUT, JSON.stringify({ fetchedAt: new Date().toISOString(), posts }, null, 2) + '\n');
console.log(`Wrote ${posts.length} posts to ${OUT}`);
