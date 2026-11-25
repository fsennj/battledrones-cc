# XR-Stimmen und Hörabnahme · 25. November 2026

## Stand im Spiel

- Am XR-Tisch sind Auswahl, Zielbestätigung, Flug, Funkcheck und alpine Atmosphäre angebunden. Achensee, Inntal und Zillertal haben eigene Umgebungsprofile. Auswahl, Bewegung, Missionsfortschritt und Stummschaltung wurden im Browser geprüft. Die Hör- und Richtungsabnahme am physischen Headset ist offen.
- 18 Spielclips decken Nordtirol, Zürich und Norditalien ab. Sprache und Stimmton sind am Tisch getrennt einstellbar. Die Laufzeitdateien bestanden den technischen Check mit 5/5 Prüfpunkten. Die subjektive Hörfreigabe ist ein eigener Schritt.
- Die Hörabnahme bietet regionale Vergleichsaufnahmen und vier Kriterien. Eine Freigabe erfordert mindestens vier Sterne pro Kriterium. Bei Synthese-Takes kann eine niedrigere Wertung einen Neurender anstoßen. Die Originalausschnitte mit abweichendem Wortlaut dienen der Hörabnahme.

## Nordtirol

Der blinde Vergleich mit sechs Paaren ergab im Mittel 1,83 Sterne für den LoRA-Piloten und 1,33 für Chatterbox ohne Adapter. Alle fünf eindeutigen Präferenzen gingen an die Variante auf Position A. Das Ergebnis reicht für eine Dialektfreigabe nicht aus. Die Nachprüfung ging deshalb zu echten Originalausschnitten über.

| Clip | Vorliegender Take | Aktuelle Hörwertung |
| --- | ---: | --- |
| Wasp-Auswahl | 5 | offen |
| Wasp-Bewegung | 5 | offen |
| Condor-Bereitmeldung | 5 | offen |
| Condor-Bewegung | 5 | offen |
| Funkcheck | 5 | offen |
| Missionsabschluss | 6 | offen |

Die Übersicht wurde anhand der lokal gespeicherten Wertungen und der Prüfsummen der sechs aktuellen WAV-Dateien erstellt. Historische Wertungen gehören jeweils zur damaligen Aufnahme.

**Missionsabschluss, Take 6.** Petra Schattanek meldet nach einer praktischen Tagfalter-Erhebung „So, und somit hast du die erste Erhebung schon gemacht.“ Sie ist in Rum geboren und in Fulpmes aufgewachsen. Der Schnitt von 11:28,78 bis 11:32,25 dauert 3,47 Sekunden und wurde im Browser vollständig abgespielt. Take 5 ist in derselben Ansicht unter **Vorherigen Take anhören** verfügbar. [Originalszene](https://www.youtube.com/watch?v=EG5LRDzHCQk&t=688s) · [Herkunftsnachweis, S. 210](https://www.zobodat.at/pdf/ENTAU_0024_0209-0212.pdf) · [Lizenz CC BY 4.0](https://creativecommons.org/licenses/by/4.0/deed.de)

## Wiedereinstieg am 26. November

1. Im bestehenden Projekt-Checkout `node tools/xr-voice-review.mjs` starten und den [Missionsabschluss](http://127.0.0.1:5192/#de-AT.command.complete) öffnen. Der Server lädt den vorhandenen Stand aus `.xr-voice-review/` einschließlich der Blindrunde. Diese lokalen Daten enthalten die WAVs und gespeicherten Wertungen.
2. Take 6 gegen den vorherigen Take und die Nordtiroler Hörreferenz bewerten. Danach die fünf übrigen Nordtiroler Takes prüfen.
3. Die Aufnahmequellen, Schnitte und bisherigen Browserprüfungen stehen im lokalen `XR-SOUNDDESIGN.md`. Die Schnittdaten für Take 6 stehen in `art/xr/sound/voices/tirol-take6.json`.

Dieses Dokument ist die Übergabe für den Arbeitsstand im lokalen Checkout. Der GitHub-Stand umfasst die Markdown-Übergabe.
