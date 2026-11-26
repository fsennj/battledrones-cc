/**
 * The menu's "🎬 Watch a replay" sheet: paste a battle record (the JSON an
 * agent battle writes to battles/, AGENT-BATTLES.md "Battle records") or pick
 * its file, and watch it in the battle viewer. The viewer itself loads only
 * once a record is chosen (main.ts).
 */
import { openSheet } from "./career";

export function showReplayPicker(host: HTMLElement, watch: (json: string, commit: () => boolean) => Promise<void>): void {
  const wrap = openSheet(
    host,
    "replaysheet",
    `<h2>Watch a replay</h2>
     <p class="sh-sub"><label for="replay-json">Paste a battle record copied from the end of a match, or choose its JSON file.</label></p>
     <textarea id="replay-json" spellcheck="false" autocomplete="off"></textarea>
     <button type="button" class="cta alt replay-file">Choose a file…</button>
     <input type="file" accept=".json,application/json" hidden>
     <p class="sh-note replay-error" role="alert" hidden></p>
     <div class="sh-actions"><button class="cta alt sheet-close">Cancel</button><button class="cta" id="replay-go">▶ Watch</button></div>`
  );
  const text = wrap.querySelector<HTMLTextAreaElement>("#replay-json")!;
  const error = wrap.querySelector<HTMLElement>(".replay-error")!;
  const go = wrap.querySelector<HTMLButtonElement>("#replay-go")!;
  const choose = wrap.querySelector<HTMLButtonElement>(".replay-file")!;
  const cancel = wrap.querySelector<HTMLButtonElement>(".sheet-close")!;
  const input = wrap.querySelector<HTMLInputElement>("input[type=file]")!;
  const commit = () => {
    if (!wrap.isConnected) return false;
    wrap.remove();
    return true;
  };
  const play = async (file?: File) => {
    if (!wrap.isConnected || go.disabled) return;
    error.hidden = true;
    cancel.focus({ preventScroll: true });
    choose.disabled = go.disabled = true;
    go.textContent = "Loading…";
    let readingFile = !!file;
    try {
      const json = file ? await file.text() : text.value;
      readingFile = false;
      if (!wrap.isConnected) return;
      if (!json.trim()) throw new Error("Paste a battle record or choose a JSON file.");
      if (file) text.value = json;
      await watch(json, commit);
    } catch (e) {
      if (!wrap.isConnected) return;
      error.textContent = readingFile ? "Couldn't read that file. Try choosing it again." : e instanceof Error ? e.message : String(e);
      error.hidden = false;
      choose.disabled = go.disabled = false;
      go.textContent = "▶ Watch";
    }
  };
  go.addEventListener("click", () => void play());
  choose.addEventListener("click", () => input.click());
  input.addEventListener("change", () => {
    const file = input.files?.[0];
    input.value = "";
    if (file) void play(file);
  });
}
