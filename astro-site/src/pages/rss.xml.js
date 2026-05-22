import rss from "@astrojs/rss";
import { getCollection } from "astro:content";

export async function GET(context) {
  const posts = await getCollection("posts");
  posts.sort((a, b) => new Date(b.data.date).getTime() - new Date(a.data.date).getTime());

  return rss({
    title: "The Ganja Club",
    description: "Medical cannabis news, policy analysis, and culture.",
    site: context.site || "https://theganjaclub.netlify.app",
    items: posts.map(post => ({
      title: post.data.title,
      description: post.data.excerpt,
      pubDate: new Date(post.data.date),
      link: `/post/${post.data.slug}`,
      categories: post.data.tags,
    })),
    customData: `<language>en-gb</language>`,
    stylesheet: "/styles/rss.xsl",
  });
}
