import type { Metadata } from "next";
import { IBM_Plex_Sans_Thai, Pixelify_Sans } from "next/font/google";
import "./globals.css";

const thai = IBM_Plex_Sans_Thai({ subsets: ["thai", "latin"], weight: ["400", "500", "600", "700"], variable: "--font-thai" });
const pixel = Pixelify_Sans({ subsets: ["latin"], weight: ["500", "700"], variable: "--font-pixel" });

export const metadata: Metadata = {
  title: "Gastron AI Office",
  description: "Virtual office where Gastron's AI marketing team plans and produces campaigns together.",
};

export default function RootLayout({ children }: { children: React.ReactNode }) {
  return (
    <html lang="th" className={`${thai.variable} ${pixel.variable}`}>
      <body>{children}</body>
    </html>
  );
}
