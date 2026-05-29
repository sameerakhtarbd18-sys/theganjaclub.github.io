import { defineCollection, z } from "astro:content";
import { glob } from "astro/loaders";

const posts = defineCollection({
  loader: glob({ pattern: "**/*.md", base: "./src/content/posts" }),
  schema: z.object({
    title: z.string(),
    slug: z.string(),
    date: z.string(),
    region: z.string(),
    excerpt: z.string(),
    image: z.string(),
    category: z.enum(["news", "guide"]).default("news"),
    tags: z.array(z.string()).default(["uncategorized"]),
  }),
});

export const collections = { posts };
