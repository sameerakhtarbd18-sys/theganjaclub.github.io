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
    author: z.string().default("The Ganja Club"),
    category: z.enum(["news", "guide", "review"]).default("news"),
    tags: z.array(z.string()).default(["uncategorized"]),
    sources: z.array(z.string()).optional(),
  }),
});

export const collections = { posts };
