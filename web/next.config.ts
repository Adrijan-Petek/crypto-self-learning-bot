import type { NextConfig } from "next";
import path from "node:path";

const isGithubPages = process.env.GITHUB_PAGES === "true";

const nextConfig: NextConfig = {
  output: "export",
  outputFileTracingRoot: path.join(__dirname, ".."),
  basePath: isGithubPages ? "/crypto-self-learning-bot" : undefined,
  assetPrefix: isGithubPages ? "/crypto-self-learning-bot/" : undefined,
  trailingSlash: true,
};

export default nextConfig;
