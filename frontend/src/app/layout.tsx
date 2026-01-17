import type { Metadata } from "next";
import "./globals.css";

export const metadata: Metadata = {
  title: "Data-Organizer",
  description: "AI-powered filesystem analysis and optimization tool",
};

export default function RootLayout({
  children,
}: {
  children: React.ReactNode;
}) {
  return (
    <html lang="en">
      <body>{children}</body>
    </html>
  );
}
