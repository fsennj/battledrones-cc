const strings = {
  de: {
    review: "Musik-Hörabnahme", language: "Sprache", export: "Auswahl exportieren", player: "Wiedergabe",
    emptyPlayer: "Titel zum Anhören wählen", show: "Anzeigen", sort: "Sortieren", all: "Alle Titel",
    unrated: "Ohne Wertung", selectedOnly: "Spielauswahl", albumOrder: "Albumreihenfolge", topRated: "Beste Wertung",
    previous: "Zurück", next: "Weiter", serious: "Ernst", fun: "Tirol-Fun", groups: "Fassung", pages: "Seiten",
    catalogue: "Titel", play: "Anhören", pause: "Pause", pick: "Fürs Spiel", picked: "Ausgewählt",
    unavailable: "Langfassung fehlt", clear: "Wertung löschen", empty: "Keine Titel in dieser Ansicht.",
    loading: "Titel werden geladen …", loadError: "Titel konnten nicht geladen werden. Lade die Seite erneut.",
    saveError: "Änderung konnte nicht gespeichert werden.", saved: "Gespeichert", audioError: "Die Datei konnte nicht abgespielt werden.",
    score: n => `${n} ${n === 1 ? "Stern" : "Sterne"}`, page: (n, max) => `Seite ${n} von ${max}`,
    summary: (rated, total, picked) => `${rated} von ${total} bewertet · ${picked} in der Spielauswahl`,
  },
  en: {
    review: "Music review", language: "Language", export: "Export selection", player: "Playback",
    emptyPlayer: "Choose a track to play", show: "Show", sort: "Sort", all: "All tracks",
    unrated: "Unrated", selectedOnly: "Game selection", albumOrder: "Album order", topRated: "Highest rated",
    previous: "Previous", next: "Next", serious: "Serious", fun: "Tyrolean fun", groups: "Version", pages: "Pages",
    catalogue: "Tracks", play: "Play", pause: "Pause", pick: "For the game", picked: "Selected",
    unavailable: "Full-length version missing", clear: "Clear rating", empty: "No tracks in this view.",
    loading: "Loading tracks …", loadError: "Could not load tracks. Reload the page to try again.",
    saveError: "Could not save the change.", saved: "Saved", audioError: "Could not play the file.",
    score: n => `${n} ${n === 1 ? "star" : "stars"}`, page: (n, max) => `Page ${n} of ${max}`,
    summary: (rated, total, picked) => `${rated} of ${total} rated · ${picked} selected for the game`,
  },
};

const byId = id => document.getElementById(id);
const tracksList = byId("tracks");
const player = byId("audio");
const language = byId("language");
const filter = byId("filter");
const sort = byId("sort");
const previous = byId("previous");
const next = byId("next");
const groups = [...document.querySelectorAll("[data-group]")];
const saving = new Set();
const pages = { serious: 0, fun: 0 };
let tracks = [];
let group = "serious";
let locale = "de";
let currentId;
let loaded = false;
let status = ["loading", false];

try {
  if (localStorage.getItem("stahltrieb-review-language") === "en") locale = "en";
} catch {
  // The review state lives on the server even when browser preferences are unavailable.
}

function node(tag, content, className) {
  const element = document.createElement(tag);
  if (content) element.textContent = content;
  if (className) element.className = className;
  return element;
}

function button(text, label, action, key, className) {
  const element = node("button", text, className);
  element.type = "button";
  element.dataset.control = key;
  element.setAttribute("aria-label", label);
  element.addEventListener("click", action);
  return element;
}

function announce(key, error = false) {
  status = [key, error];
  byId("feedback").textContent = key ? strings[locale][key] : "";
  byId("feedback").dataset.error = String(error);
}

function applyLocale() {
  const text = strings[locale];
  document.documentElement.lang = locale === "de" ? "de-AT" : "en";
  document.title = `Stahltrieb · ${text.review}`;
  language.value = locale;
  for (const element of document.querySelectorAll("[data-text]")) {
    element.textContent = text[element.dataset.text];
  }
  for (const key of ["catalogue", "groups", "pagination"]) {
    byId(key).setAttribute("aria-label", text[key === "pagination" ? "pages" : key]);
  }
  announce(...status);
  render();
}

async function change(track, changes) {
  if (saving.has(track.id)) return;
  saving.add(track.id);
  try {
    const response = await fetch(`/api/tracks/${track.id}`, {
      method: "PATCH", headers: { "Content-Type": "application/json" }, body: JSON.stringify(changes),
    });
    if (!response.ok) throw new Error("Save failed");
    Object.assign(track, await response.json());
    announce("saved");
  } catch {
    announce("saveError", true);
  } finally {
    saving.delete(track.id);
    render();
  }
}

async function play(track) {
  if (currentId === track.id && !player.paused) {
    player.pause();
    return;
  }
  if (currentId !== track.id) {
    currentId = track.id;
    player.src = `/audio/${track.id}.mp3`;
  }
  try {
    await player.play();
    if (status[0] === "audioError") announce();
  } catch (error) {
    if (error.name !== "AbortError") announce("audioError", true);
  }
  render();
}

