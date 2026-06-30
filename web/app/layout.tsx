import type { Metadata } from "next";
import "./globals.css";

export const metadata: Metadata = {
  title: "Quorum — Supply-Chain Exception Society",
  description:
    "A multi-agent society that decides whether a disruption is material to your shipments.",
};

export default function RootLayout({
  children,
}: {
  children: React.ReactNode;
}) {
  return (
    <html lang="en">
      <head>
        <link
          rel="stylesheet"
          href="https://unpkg.com/maplibre-gl@4/dist/maplibre-gl.css"
        />
      </head>
      <body>{children}</body>
    </html>
  );
}
