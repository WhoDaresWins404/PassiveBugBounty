/** @type {import('next').NextConfig} */
const nextConfig = {
  reactStrictMode: true,
  env: {
    NEXT_PUBLIC_GRAPHQL_ENDPOINT: process.env.GRAPHQL_ENDPOINT || 'http://localhost:5000/graphql',
  },
};

module.exports = nextConfig;
