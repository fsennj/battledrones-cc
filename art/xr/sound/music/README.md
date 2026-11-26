# Battle Drones XR · Musik / Music

[Deutsch](#deutsch) · [English](#english)

## Deutsch

Das ist ein erster Arbeitsstand. Musikalisch gibt es noch sehr viel aufzuholen, vor allem beim Wiedererkennungswert der Riffs, bei den Tiroler Instrumenten und bei der Mischung im Spiel. Irgendwo muss man anfangen. Diese Sammlung gibt uns Material, das wir gemeinsam anhören, vergleichen und gezielt weiterentwickeln können.

| Datei oder Ordner | Verwendung |
| --- | --- |
| [Tiroler Eisen](tiroler-eisen.mp3) und [Stubai Stomp](stubai-stomp.mp3) | Zwei erste Klangproben für die ernste und die Tirol-Fun-Richtung. |
| [Stahltrieb · Kurzskizzen](stahltrieb/README.md) | 50 kurze Entwürfe zum schnellen Vergleichen von Riffs, Rhythmus und Instrumentierung. |
| [Stahltrieb · Langfassungen](stahltrieb/langfassungen/README.md) | 50 vollständige Entwürfe für die Hörabnahme, davon 35 **Ernst** und 15 **Tirol-Fun**. Jeder Titel dauert 3:30 bis 4:00. |
| [Wiedergabeliste der Langfassungen](stahltrieb/langfassungen/Stahltrieb-Langfassungen.m3u8) | Alle 50 MP3s in Albumreihenfolge für einen lokalen Medienplayer. |
| [Browser-Hörabnahme](../../../../tools/xr-music-review.mjs) | Langfassungen anhören, je 1–5 Sterne vergeben und Titel für das Spiel vormerken. |

Im Projektordner mit Node.js `node tools/xr-music-review.mjs` ausführen und [die Hörabnahme öffnen](http://127.0.0.1:5193/). Über **Ernst** und **Tirol-Fun** wechselst du die Liste. **Beste Wertung** sortiert nach Sternen. Mit **Fürs Spiel** markierst du Titel. **Auswahl exportieren** lädt die markierten Stücke samt Wertung und Dateipfad als `stahltrieb-auswahl.json`. Der Server speichert Wertungen lokal in `.xr-music-review/ratings.json`. Die Vormerkung dient der späteren Spielmischung und Freigabe.

### Nachtkonvoi im XR-Tisch testen

Die [27-Sekunden-Hörprobe](../ton-1-nachtkonvoi.wav) verbindet Musik, Briefing-Stellvertreter, Auswahl, Zielbestätigung, Wasp-Motor, Funk und Abschlussmeldung. Der [XR-Patch](../nachtkonvoi-xr.patch) enthält die Live-Mischung, den Schutz vor einem doppelten Funkstart am Wegpunkt und den leiseren Schwebeflugpegel bis zum Ende der Meldung. Der [Audio-Smoke-Test](../../../../tools/xr-audio-smoke.mjs) verwendet für den Wasp-Klick jetzt die tatsächliche Kamera und Canvas-Fläche.

Der Chrome-Link benötigt den lokalen XR-Checkout mit angewendetem Patch und der [Nachtkonvoi-MP3](stahltrieb/langfassungen/08-nachtkonvoi.mp3) im gleichen Projektpfad. Für einen XR-Checkout vor der Integration zuerst `git apply --check <Pfad-zum-Patch>` ausführen und danach den Patch mit `git apply <Pfad-zum-Patch>` anwenden. Vite im XR-Checkout mit `npm run dev` starten. In der [Zillertal-Testszene in Chrome](http://127.0.0.1:5173/xr.html?map=zillertal&ton=nachtkonvoi) auf **Nachtkonvoi · Funkprobe im Flug** klicken.

Im normalen Chrome wurden alle drei Funkstationen bis „Mission abgeschlossen“ geprüft. Der Desktop-Audio-Smoke inklusive Wasp-Klick und Funküberlagerung bestand in 72,39 s, der TypeScript-Check ebenfalls. Die erste Funkmeldung lief einmal vollständig über 3,62 s. Im gemessenen Überlappungsfenster lag sie rund 10,1 dB über dem Motor. Whisper large-v3 erkannte aus dem gemischten Spielausgang den vollständigen Satz „Funküberprüfung erledigt. Empfang ist klar.“ Die persönliche Hörfreigabe auf Lautsprechern und im Headset steht aus.

### Produktion und Prüfstand

1. **Entwurf mit Codex.** Aus dem Sounddesign-Briefing entstanden eigene Instrumentalbeschreibungen, Titel, Tempi und Arrangements. Die ernste Fassung verwendet Industrial Rock, Groove Metal und Breakbeats. Tirol-Fun setzt unter anderem Steirische Harmonika, Hackbrett und Maultrommel im Arrangement ein. Als Eingabe für die Musikgenerierung dienten Textbeschreibungen und Seeds.
2. **Lokale Musikgenerierung.** Codex übergab die Renderaufträge an ComfyUI 0.45.4 auf einer RTX 5090. ACE-Step 1.5 XL Turbo BF16 erzeugte die Musik. Für die Text- und Audiocode-Konditionierung kamen `qwen_0.6b_ace15.safetensors` und `qwen_1.7b_ace15.safetensors` zum Einsatz. Der Workflow verwendete Euler mit acht Schritten, Scheduler `simple` und Flow-Shift 3. `ace_1.5_vae.safetensors` dekodierte das Ergebnis für den FLAC-Export. Die zusammengezählte Renderzeit der erfolgreichen Langfassungen betrug 778,87 s. Tokenzahlen wurden nicht erfasst. [Modellkarte und Modelllizenz](https://huggingface.co/Comfy-Org/ACE-Step-1.5)
3. **Schnitt und Export.** Die Langfassungen wurden mit erweiterten Arrangements neu gerendert. Python mit NumPy, SciPy, SoundFile und PyAV schnitt überschüssige Stille, setzte kurze Blenden und passte den Pegel an. Der Export erfolgte als Stereo-MP3 mit 48 kHz und 320 kbit/s. Alle 50 Langfassungen wurden vollständig dekodiert. Ihre geschätzten True Peaks liegen zwischen −4,62 und −2,05 dBTP. [Dauern und Messwerte](stahltrieb/langfassungen/README.md)
4. **Abnahme.** Wiedergabe, Vorspulen, Sternwertung, Speicherung über Neustart, Rangfolge und Export wurden geprüft. Die musikalische Auswahl und die Mischung mit Funk und Spieleffekten stehen zur Projektabnahme offen.

## English

This is an early working draft. There is still a lot of ground to make up, especially on distinctive riffs, the Tyrolean instruments and the in-game mix. We have to start somewhere. This collection gives us material to listen to together, compare and develop further.

| File or folder | Purpose |
| --- | --- |
| [Tiroler Eisen](tiroler-eisen.mp3) and [Stubai Stomp](stubai-stomp.mp3) | Two initial demos for the serious and Tyrolean fun directions. |
| [Stahltrieb short demos](stahltrieb/README.md) | 50 short drafts for comparing riffs, rhythm and instrumentation. |
| [Stahltrieb full-length versions](stahltrieb/langfassungen/README.md) | 50 complete drafts for review, with 35 **Serious** and 15 **Tyrolean fun** tracks. Each runs from 3:30 to 4:00. |
| [Full-length playlist](stahltrieb/langfassungen/Stahltrieb-Langfassungen.m3u8) | All 50 MP3s in album order for a local media player. |
| [Browser review](../../../../tools/xr-music-review.mjs) | Listen to full tracks, give each 1–5 stars and shortlist tracks for the game. |

Run `node tools/xr-music-review.mjs` with Node.js from the checkout and [open the review](http://127.0.0.1:5193/). Switch between **Serious** and **Tyrolean fun**. Use **Highest rated** to sort by stars and **For the game** to shortlist a track. **Export selection** downloads the selected tracks, ratings and asset paths as `stahltrieb-auswahl.json`. The server saves ratings locally in `.xr-music-review/ratings.json`. The shortlist is for the subsequent in-game mix and approval.

### Test Nachtkonvoi on the XR tabletop

The [27-second preview](../ton-1-nachtkonvoi.wav) combines the score, a briefing stand-in, selection and destination cues, the Wasp engine, radio and the completion report. The [XR patch](../nachtkonvoi-xr.patch) contains the live mix, prevents waypoint arrival from restarting a radio line, and keeps the motor at quiet hover power until the line ends. The [audio smoke test](../../../../tools/xr-audio-smoke.mjs) now uses the actual camera and canvas to click the Wasp.

The Chrome link requires the local XR checkout with the patch applied and the [Nachtkonvoi MP3](stahltrieb/langfassungen/08-nachtkonvoi.mp3) at the same project path. On a pre-integration XR checkout, run `git apply --check <path-to-patch>` followed by `git apply <path-to-patch>`. Start Vite in the XR checkout with `npm run dev`. In the [Zillertal Chrome test scene](http://127.0.0.1:5173/xr.html?map=zillertal&ton=nachtkonvoi), click **Nachtkonvoi · In-flight radio test**.

The regular Chrome tab reached all three radio stations and completed the mission. The desktop audio smoke test, including Wasp selection and the radio overlap, passed in 72.39 s. TypeScript also passed. The first line played once for the full 3.62 s. During the measured overlap, speech was about 10.1 dB above the engine. Whisper large-v3 transcribed the entire line from the mixed game output. Personal listening review on speakers and in the headset is pending.

### Production and verification

1. **Drafted with Codex.** The sound design brief informed original instrumental descriptions, titles, tempos and arrangements. The serious cues use industrial rock, groove metal and breakbeats. Tyrolean fun arrangements include button accordion, hammered dulcimer and jaw harp. Musical generation used text prompts and seeds as inputs.
2. **Generated locally.** Codex submitted jobs to ComfyUI 0.45.4 on an RTX 5090. ACE-Step 1.5 XL Turbo BF16 generated the music. The text and audio-code conditioning used `qwen_0.6b_ace15.safetensors` and `qwen_1.7b_ace15.safetensors`. The workflow used eight Euler steps, the `simple` scheduler and a flow shift of 3. `ace_1.5_vae.safetensors` decoded the output for FLAC export. Successful full-length runs took 778.87 s in total. Token counts were unavailable. [Model card and model license](https://huggingface.co/Comfy-Org/ACE-Step-1.5)
3. **Edited and exported.** The tracks were re-rendered with longer arrangements. Python with NumPy, SciPy, SoundFile and PyAV trimmed excess silence, applied short fades and adjusted levels. The exports are 48 kHz stereo MP3s at 320 kbit/s. All 50 tracks were fully decoded in verification. Estimated true peaks range from −4.62 to −2.05 dBTP. [Durations and measurements](stahltrieb/langfassungen/README.md)
4. **Reviewed technically.** Playback, seeking, star ratings, persistence after restart, ranking and export were tested. Track selection and mixing with radio and game effects are pending project review.
