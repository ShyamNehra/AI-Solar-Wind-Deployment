import type { Metadata } from "next";

export const metadata: Metadata = {
  title: "Solar & Wind Deployment Platform",
  description: "Milestone 1 Core Auth & Project/Site Scaffold",
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
