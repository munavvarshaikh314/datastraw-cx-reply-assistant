import type { Metadata } from "next";
import "./globals.css";

export const metadata: Metadata = {
  title: "DataStraw CX",
  description: "AI Customer Support Workspace",
};

export default function RootLayout({
  children,
}: Readonly<{
  children: React.ReactNode;
}>) {
  return (
    <html lang="en">
      <body>{children}</body>
    </html>
  );
}
