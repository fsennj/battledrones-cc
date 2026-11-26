"""Build the English radio clips offline using the Kokoro-82M Apache-2.0 model.

Install kokoro-onnx==0.6.1 and soundfile==0.14.0 in an isolated Python environment.
Run with kokoro-v1.0.int8.onnx and voices-v1.0.bin from kokoro-onnx model-files-v1.1.
The game plays the resulting MP3 from its own origin without an inference dependency.
"""

import argparse
from concurrent.futures import ProcessPoolExecutor
from hashlib import sha256
import json
from pathlib import Path

import numpy as np
import onnxruntime as ort
import soundfile as sf
from kokoro_onnx import Kokoro


def open_voice(model, voices):
    global voice
    options = ort.SessionOptions()
    options.intra_op_num_threads = 1
    options.inter_op_num_threads = 1
    session = ort.InferenceSession(str(model), sess_options=options, providers=["CPUExecutionProvider"])
    voice = Kokoro.from_session(session, str(voices))


def render_line(item):
    key, text = item
    speech, rate = voice.create(text, voice="af_heart", speed=1.0, lang="en-us")
    assert rate == 24000 and speech.ndim == 1 and len(speech) > rate // 4, key
    # Keep soft words audible without clipping an emphatic sound.
    rms = np.sqrt(np.mean(np.square(speech)))
    peak = np.max(np.abs(speech))
    assert np.isfinite(rms) and 0 < rms <= peak, key
    speech = speech * min(0.12 / rms, 0.8 / peak)
    # Silence on both sides gives the compressed stream room between clips.
    return np.pad(speech, (rate * 3 // 50, rate * 2 // 25))


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("model", type=Path)
    parser.add_argument("voices", type=Path)
    parser.add_argument("--workers", type=int, choices=range(1, 5), default=1)
    args = parser.parse_args()

    root = Path(__file__).resolve().parents[2]
    lines = json.loads(Path(__file__).with_name("en-lines.json").read_text(encoding="utf-8"))
    rate = 24000
    cue_sheet = {}
    with ProcessPoolExecutor(max_workers=args.workers, initializer=open_voice, initargs=(args.model, args.voices)) as pool:
        score = list(pool.map(render_line, lines.items()))
    cursor = 0
    for key, clip in zip(lines, score, strict=True):
        cue_sheet[key] = [round(cursor / rate, 5), round(len(clip) / rate, 5)]
        cursor += len(clip)

    out = root / "public" / "assets" / "audio"
    out.mkdir(parents=True, exist_ok=True)
    bank = out / ".radio-en.render.mp3"
    sf.write(bank, np.concatenate(score), rate, format="MP3")
    filename = f"radio-en-{sha256(bank.read_bytes()).hexdigest()[:12]}.mp3"
    bank.replace(out / filename)
    manifest = {"file": filename, "cues": cue_sheet}
    (root / "src" / "game" / "radio-en.json").write_text(json.dumps(manifest, indent=2) + "\n", encoding="utf-8")
    print(f"Recorded {len(cue_sheet)} lines, {cursor / rate:.1f} seconds.")


if __name__ == "__main__":
    main()
