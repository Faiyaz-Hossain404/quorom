/** @type {import('next').NextConfig} */
const nextConfig = {
  // Static export -> ./out, served by nginx (no Node runtime in prod; avoids
  // OOM on small ECS instances since the build runs locally / in CI).
  output: "export",
  images: { unoptimized: true },
};

export default nextConfig;
