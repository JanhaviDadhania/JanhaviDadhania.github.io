// Shared map of MDX components available to every post collection.
// Each post slug template (blog/research/data/fantasy) imports this and
// passes it to <Content components={postComponents} />, so any new
// component (Section, Quote, Excerpt, Arrow, …) is registered in one place.

import Section from '@/components/Section.astro';
import Quote from '@/components/Quote.astro';
import Excerpt from '@/components/Excerpt.astro';
import Arrow from '@/components/Arrow.astro';

export const postComponents = { Section, Quote, Excerpt, Arrow };
