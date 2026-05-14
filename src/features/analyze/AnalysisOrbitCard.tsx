import clsx from "clsx";
import type { ReactNode } from "react";

interface AnalysisOrbitCardProps {
  title: string;
  kicker: string;
  children: ReactNode;
  className?: string;
}

export function AnalysisOrbitCard({ title, kicker, children, className }: AnalysisOrbitCardProps) {
  return (
    <article
      className={clsx(
        "h-fit self-start rounded-[8px] border border-[rgba(234,224,200,0.18)] bg-[rgba(10,14,16,0.68)] p-4 shadow-[0_14px_32px_rgba(0,0,0,0.22)] backdrop-blur-md",
        className,
      )}
    >
      <p className="text-[12px] tracking-[0.16em] text-[#c7a968]">{kicker}</p>
      <h3 className="mt-2 font-[var(--font-display)] text-[22px] leading-tight text-[#fff3dd]">{title}</h3>
      <div className="mt-3 text-[14px] leading-6 text-[#eadfc9]">{children}</div>
    </article>
  );
}
