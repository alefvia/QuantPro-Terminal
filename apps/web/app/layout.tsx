import type { ReactNode } from "react";
import "./globals.css";

export const metadata = {
  title: "QuantPro Terminal",
  description: "Research and paper-trading quantitative terminal",
};

export default function RootLayout({ children }: { children: ReactNode }) {
  return (
    <html lang="pt-BR">
      <body>{children}</body>
    </html>
  );
}
