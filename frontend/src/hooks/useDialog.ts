import { useEffect, useRef } from "react";

/** Trap focus while open, close on Escape, and return focus to the opener. */
export function useDialog(open: boolean, onClose: () => void) {
  const ref = useRef<HTMLDivElement>(null);
  const close = useRef(onClose);
  close.current = onClose;
  useEffect(() => {
    if (!open) return;
    const previous = document.activeElement as HTMLElement | null;
    const root = ref.current;
    if (!root) return;
    const inertElements: [HTMLElement, boolean][] = [];
    let branch: HTMLElement = root;
    while(branch.parentElement && branch.parentElement !== document.body) {
      for(const sibling of Array.from(branch.parentElement.children)) {
        if(sibling !== branch && sibling instanceof HTMLElement) { inertElements.push([sibling,sibling.inert]); sibling.inert = true; }
      }
      branch = branch.parentElement;
    }
    const focusable = () => Array.from(root.querySelectorAll<HTMLElement>('button:not(:disabled), a[href], input, select, textarea, [tabindex="0"]')).filter(el => el.getClientRects().length > 0);
    (focusable()[0] || root).focus();
    const keydown = (event: KeyboardEvent) => {
      if (event.key === "Escape") { event.preventDefault(); close.current(); }
      if (event.key !== "Tab") return;
      const items = focusable();
      if (!items.length) { event.preventDefault(); root.focus(); return; }
      const first = items[0], last = items[items.length - 1];
      if (event.shiftKey && (document.activeElement === first || !root.contains(document.activeElement))) { event.preventDefault(); last.focus(); }
      else if (!event.shiftKey && (document.activeElement === last || !root.contains(document.activeElement))) { event.preventDefault(); first.focus(); }
    };
    document.addEventListener("keydown", keydown);
    return () => { document.removeEventListener("keydown", keydown); inertElements.forEach(([element,value]) => {element.inert=value;}); previous?.focus(); };
  }, [open]);
  return ref;
}
