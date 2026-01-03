/** @type {import('next').NextConfig} */
const nextConfig = {
  reactStrictMode: true,
  poweredByHeader: false,
  typedRoutes: true,
  experimental: {
    turbopack: {
      root: '/mnt/e/giaic/learning/spec_kit_plus/todo_correct/frontend',
    },
  },
}

module.exports = nextConfig
