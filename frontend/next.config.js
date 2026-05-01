/** @type {import('next').NextConfig} */
const nextConfig = {
  transpilePackages: ["react-leaflet", "leaflet"],
  eslint: { ignoreDuringBuilds: true },
  typescript: { ignoreBuildErrors: true },
  async headers() {
    return [
      {
        source: "/manifest.json",
        headers: [{ key: "Content-Type", value: "application/manifest+json" }],
      },
    ];
  },
};

module.exports = nextConfig;
