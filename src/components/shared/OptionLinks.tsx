import Link from "next/link";

interface OptionItem<T extends string> {
  value: T;
  label: string;
}

interface OptionLinksProps<T extends string> {
  title: string;
  options: OptionItem<T>[];
  activeValue: T;
  getHref: (value: T) => string;
}

export function OptionLinks<T extends string>({
  title,
  options,
  activeValue,
  getHref,
}: OptionLinksProps<T>) {
  return (
    <div className="space-y-3">
      <h3 className="text-[14px] font-semibold text-[#111827]">{title}</h3>
      <div className="flex flex-wrap gap-2">
        {options.map((option) => {
          const isActive = option.value === activeValue;
          return (
            <Link
              key={option.value}
              className={`rounded-md border px-3 py-2 text-[14px] ${
                isActive
                  ? "border-[#8f3647] bg-[#faf2f4] text-[#8f3647]"
                  : "border-[#d1d5db] bg-white text-[#374151] hover:border-[#9ca3af]"
              }`}
              href={getHref(option.value)}
            >
              {option.label}
            </Link>
          );
        })}
      </div>
    </div>
  );
}
