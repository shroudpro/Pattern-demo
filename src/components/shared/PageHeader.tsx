import Link from "next/link";
import clsx from "clsx";
import type { ReactNode } from "react";

interface PageHeaderProps {
  eyebrow?: string;
  title: string;
  description?: string;
  backHref?: string;
  backLabel?: string;
  className?: string;
  titleClassName?: string;
  descriptionClassName?: string;
  aside?: ReactNode;
}

export function PageHeader({
  eyebrow,
  title,
  description,
  backHref,
  backLabel = "返回",
  className,
  titleClassName,
  descriptionClassName,
  aside,
}: PageHeaderProps) {
  return (
    <header className={clsx("space-y-3", className)}>
      {backHref ? (
        <Link className="inline-flex text-[14px] text-[#7e6443] transition-colors hover:text-[#4c2e18]" href={backHref}>
          {backLabel}
        </Link>
      ) : null}
      {eyebrow ? <p className="text-[14px] font-medium text-[#8f3647]">{eyebrow}</p> : null}
      <div className={clsx("gap-4", aside ? "grid items-end md:grid-cols-[minmax(0,1fr)_auto]" : "space-y-2")}>
        <div className="space-y-2">
          <h1 className={clsx("text-[32px] font-semibold leading-[1.25] text-[#111827]", titleClassName)}>{title}</h1>
          {description ? (
            <p className={clsx("max-w-[760px] text-[16px] text-[#6b7280]", descriptionClassName)}>{description}</p>
          ) : null}
        </div>
        {aside ? <div className="flex justify-start md:justify-end">{aside}</div> : null}
      </div>
    </header>
  );
}
