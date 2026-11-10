# Task 2 după izolarea sintetică a pierderii de prefix

## Protocol

Gyro-S/OpenCode V2 standalone, același Task 2 Cache, prompt cu pauză artificială de 12 s și aceeași acceptanță externă, sesiuni/workspaces/baze izolate, 12 unelte, warming OpenCode off, output 16384. Rulări secvențiale cu aceeași încălzire separată: titlu automat, apoi titlu explicit `--title`, timeout 210 s fiecare. Suita externă SHA-256 `94918e3c5f113f6ed3c896740aac007261c821c9aa281937fa0e9518c82fb205`.

| Profil | Wall | Stare | Acceptanță externă | Teste proprii independente | Erori tool |
|---|---:|---|---:|---:|---|
| Titlu automat | 157,095 s | finalizat, exit 0 | 17/17 | 15/15 | 0 raportate |
| Titlu explicit | 139,423 s | finalizat, exit 0 | 17/17 | 23/23 | 1 shell exit 1 la un test propriu inițial, apoi corectat |

Suitele proprii au fost rerulate independent. Testele generate nu sunt identice și numărul lor nu reprezintă scor comparabil de calitate. Captura HTTP redactată arată o cerere fără unelte din 9 în varianta automată și niciuna din 10 în varianta explicită, toate HTTP 200. În varianta automată, cererea fără unelte a fost procesată înaintea primei cereri principale: engine a citit 571 tokeni fără reuse (1292 ms prefill, 3819 ms generare), apoi 6105 tokeni fără reuse (4204 ms prefill), după care reutilizarea pașilor principali a continuat. Nu s-a demonstrat în această rulare o întrerupere a unui prefix principal deja stabilit. O cerere fără unelte este compatibilă cu titlul, dar nu este identificată cu certitudine fără conținut.

Testul sintetic în `gyro-prefix-factor-20261110` a reprodus de două ori cache miss după o cerere auxiliară intercalată, în condiții de RAM disponibil scăzut. Acest benchmark real nu reproduce acea intercalare și nu dovedește că `--title` previne toate cache miss-urile sau că diferența de 17,672 s este cauzată de acesta. Ordinea este fixă, câte o rulare per profil, iar numărul de pași și testele generate diferă. Setarea este limitată la sesiuni CLI individuale; nicio modificare globală.

Date: `results.json`, `http-metadata.json` redactat, `*-metrics.json`, `*-engine.log`, `*-acceptance.txt`, `*.jsonl`, `run_title.py`, workspaces. JSONL-urile pot conține cod, spre deosebire de metadatele HTTP.
