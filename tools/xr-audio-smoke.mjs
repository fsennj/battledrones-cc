// Run against Vite: node tools/xr-audio-smoke.mjs [base URL] [path/to/iwer.min.js]
import assert from "node:assert/strict";
import { existsSync } from "node:fs";
import { resolve } from "node:path";
import { chromium } from "playwright-core";

const base = new URL(process.argv[2] ?? "http://127.0.0.1:5173/");
const iwerPath = process.argv[3];
const executablePath = process.env.CHROMIUM_PATH ?? [
  "C:/Program Files/Google/Chrome/Application/chrome.exe",
  "/opt/pw-browsers/chromium-1194/chrome-linux/chrome",
].find(existsSync);
const browser = await chromium.launch({
  executablePath, args: ["--use-angle=swiftshader", "--enable-unsafe-swiftshader"],
});
const started = performance.now();

try {
  const page = await browser.newPage({ viewport: { width: 1280, height: 800 } });
  const errors = [];
  page.on("pageerror", (error) => errors.push(error.message));
  await page.route((url) => url.pathname.endsWith("/src/xr/main.ts"), async (route) => {
    const response = await route.fetch();
    const source = await response.text();
    const marker = "scene.add(table.root);";
    assert.equal(source.split(marker).length, 2, "Expected one live XR table");
    // Expose the rendered camera and table only in this isolated browser test.
    await route.fulfill({ response, body: source.replace(marker, `${marker}
      window.audioScene = { THREE, renderer, camera, table, tirol, world };`) });
  });
  await page.addInitScript(() => {
    const probe = window.audioProbe = { notes: [], loops: 0, spatial: [], analyser: null, score: false, relay: [], motor: [] };
    const startOsc = OscillatorNode.prototype.start;
    OscillatorNode.prototype.start = function (...args) {
      startOsc.apply(this, args);
      probe.notes.push(this.frequency.value);
    };
    const startBuffer = AudioBufferSourceNode.prototype.start;
    AudioBufferSourceNode.prototype.start = function (...args) {
      startBuffer.apply(this, args);
      if (this.loop) {
        probe.loops++;
        if (this.buffer?.duration > 200) probe.score = true;
      } else if (Math.abs((this.buffer?.duration ?? 0) - 3.615) < 0.001) {
        const line = { start: this.context.currentTime };
        probe.relay.push(line);
        this.addEventListener("ended", () => { line.end = this.context.currentTime; }, { once: true });
      }
    };
    const setTargetAtTime = AudioParam.prototype.setTargetAtTime;
    AudioParam.prototype.setTargetAtTime = function (level, at, timeConstant) {
      if (timeConstant === 0.055) probe.motor.push({ level, at });
      return setTargetAtTime.call(this, level, at, timeConstant);
    };
    const createPanner = AudioContext.prototype.createPanner;
    AudioContext.prototype.createPanner = function (...args) {
      const panner = createPanner.apply(this, args);
      probe.spatial.push(panner);
      return panner;
    };
    const connect = AudioNode.prototype.connect;
    AudioNode.prototype.connect = function (node, ...args) {
      if (this instanceof DynamicsCompressorNode && node === this.context.destination) {
        probe.analyser = this.context.createAnalyser();
        connect.call(this, probe.analyser);
      }
      return connect.call(this, node, ...args);
    };
    window.audioPeak = () => {
      if (!probe.analyser) return 0;
      const samples = new Float32Array(probe.analyser.fftSize);
      probe.analyser.getFloatTimeDomainData(samples);
      return Math.max(...samples.map(Math.abs));
    };
  });
  if (iwerPath) {
    await page.addInitScript({ path: resolve(iwerPath) });
    await page.route((url) => url.pathname.endsWith("/xr.html"), async (route) => {
      const response = await route.fetch();
      const initialization = '<script>window.xrTestDevice = new IWER.XRDevice(IWER.metaQuest3);' +
        'xrTestDevice.installRuntime({ forceInstall: true });</script>';
      await route.fulfill({ response, body: (await response.text()).replace("</head>", initialization + "</head>") });
    });
  }

  const notes = (frequency) => page.evaluate((freq) =>
    window.audioProbe.notes.filter((frequency) => frequency === freq).length, frequency);
  const peakAbove = (peak) => page.waitForFunction((value) => window.audioPeak() > value, peak);
  const waitSilent = () => page.waitForFunction(() => window.audioPeak() < 1e-7);
  const mute = page.locator("#mute-audio");
  const route = (pointCount) => page.waitForFunction((n) =>
    document.querySelectorAll("#mission-panel li.complete").length === n, pointCount, { timeout: 25000 });

  async function open(region) {
    const url = new URL("xr.html", base);
    if (region) url.searchParams.set("map", region);
    await page.goto(url.href);
    await page.getByText("Wähle eine blaue Einheit.", { exact: true }).waitFor();
    return page.evaluate(async () => {
      await new Promise((resolve) => requestAnimationFrame(() => requestAnimationFrame(resolve)));
      const { THREE, renderer, camera, table, tirol, world } = window.audioScene;
      const wasps = [...world.units.values()].filter((unit) => unit.kind === "wasp" && unit.faction === "blue");
      const unit = wasps[tirol ? 0 : 1];
      const { left, top, width, height } = renderer.domElement.getBoundingClientRect();
      const point = (physical) => {
        const screen = physical.clone().project(camera);
        return { screen: [left + (screen.x + 1) / 2 * width, top + (1 - screen.y) / 2 * height],
          physical: physical.toArray() };
      };
      const ground = (x, z) => point(table.root.localToWorld(new THREE.Vector3(x, table.heightAt(x, z), z)));
      return {
        unit: point(table.unitWorldPosition(unit.id, new THREE.Vector3())),
        targets: tirol ? tirol.checkpoints.map(({ x, y }) => ground(x, y))
          : [ground(unit.x + 7, unit.y + 2)],
      };
    });
  }

  const tirol = await open("zillertal");
  assert.equal(await page.evaluate(() => window.audioProbe.analyser), null);
  await page.mouse.move(...tirol.unit.screen);
  assert.equal(await notes(920), 0);
  await page.mouse.click(...tirol.targets[0].screen);
  await peakAbove(0.0003);
  assert.equal(await notes(600), 0);
  assert.equal(await page.evaluate(() => window.audioProbe.loops), 2);
  await page.mouse.click(...tirol.unit.screen);
  await page.getByText("WASP ausgewählt. Wähle ein Ziel.", { exact: true }).waitFor();
  await page.mouse.click(...tirol.unit.screen);
  assert.equal(await notes(920), 1);
  await page.mouse.click(5, 400);
  assert.equal(await notes(600), 0);
  await page.mouse.click(...tirol.targets[0].screen);
  assert.equal(await notes(600), 1);
  assert.equal(await notes(800), 1);
  await page.waitForFunction(() => window.audioProbe.notes.includes(115));
  await peakAbove(0.004);
  await mute.click();
  assert.equal(await mute.getAttribute("aria-pressed"), "true");
  await waitSilent();
  await route(1);
  assert.equal(await notes(1240), 0);
  await mute.click();
  assert.equal(await mute.getAttribute("aria-pressed"), "false");
  await peakAbove(0.0003);
  assert.equal(await notes(1240), 0);
  for (const [i, target] of tirol.targets.slice(1).entries()) {
    await page.mouse.click(...target.screen);
    await route(i + 2);
    assert.equal(await notes(1240), i + 1);
    assert.equal(await notes(740), i + 1);
  }
  await page.getByText("Mission abgeschlossen.", { exact: true }).waitFor();
  await page.waitForFunction(() => window.audioPeak() < 0.009);
  assert.equal(await notes(1240), 2);

  // A saved master mute also applies to a fresh page, including its first gesture.
  await mute.click();
  for (const region of ["achensee", "inntal"]) {
    const other = await open(region);
    assert.equal(await mute.getAttribute("aria-pressed"), "true");
    await page.mouse.click(...other.unit.screen);
    await waitSilent();
    assert.equal(await notes(920), 0);
    assert.equal(await page.evaluate(() => window.audioProbe.loops), 0);
    await mute.click();
    await peakAbove(0.0003);
    assert.equal(await page.evaluate(() => window.audioProbe.loops), 2);
    await page.mouse.click(...other.targets[0].screen);
    await route(1);
    assert.equal(await notes(540), 1);
    assert.equal(await notes(1240), 0);
    await mute.click();
  }

  // Check the two persisted buses independently using the same engine as the 2D game.
  await open("zillertal");
  await page.evaluate(async () => {
    const { sfx } = await import("/src/game/audio.ts");
    sfx.setChannel("music", false);
    sfx.setChannel("sfx", true);
  });
  await mute.click(); // master on, Music remains off
  const effectsOnly = await open("zillertal");
  await page.mouse.click(...effectsOnly.unit.screen);
  await peakAbove(0.007);
  assert.equal(await notes(920), 1);
  assert.equal(await page.evaluate(() => window.audioProbe.loops), 0);
  await page.evaluate(async () => {
    const { sfx } = await import("/src/game/audio.ts");
    sfx.setChannel("music", true);
    sfx.setChannel("sfx", false);
  });
  await peakAbove(0.0003);
  await page.mouse.click(...effectsOnly.targets[0].screen);
  await route(1);
  assert.deepEqual(await Promise.all([notes(600), notes(115), notes(1240)]), [0, 0, 0]);

  await page.evaluate(async () => {
    const { sfx } = await import("/src/game/audio.ts");
    sfx.setChannel("sfx", true);
  });
  const river = await open(null);
  if (iwerPath) {
    await page.getByRole("button", { name: "VR starten" }).click();
    await page.getByRole("button", { name: "VR verlassen" }).waitFor();
    async function press(point, control) {
      await page.evaluate(async ({ coordinates, control }) => {
        const { Vector3, Quaternion } = await import("/node_modules/three/build/three.module.js");
        const hand = window.xrTestDevice.controllers.right;
        hand.connected = true;
        const origin = new Vector3(0.24, 1.28, -0.2);
        const direction = new Vector3(...coordinates).sub(origin).normalize();
        const orientation = new Quaternion().setFromUnitVectors(new Vector3(0, 0, -1), direction);
        hand.position.set(...origin.toArray());
        hand.quaternion.set(...orientation.toArray());
        const nextFrame = () => new Promise((resolve) => requestAnimationFrame(resolve));
        await nextFrame();
        hand.updateButtonValue(control, 1);
        await nextFrame();
        await nextFrame();
        hand.updateButtonValue(control, 0);
      }, { coordinates: point.physical, control });
    }
    await press(river.unit, "trigger");
    await page.getByText("WASP ausgewählt. Wähle ein Ziel.", { exact: true }).waitFor();
    assert.equal(await notes(920), 1);
    await press(river.targets[0], "trigger");
    await page.waitForFunction(() => window.audioProbe.spatial.some((panner) =>
      panner.panningModel === "HRTF" && panner.positionZ.value < -0.15));
    assert.equal(await notes(600), 1);
    await peakAbove(0.001);
    await press(river.targets[0], "squeeze");
    await page.waitForFunction(() => document.querySelector("#mute-audio").getAttribute("aria-pressed") === "true");
    await waitSilent();
    await page.getByText("WASP hat das Ziel erreicht.", { exact: true }).waitFor();
    await page.getByRole("button", { name: "VR verlassen" }).dispatchEvent("click");
    await page.getByRole("button", { name: "VR starten" }).waitFor();
  } else {
    await page.mouse.click(...river.unit.screen);
    assert.equal(await notes(920), 1);
    await page.mouse.click(...river.targets[0].screen);
    await page.getByText("WASP hat das Ziel erreicht.", { exact: true }).waitFor();
    assert.equal(await notes(600), 1);
  }
  assert.equal(await page.evaluate(() => window.audioProbe.loops), 0);

  await page.evaluate(() => {
    localStorage.removeItem("battledrones.audio");
    localStorage.removeItem("battledrones.muted");
  });
  await page.goto(new URL("xr.html?map=zillertal&ton=nachtkonvoi", base).href);
  await page.getByRole("button", { name: "Nachtkonvoi · Funkprobe im Flug" }).click();
  await route(1);
  await page.waitForFunction(() => window.audioProbe.relay[0]?.end);
  const overlap = await page.evaluate(() => {
    const { relay, score, motor } = window.audioProbe;
    const [{ start, end }] = relay;
    return { count: relay.length, duration: end - start, score,
      motorAtStart: motor.some(({ level, at }) => level > 0.03 && at >= start && at < start + 0.3),
      motorAtEnd: motor.some(({ level, at }) => level > 0.03 && at > end - 0.3 && at <= end) };
  });
  assert.equal(overlap.count, 1, "The waypoint should not restart the in-flight radio line");
  assert.ok(overlap.duration >= 3.60 && overlap.score && overlap.motorAtStart && overlap.motorAtEnd,
    `Expected a complete radio line with music and motor throughout: ${JSON.stringify(overlap)}`);
  assert.deepEqual(errors, []);
  console.log(`XR AUDIO OK (desktop Tirol and ${iwerPath ? "emulated Quest 3" : "desktop Riverlands"}, ${Math.round(performance.now() - started)} ms)`);
} finally {
  await browser.close();
}
