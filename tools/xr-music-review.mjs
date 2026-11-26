import { randomUUID } from "node:crypto";
import { createReadStream, existsSync, mkdirSync, readFileSync, renameSync, rmSync, statSync, writeFileSync } from "node:fs";
import { createServer } from "node:http";
import { dirname, join, resolve } from "node:path";
import { pipeline } from "node:stream/promises";
import { fileURLToPath } from "node:url";
import { parseArgs } from "node:util";

const root = fileURLToPath(new URL("../", import.meta.url));
const ui = join(root, "tools/xr-music-review");
const album = "art/xr/sound/music/stahltrieb";
const longAlbum = `${album}/langfassungen`;
const { values } = parseArgs({ options: {
  port: { type: "string", default: "5193" },
  state: { type: "string", default: join(root, ".xr-music-review/ratings.json") },
} });
const port = Number(values.port);
if (!Number.isInteger(port) || port < 1 || port > 65535) throw new Error("Invalid port");
const host = `127.0.0.1:${port}`;
const origin = `http://${host}`;
const statePath = resolve(values.state);
const ratings = existsSync(statePath) ? JSON.parse(readFileSync(statePath, "utf8")) : {};
const catalogue = new Map();
const playlistEntries = contents => contents.matchAll(/^#EXTINF:(\d+),([^\r\n]+)\r?\n(\d{2}-[a-z0-9-]+\.mp3)[ \t\r]*$/gm);
const durationsPath = join(root, longAlbum, "Stahltrieb-Langfassungen.m3u8");
const durations = existsSync(durationsPath)
  ? new Map(Array.from(playlistEntries(readFileSync(durationsPath, "utf8")), ([, seconds, , file]) => [file, Number(seconds)]))
  : new Map();
const playlist = readFileSync(join(root, album, "Stahltrieb.m3u8"), "utf8");
for (const [, , title, file] of playlistEntries(playlist)) {
  const number = Number(file.slice(0, 2));
  if (number !== catalogue.size + 1) throw new Error(`Unexpected title order: ${file}`);
  const id = file.slice(0, -4);
  const duration = durations.get(file) ?? null;
  if (duration !== null && (duration < 180 || duration > 600)) throw new Error(`Track duration out of range: ${file}`);
  catalogue.set(id, { id, title, number, group: number <= 35 ? "serious" : "fun", file: `${longAlbum}/${file}`, duration });
}
if (catalogue.size !== 50) throw new Error("Expected 50 titles in Stahltrieb.m3u8");

const files = new Map([
  ["/", ["index.html", "text/html; charset=utf-8"]],
  ["/review.css", ["review.css", "text/css; charset=utf-8"]],
  ["/review.js", ["review.js", "text/javascript; charset=utf-8"]],
]);

function trackView(track) {
  return { ...track, available: existsSync(join(root, track.file)), rating: null, selected: false, ...ratings[track.id] };
}

function json(response, payload, status = 200) {
  response.writeHead(status, { "Content-Type": "application/json; charset=utf-8" });
  response.end(JSON.stringify(payload));
}

function save(track, changes) {
  const next = { ...ratings, [track.id]: { ...ratings[track.id], ...changes } };
  const pending = `${statePath}.${randomUUID()}.tmp`;
  mkdirSync(dirname(statePath), { recursive: true });
  try {
    writeFileSync(pending, JSON.stringify(next, null, 2) + "\n", { flag: "wx" });
    renameSync(pending, statePath);
  } finally {
    rmSync(pending, { force: true });
  }
  ratings[track.id] = next[track.id];
}

async function readChanges(request) {
  let body = "";
  const length = Number(request.headers["content-length"]);
  if (!Number.isInteger(length) || length < 2 || length > 256) return null;
  request.setEncoding("utf8");
  for await (const chunk of request) body += chunk;
  try {
    const changes = JSON.parse(body);
    if (!changes || typeof changes !== "object" || Array.isArray(changes)) return null;
    const checks = {
      rating: value => value === null || Number.isInteger(value) && value >= 1 && value <= 5,
      selected: value => typeof value === "boolean",
    };
    const entries = Object.entries(changes);
    return entries.length && entries.every(([key, value]) => Object.hasOwn(checks, key) && checks[key](value)) ? changes : null;
  } catch {
    return null;
  }
}

async function streamAudio(request, response, path) {
  const { size } = statSync(path);
  const headers = { "Content-Type": "audio/mpeg", "Accept-Ranges": "bytes", "Content-Length": size };
  const range = request.headers.range;
  if (!range) {
    response.writeHead(200, headers);
    if (request.method === "HEAD") return response.end();
    return pipeline(createReadStream(path), response);
  }
  const match = /^bytes=(\d*)-(\d*)$/.exec(range);
  const start = match?.[1] ? Number(match[1]) : Math.max(0, size - Number(match?.[2]));
  const end = match?.[1] && match[2] ? Math.min(size - 1, Number(match[2])) : size - 1;
  if (!match || !match[1] && !match[2] || start >= size || start > end) {
    response.writeHead(416, { "Content-Range": `bytes */${size}` });
    return response.end();
  }
  response.writeHead(206, { ...headers, "Content-Range": `bytes ${start}-${end}/${size}`, "Content-Length": end - start + 1 });
  if (request.method === "HEAD") return response.end();
  return pipeline(createReadStream(path, { start, end }), response);
}

async function handle(request, response) {
  response.setHeader("Cache-Control", "no-store");
  response.setHeader("X-Content-Type-Options", "nosniff");
  response.setHeader("Content-Security-Policy", "default-src 'self'; base-uri 'none'; frame-ancestors 'none'");
  if (request.headers.host !== host || request.headers.origin && request.headers.origin !== origin) {
    return json(response, { error: "Local access only" }, 403);
  }
  const { pathname } = new URL(request.url, origin);
  if (request.method === "GET" && files.has(pathname)) {
    const [file, type] = files.get(pathname);
    response.writeHead(200, { "Content-Type": type });
    return response.end(readFileSync(join(ui, file)));
  }
  if (request.method === "GET" && pathname === "/api/tracks") {
    return json(response, Array.from(catalogue.values(), trackView));
  }
  if (request.method === "GET" && pathname === "/api/selection") {
    const tracks = Array.from(catalogue.values(), trackView).filter(track => track.selected);
    tracks.sort((a, b) => (b.rating ?? 0) - (a.rating ?? 0) || a.number - b.number);
    response.setHeader("Content-Disposition", 'attachment; filename="stahltrieb-auswahl.json"');
    return json(response, { album: "Stahltrieb", tracks: tracks.map(({ available, ...track }) => track) });
  }
  const audioId = /^\/audio\/([a-z0-9-]+)\.mp3$/.exec(pathname)?.[1];
  const reviewId = /^\/api\/tracks\/([a-z0-9-]+)$/.exec(pathname)?.[1];
  if (["GET", "HEAD"].includes(request.method) && catalogue.has(audioId)) {
    const path = join(root, catalogue.get(audioId).file);
    if (existsSync(path)) return streamAudio(request, response, path);
  }
  if (request.method === "PATCH" && catalogue.has(reviewId)) {
    const track = catalogue.get(reviewId);
    if (!existsSync(join(root, track.file))) return json(response, { error: "Track unavailable" }, 409);
    const changes = await readChanges(request);
    if (!changes) return json(response, { error: "Invalid rating or selection" }, 400);
    save(track, changes);
    return json(response, trackView(track));
  }
  return json(response, { error: "Not found" }, 404);
}

createServer((request, response) => {
  handle(request, response).catch(error => {
    if (response.destroyed) return;
    console.error(error);
    if (!response.headersSent) json(response, { error: "Server error" }, 500);
    else response.end();
  });
}).listen(port, "127.0.0.1", () => console.log(`Stahltrieb: ${origin}`));
