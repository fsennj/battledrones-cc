import { createReadStream } from "node:fs";
import { stat } from "node:fs/promises";
import { createServer } from "node:http";
import { extname, join } from "node:path";
import { fileURLToPath } from "node:url";

const bundle = fileURLToPath(new URL("../art/xr/sound/nachtkonvoi-runtime/", import.meta.url));
const host = "127.0.0.1";
const port = 5194;
const scene = "/xr.html?map=zillertal&ton=nachtkonvoi";
const mime = {
  ".css": "text/css; charset=utf-8", ".html": "text/html; charset=utf-8",
  ".js": "text/javascript; charset=utf-8", ".json": "application/json",
  ".mp3": "audio/mpeg", ".wav": "audio/wav", ".glb": "model/gltf-binary",
  ".jpg": "image/jpeg", ".png": "image/png", ".webp": "image/webp", ".woff2": "font/woff2",
};

const server = createServer(async (request, response) => {
  response.setHeader("X-Content-Type-Options", "nosniff");
  if (request.method !== "GET" && request.method !== "HEAD") {
    response.writeHead(405, { Allow: "GET, HEAD" }).end();
    return;
  }
  const url = new URL(request.url, `http://${host}:${port}`);
  if (url.pathname === "/" || url.pathname === "/xr.html" && (url.searchParams.get("map") !== "zillertal" || url.searchParams.get("ton") !== "nachtkonvoi")) {
    response.writeHead(302, { Location: scene }).end();
    return;
  }
  if (url.pathname !== "/xr.html" && !/^\/(?:assets|icons)\/(?:[\w-]+\/)*[\w.-]+$/.test(url.pathname)) {
    response.writeHead(404).end();
    return;
  }
  const path = join(bundle, url.pathname.slice(1));
  const file = await stat(path).catch(() => null);
  if (!file?.isFile()) {
    response.writeHead(404).end();
    return;
  }
  response.writeHead(200, {
    "Content-Type": mime[extname(path)] ?? "application/octet-stream",
    "Content-Length": file.size,
  });
  if (request.method === "HEAD") response.end();
  else createReadStream(path).on("error", () => response.destroy()).pipe(response);
});

await stat(join(bundle, "xr.html"));
server.listen(port, host, () => console.log(`Nachtkonvoi: http://${host}:${port}${scene}`));
