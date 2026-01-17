/** @type {import('next').NextConfig} */
const nextConfig = {
  reactStrictMode: true,
  swcMinify: true,
  output: 'standalone',

  // Disable x-powered-by header
  poweredByHeader: false,

  // Configure image domains if needed
  images: {
    domains: [],
  },

  // Environment variables
  env: {
    NEXT_PUBLIC_API_URL: process.env.NEXT_PUBLIC_API_URL || 'http://localhost:8004',
  },
}

module.exports = nextConfig
