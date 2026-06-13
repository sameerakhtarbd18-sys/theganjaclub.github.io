import { defineConfig } from "astro/config";
import sitemap from "@astrojs/sitemap";

export default defineConfig({
  output: "static",
  // Updated for Cloudflare Pages. Change to the custom domain when one is purchased.
  site: "https://theganjaclub.co.uk",
  integrations: [sitemap()],
  build: {
    assets: "assets",
  },
});
