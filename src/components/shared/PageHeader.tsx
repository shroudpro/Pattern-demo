import Link from "next/link";
import clsx from "clsx";

interface PageHeaderProps {
  eyebrow?: string;
  title: string;
  description?: string;
  backHref?: string;
  backLabel?: string;
  className?: string;
  titleClassName?: string;
  descriptionClassName?: string;
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
}: PageHeaderProps) {
  return (
    <header className={clsx("space-y-3", className)}>
      {backHref ? (
        <Link className="inline-flex text-[14px] text-[#7e6443] transition-colors hover:text-[#4c2e18]" href={backHref}>
          {backLabel}
        </Link>
      ) : null}
      {eyebrow ? <p className="text-[14px] font-medium text-[#8f3647]">{eyebrow}</p> : null}
      <div className="space-y-2">
        <h1 className={clsx("text-[32px] font-semibold leading-[1.25] text-[#111827]", titleClassName)}>{title}</h1>
        {description ? (
          <p className={clsx("max-w-[760px] text-[16px] text-[#6b7280]", descriptionClassName)}>{description}</p>
        ) : null}
      </div>
    </header>
  );
}
