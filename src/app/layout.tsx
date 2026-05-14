import type { Metadata } from "next";
import "@/app/globals.css";
import { IntroOverlay } from "@/components/motion/IntroOverlay";
import { RouteTransitionProvider } from "@/components/motion/RouteTransitionProvider";

export const metadata: Metadata = {
  title: "字象万千",
  description: "AI 汉字文化意象可视化系统",
};

export default function RootLayout({
  children,
}: Readonly<{
  children: React.ReactNode;
}>) {
  return (
    <html lang="zh-CN">
      <body>
        <RouteTransitionProvider>
          <IntroOverlay />
          {children}
        </RouteTransitionProvider>
      </body>
    </html>
  );
}