function formatDuration(seconds) {
  return `${Math.floor(seconds / 60)}:${String(seconds % 60).padStart(2, "0")}`;
}

function trackRow(track) {
  const text = strings[locale];
  const row = node("li", "", "track");
  row.dataset.id = track.id;
  row.classList.toggle("is-current", currentId === track.id);
  const title = node("div", "", "track-title");
  const playing = currentId === track.id && !player.paused;
  const listen = button(playing ? "Ⅱ" : "▶", `${playing ? text.pause : text.play} · ${track.title}`, () => play(track), "play");
  listen.disabled = !track.available;
  const name = node("div");
  name.append(node("strong", track.title));
  if (track.duration || !track.available) {
    name.append(node("p", track.available ? formatDuration(track.duration) : text.unavailable, "track-info"));
  }
  title.append(listen, name);

  const stars = node("div", "", "stars");
  stars.setAttribute("role", "group");
  stars.setAttribute("aria-label", `${track.title} · ${track.rating === null ? text.unrated : text.score(track.rating)}`);
  for (let rating = 1; rating <= 5; rating += 1) {
    const filled = rating <= track.rating;
    const star = button(filled ? "★" : "☆", text.score(rating), () => change(track, { rating }), `rating-${rating}`, filled ? "filled" : "");
    star.setAttribute("aria-pressed", String(track.rating === rating));
    star.disabled = !track.available;
    stars.append(star);
  }
  const clear = button("×", text.clear, () => change(track, { rating: null }), "clear", "clear");
  clear.disabled = track.rating === null;
  stars.append(clear);

  const pick = button(track.selected ? text.picked : text.pick, `${track.selected ? text.picked : text.pick} · ${track.title}`,
    () => change(track, { selected: !track.selected }), "pick", "pick");
  pick.setAttribute("aria-pressed", String(track.selected));
  pick.disabled = !track.available;
  row.append(title, stars, pick);
  return row;
}

function render() {
  const text = strings[locale];
  const focused = document.activeElement;
  const focusedTrack = focused.closest("[data-id]")?.dataset.id;
  const focusedControl = focused.dataset.control;
  const active = tracks.find(track => track.id === currentId);
  byId("player-title").textContent = active?.title ?? text.emptyPlayer;
  const category = tracks.filter(track => track.group === group);
  for (const tab of groups) {
    const key = tab.dataset.group;
    const count = tracks.filter(track => track.group === key).length;
    tab.textContent = loaded ? `${text[key]} (${count})` : text[key];
    tab.setAttribute("aria-pressed", String(key === group));
  }
  byId("summary").textContent = loaded ? text.summary(category.filter(t => t.rating !== null).length, category.length,
    category.filter(t => t.selected).length) : "";
  const shown = category.filter(t => filter.value === "all" || (filter.value === "unrated" ? t.rating === null : t.selected));
  if (sort.value === "rating") shown.sort((a, b) => (b.rating ?? 0) - (a.rating ?? 0) || a.number - b.number);
  const narrow = matchMedia("(max-width: 41rem)").matches;
  const pageSize = Math.min(6, Math.max(1, Math.floor((window.innerHeight - (narrow ? 475 : 360)) / (narrow ? 108 : 55))));
  const max = Math.max(1, Math.ceil(shown.length / pageSize));
  const page = pages[group] = Math.min(pages[group], max - 1);
  const rows = shown.slice(page * pageSize, (page + 1) * pageSize).map(trackRow);
  if (loaded && !rows.length) rows.push(node("li", text.empty, "empty"));
  tracksList.replaceChildren(...rows);
  previous.disabled = page === 0;
  next.disabled = page + 1 === max;
  byId("position").textContent = loaded ? text.page(page + 1, max) : "";
  if (focusedTrack && focusedControl) {
    const replacement = tracksList.querySelector(`[data-id="${focusedTrack}"] [data-control="${focusedControl}"]:not(:disabled)`);
    (replacement ?? filter).focus({ preventScroll: true });
  }
}

for (const tab of groups) tab.addEventListener("click", () => { group = tab.dataset.group; render(); });
for (const select of [filter, sort]) select.addEventListener("change", () => { pages.serious = pages.fun = 0; render(); });
previous.addEventListener("click", () => { pages[group] -= 1; render(); });
next.addEventListener("click", () => { pages[group] += 1; render(); });
language.addEventListener("change", () => {
  locale = language.value;
  try { localStorage.setItem("stahltrieb-review-language", locale); } catch { /* optional preference */ }
  applyLocale();
});
for (const name of ["play", "pause", "ended"]) player.addEventListener(name, render);
player.addEventListener("error", () => { if (currentId) announce("audioError", true); });
window.addEventListener("resize", render);

applyLocale();
try {
  const response = await fetch("/api/tracks");
  if (!response.ok) throw new Error("Catalogue unavailable");
  tracks = await response.json();
  loaded = true;
  announce();
  render();
} catch {
  announce("loadError", true);
}
