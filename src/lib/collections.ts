import { getCollection, type CollectionEntry } from 'astro:content';

type PostCollection = 'blog' | 'research' | 'data' | 'fantasy' | 'tools';

// Returns published (non-draft) entries from a collection, sorted newest first.
export async function getPublishedEntries<T extends PostCollection>(
  collection: T,
): Promise<CollectionEntry<T>[]> {
  const all = await getCollection(collection, ({ data }: { data: { draft?: boolean } }) => !data.draft);
  all.sort((a, b) => b.data.date.getTime() - a.data.date.getTime());
  return all as CollectionEntry<T>[];
}
