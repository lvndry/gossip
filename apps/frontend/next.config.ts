import type { NextConfig } from "next";

const nextConfig: NextConfig = {
  images: {
    remotePatterns: [
      {
        protocol: 'https',
        hostname: '**.public.fr',
      },
      {
        protocol: 'https',
        hostname: 'public.fr',
      },
      {
        protocol: 'https',
        hostname: '**.vsd.fr',
      },
      {
        protocol: 'https',
        hostname: 'vsd.fr',
      },
    ],
  },
};

export default nextConfig;
