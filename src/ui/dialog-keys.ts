/** Keep keyboard focus inside an open dialog, including after its contents change. */
export function dialogKeys(dialog: HTMLElement, close?: () => void): void {
  dialog.addEventListener("keydown", (e) => {
    if (e.key === "Escape" && close) {
      e.preventDefault();
      e.stopPropagation();
      close();
      return;
    }
    if (e.key !== "Tab") return;
    const controls = Array.from(
      dialog.querySelectorAll<HTMLElement>("button, a[href], input, textarea, select, [tabindex]")
    ).filter((el) => el.tabIndex >= 0 && !el.matches(":disabled") && el.getClientRects().length);
    const first = controls[0];
    const last = controls.at(-1);
    const active = document.activeElement as HTMLElement;
    if (!controls.includes(active) || (e.shiftKey ? active === first : active === last)) {
      e.preventDefault();
      ((e.shiftKey ? last : first) ?? dialog).focus();
    }
  });
}
