interface ErrorStateProps {
  title: string;
  detail: string;
}

export function ErrorState({ title, detail }: ErrorStateProps) {
  return (
    <div className="page-shell flex items-center justify-center p-6">
      <div className="max-w-[640px] rounded-lg border border-[#f1c7c7] bg-white p-8">
        <h1 className="text-[24px] font-semibold text-[#111827]">{title}</h1>
        <p className="mt-3 text-[16px] text-[#6b7280]">{detail}</p>
      </div>
    </div>
  );
}
