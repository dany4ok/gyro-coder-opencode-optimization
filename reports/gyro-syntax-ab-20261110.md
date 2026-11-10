# Task 1: diagnostic IndentationError și verificare temporară de sintaxă

## Cauza observată

Reconstrucția în memorie a apelurilor `write` și `edit` din `gyro-fixture-ab-20261110/baseline.jsonl` reproduce exact fișierul lăsat pe disc. Scrierea inițială și prima editare compilau. A doua editare a înlocuit doar începutul blocului `PARSERS` cu un bloc întreg, lăsând vechile linii de final după acesta: `IndentationError` la linia 43. O editare ulterioară a mutat eroarea la linia 35, unde a rămas. Trei editări ulterioare nu au eliminat-o; primul unittest a semnalat corect eroarea. Nu a fost demonstrat un defect al tool-ului: fiecare fragment vechi apărea o singură dată, iar tool-ul a aplicat textul cerut.

## Test secvențial

OpenCode V2 standalone, Gyro-S, același Task 1, prompt și pauză artificială de 12 s, încălzire, titlu explicit, output 16384, warming oprit și limită de 240 s. Ordine baseline, apoi workspace cu `AGENTS.md` local care cere `python -m py_compile` după fiecare editare și înlocuirea blocurilor complete. Workspaces/baze izolate; nicio modificare globală. Suită externă SHA-256 `00bcddba2a3901ccac351e6edc9fefcfa6dd2b6a42060f19a00ec5d6217e95e6`.

| Profil | Stare | Acceptanță externă la oprire | Teste proprii rerulate la oprire | Erori tool raportate |
|---|---|---:|---:|---:|
| Baseline | TIMEOUT 240,099 s | 20/20 pe artefact parțial | 14/14 | 5 shell exit nenul |
| Instrucțiune sintaxă | TIMEOUT 240,091 s | 11/20 pe artefact parțial | 13/19 | 1 shell exit nenul |

Rezultatele au fost rerulate independent după oprire. În varianta cu instrucțiune, 9 din 20 teste externe eșuează, multe din cauza antetului CSV numărat ca înregistrare; compilarea finală a ambelor fișiere Python trece. Rezultatele sunt parțiale: agentul nu a terminat și nu se poate spune dacă ar fi corectat erorile. Diferența dintre cele două artefacte nu demonstrează un efect cauzal al instrucțiunii.

## Respectarea instrucțiunii

În varianta cu instrucțiune au fost 9 editări și o singură comandă `py_compile`, imediat după a șasea editare; trei editări ale implementării au urmat ulterior fără compilare capturată. Compilarea a fost deci grupată, nu executată după fiecare editare. Sintaxa finală era validă, dar asta nu dovedește corectitudinea semantică. Baseline a avut 6 editări și nicio comandă explicită `py_compile`; testele sale au verificat indirect importarea codului.

Nu există dovadă suficientă că instrucțiunea îmbunătățește fiabilitatea sau performanța și ea nu a fost aplicată global. Date: `results.json`, `*.jsonl`, `*-acceptance.txt`, `*-engine.log`, `*-metrics.json`, `http-metadata.json`, workspaces și `run_syntax.py`. Metadatele HTTP sunt redactate; logurile JSONL pot conține cod.
