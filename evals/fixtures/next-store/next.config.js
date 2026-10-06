/** @type {import('next').NextConfig} */
const nextConfig = {
  env: {
    INVENTORY_API_URL: process.env.INVENTORY_API_URL,
    INVENTORY_API_TOKEN: process.env.INVENTORY_API_TOKEN,
  },
  async headers() {
    return [
      {
        source: '/:path*',
        headers: [
          { key: 'X-Content-Type-Options', value: 'nosniff' },
          { key: 'Referrer-Policy', value: 'strict-origin-when-cross-origin' },
          { key: 'Content-Security-Policy', value: "frame-ancestors 'none'" },
        ],
      },
    ];
  },
};

module.exports = nextConfig;
