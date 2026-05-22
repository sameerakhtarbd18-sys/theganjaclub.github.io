import { defineConfig } from "astro/config";

export default defineConfig({
  output: "static",
  site: "https://theganjaclub.netlify.app",
  build: {
    assets: "assets",
  },
});
