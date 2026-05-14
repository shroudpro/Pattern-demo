import type { ButtonHTMLAttributes, ReactNode } from "react";
import clsx from "clsx";

interface TextureButtonProps extends ButtonHTMLAttributes<HTMLButtonElement> {
  children: ReactNode;
  backgroundImage: string;
  className?: string;
  labelClassName?: string;
}

export function TextureButton({
  children,
  backgroundImage,
  className,
  labelClassName,
  type = "button",
  ...props
}: TextureButtonProps) {
  return (
    <button
      {...props}
      className={clsx("texture-button", className)}
      style={{ backgroundImage: `url(${backgroundImage})` }}
      type={type}
    >
      <span className={clsx("texture-button__label", labelClassName)}>{children}</span>
    </button>
  );
}
