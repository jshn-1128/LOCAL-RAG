"use client";

import { useEffect, useCallback } from "react";

type KeyHandler = (e: KeyboardEvent) => void;

export function useKeyboardShortcut(
  key: string,
  handler: KeyHandler,
  options?: { meta?: boolean; ctrl?: boolean; shift?: boolean },
) {
  const { meta = false, ctrl = false, shift = false } = options || {};

  const onKeyDown = useCallback(
    (e: KeyboardEvent) => {
      if (
        e.key.toLowerCase() === key.toLowerCase() &&
        e.metaKey === meta &&
        e.ctrlKey === ctrl &&
        e.shiftKey === shift
      ) {
        e.preventDefault();
        handler(e);
      }
    },
    [key, handler, meta, ctrl, shift],
  );

  useEffect(() => {
    window.addEventListener("keydown", onKeyDown);
    return () => window.removeEventListener("keydown", onKeyDown);
  }, [onKeyDown]);
}
