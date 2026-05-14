import type { ReactNode } from "react";
import clsx from "clsx";

interface SectionCardProps {
  title?: string;
  children: ReactNode;
  className?: string;
  contentClassName?: string;
  titleClassName?: string;
  backgroundImage?: string;
  overlayClassName?: string;
  variant?: "plain" | "paper" | "brown";
}

export function SectionCard({
  title,
  children,
  className,
  contentClassName,
  titleClassName,
  backgroundImage,
  overlayClassName,
  variant = "plain",
}: SectionCardProps) {
  return (
    <section
      className={clsx("ornate-card", `ornate-card--${variant}`, backgroundImage ? "ornate-card--image" : null, className)}
    >
      {backgroundImage ? <div aria-hidden="true" className="ornate-card__image" style={{ backgroundImage: `url(${backgroundImage})` }} /> : null}
      {backgroundImage ? <div aria-hidden="true" className={clsx("ornate-card__overlay", overlayClassName)} /> : null}
      <div className={clsx("ornate-card__content", contentClassName)}>
        {title ? <h2 className={clsx("ornate-card__title", titleClassName)}>{title}</h2> : null}
        {children}
      </div>
    </section>
  );
}
