# Kufstein und Südfurt · Tagesstand vom 25. November 2026

## Spielbarer Stand

**Brückenkopf im Inntal** ist im lokalen Projekt über `kufstein-konvoi.html` spielbar. Im letzten Chrome-Durchlauf wurden eine Fahrzeughalle gebaut, drei Stinger produziert und ein Zwischenstand wieder aufgenommen. Der Einsatz endete mit dem erreichten Depotziel. Eigene Trupps und Fahrzeuge tragen Olivgrün. Auswahl und Produktionsleiste zeigen die passenden Modellporträts, auch für Pritschenwagen und Werkstattwagen.

Im Kufsteiner Stadtmodell erreichen Soldaten, Pritschenwagen und Stinger den Festungshof und den Bahnhofsplatz jeweils mit einem Marschbefehl. **Am Bauhof** stehen zwei provisorische Hütten. Ein Mastodon beschädigt eine Hütte nach drei Spielsekunden Kontakt und hält an. Nach einem neuen Fahrbefehl braucht er sechs weitere Kontaktsekunden, um über den Schutt weiterzufahren. Der Bewegungstest prüft auch das Laden eines Zwischenstands während des zweiten Anlaufs.

## Referenz für die Südfurt-Bots

In der Riverlands-Südfurt gelten die Depotwache an der Nordkante, der Stinger-Zielwechsel auf den Raketentrupp und der bisherige Furt-Wegpunkt mit dem um ein Feld nördlicheren Marschziel. Vorstoß, Sicherung und Wirtschaft spielten beide Laborvarianten mit denselben zwölf Tuning- und sechs Kontrollseeds bei einfachem Einkommen.

| Vergleichsgruppe | Siege | Mittlere Depotreserve von 800 | Stinger am Depot |
| --- | ---: | ---: | ---: |
| Alle Südfurt-Partien | 108/108 | 753,99 | 426 |
| Darin die 33 zuvor auffälligen Partien | 33/33 | 754,79 | 132 |
| Wirtschaftsbot mit Labor, Seed 911 | 1/1 | 800 | 4 von 4 gebauten |

Bei den 33 Partien stieg die mittlere Reserve gegenüber dem früheren Marschziel von 685,19 auf 754,79. 32 Depots behielten mehr Reserve, eines weniger. Die 132 Ankünfte blieben gleich. Der anschließende Vergleich von Versuch und Standard reproduzierte mit den 108 Talbrücken-Kontrollen insgesamt 216 Partien und 1.599 Zwischenprüfsummen. Das Seed-911-Replay des Wirtschaftsbots mit Labor endet bei Tick 751 mit der Prüfsumme `fbcf0540`.

Die lokalen Referenzen liegen in `_test/suedfurt-standard/abnahme.json` und `_test/suedfurt-standard/endstand/`. Die Seeds stehen in `tools/tirol/inntal-series.ts`. Zum Wiederholen aus dem Projektverzeichnis zwei neue Ausgabeordner verwenden.

```sh
npm run playtest:inntal -- --riverlands --set tuning --out _test/wiederaufnahme-26/tuning --compare _test/suedfurt-standard/endstand/tuning/bericht.json
npm run playtest:inntal -- --riverlands --set kontrolle --out _test/wiederaufnahme-26/kontrolle --compare _test/suedfurt-standard/endstand/kontrolle/bericht.json
```

## Wiedereinstieg am 26. November

**Offen ist die enge Gasse außerhalb des Bauhofs.** Dafür gibt es bislang weder einen Karteneinbau noch ein Testergebnis. Als Erstes eine fiktive Gasse mit einem Haus und einem Ziel hinter der Engstelle in die reguläre Stadtmission setzen.

1. Mit Stadtmissions-Seed `204107` drei frische Partien starten. Jeweils vom gleichen Startfeld dasselbe Ziel hinter dem Haus anklicken.
2. Soldatentrupp und Stinger müssen in je einem Durchgang am intakten Haus vorbeikommen. Für beide die tatsächliche Passage und das Erreichen des Ziels prüfen.
3. Beim Mastodon den Halt vor dem Haus nach dem ersten Befehl prüfen. Abwarten und denselben Zielpunkt erneut anklicken. Erst nach dem zweiten Befehl darf er die Engstelle räumen und das Ziel erreichen.

Der bestehende Bauhoftest in `tests/kufstein-gassen.test.ts` und die Hindernislogik in `src/kufstein/yard-huts.ts` sind die Einstiegspunkte. Der letzte protokollierte Vitest-Lauf bestand alle 1.800 Tests mit verlängertem Zeitlimit. Der Produktionsbuild war erfolgreich. Für den separaten Pages-Archivtest fehlt auf diesem Windows-Rechner das Programm `zip`.
