/** @type {import('next').NextConfig} */
const nextConfig = {
  reactStrictMode: true,
  
  // غیرفعال کردن Turbopack
  experimental: {
    turbo: undefined
  },
  
  transpilePackages: ["@nowex/ui", "@nowex/api", "@nowex/types"],
  
  async rewrites() {
    return [
      {
        source: "/api/:path*",
        destination: "http://localhost:8000/:path*",
      },
    ]
  },
}

module.exports = nextConfig