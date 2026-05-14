interface TagListProps {
  items: string[];
  tone?: "primary" | "neutral";
}

export function TagList({ items, tone = "neutral" }: TagListProps) {
  const toneClass =
    tone === "primary"
      ? "border-[#d9b7c0] bg-[#faf2f4] text-[#8f3647]"
      : "border-[#d1d5db] bg-[#f8f9fa] text-[#374151]";

  return (
    <div className="flex flex-wrap gap-2">
      {items.map((item) => (
        <span
          key={item}
          className={`rounded-md border px-3 py-1 text-[12px] font-medium leading-[1.5] ${toneClass}`}
        >
          {item}
        </span>
      ))}
    </div>
  );
}
