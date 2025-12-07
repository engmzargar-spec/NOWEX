/** @type {import('next').NextConfig} */
const nextConfig = {
  output: 'standalone',
  
  // غیرفعال کردن انواع خطاها
  typescript: {
    ignoreBuildErrors: true,
  },
  eslint: {
    ignoreDuringBuilds: true,
  },
  
  // تنظیمات packages
  transpilePackages: ['@nowex/ui', '@nowex/types', '@nowex/api'],
  
  // غیرفعال کردن image optimization
  images: {
    unoptimized: true,
  },
}

module.exports = nextConfig
