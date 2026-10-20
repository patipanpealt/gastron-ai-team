import type { NextConfig } from "next";

const nextConfig: NextConfig = {
  // open the dev server from a phone on the same Wi-Fi: without this Next blocks its own scripts from other devices,
  // the page loads but never starts (no office, no characters)
  allowedDevOrigins: ["192.168.*.*", "10.*.*.*", "172.16.*.*", "*.local"],
};

export default nextConfig;
