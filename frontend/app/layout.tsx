import type { Metadata } from "next";
import "./globals.css";

export const metadata: Metadata = {
  title: "Digital FTE Agent",
  description: "Generate social posts with the Digital FTE Agent backend.",
};

export default function RootLayout({ children }: Readonly<{ children: React.ReactNode }>) {
  return (
    <html lang="en">
      <body>{children}</body>
    </html>
  );
}
