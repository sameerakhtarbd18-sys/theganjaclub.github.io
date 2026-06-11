import { defineConfig } from "astro/config";
import sitemap from "@astrojs/sitemap";

export default defineConfig({
  output: "static",
  site: "https://theganjaclub.netlify.app",
  integrations: [sitemap()],
  build: {
    assets: "assets",
  },
});
