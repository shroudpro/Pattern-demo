"use client";

import { useEffect, useState, type KeyboardEvent } from "react";

import { INTRO_SESSION_KEY, shouldShowIntroOverlay } from "@/lib/design/content";

export function IntroOverlay() {
  const [visible, setVisible] = useState(false);
  const [revealed, setRevealed] = useState(false);

  useEffect(() => {
    const shouldShow = shouldShowIntroOverlay(window.sessionStorage.getItem(INTRO_SESSION_KEY));
    setVisible(shouldShow);
  }, []);

  function handleClick() {
    if (!revealed) {
      setRevealed(true);
      return;
    }

    window.sessionStorage.setItem(INTRO_SESSION_KEY, "1");
    setVisible(false);
  }

  function handleKeyDown(event: KeyboardEvent<HTMLDivElement>) {
    if (event.key === "Enter" || event.key === " ") {
      event.preventDefault();
      handleClick();
    }
  }

  if (!visible) {
    return null;
  }

  return (
    <div
      className={`intro-overlay ${revealed ? "intro-overlay--revealed" : ""}`}
      onClick={handleClick}
      onKeyDown={handleKeyDown}
      role="button"
      tabIndex={0}
    >
      <div className="intro-overlay__panel">
        <h1 className="intro-overlay__title">字象万千</h1>
        <p className="intro-overlay__subtitle">以AI赋能设计，用文化创造美好</p>
      </div>
    </div>
  );
}
