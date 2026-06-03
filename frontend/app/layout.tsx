import type { Metadata } from "next";
import { Inter } from "next/font/google";
import "./globals.css";
import { Sidebar } from "@/components/Sidebar";

const inter = Inter({ subsets: ["latin"] });

export const metadata: Metadata = {
  title: "CollegePath AI",
  description: "AI-powered college recommendation system",
};

export default function RootLayout({
  children,
}: Readonly<{
  children: React.ReactNode;
}>) {
  return (
    <html lang="en">
      <body className={inter.className}>
        <div className="h-full relative">
          <div className="hidden h-full md:flex md:w-72 md:flex-col md:fixed md:inset-y-0 z-[80] bg-[#0d1117]">
            <Sidebar />
          </div>
          <main className="md:pl-72 h-full bg-[#0b0e14]">
            {children}
          </main>
        </div>
      </body>
    </html>
  );
}
