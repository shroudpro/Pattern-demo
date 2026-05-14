interface NoticeBannerProps {
  messages: string[];
}

export function NoticeBanner({ messages }: NoticeBannerProps) {
  if (!messages.length) {
    return null;
  }

  return (
    <div className="rounded-lg border border-[#f0d8a8] bg-[#fffbeb] p-4 text-[14px] text-[#6b4f1d]">
      {messages.map((message) => (
        <p key={message}>{message}</p>
      ))}
    </div>
  );
}
