# OpenCode V2: semantica edit observată și repetarea uneltei experimentale

## Probe native

Am apelat executorul `edit` disponibil în OpenCode V2 2.2.6 printr-un tool diagnostic într-un workspace izolat (`gyro-native-edit-python-20261110`). Este o probă directă pe executorul capturat de plugin, nu o dovadă despre toate căile de execuție sau despre alte procese.

- Un fragment literal unic a fost înlocuit; o diferență internă de spații (`alpha=1` vs `alpha = 1`) a fost respinsă. Un substring literal dintr-o linie indentată a fost acceptat; acesta nu este matching flexibil, deoarece substringul există exact.
- Două apariții identice au fost respinse fără `replaceAll`; cu `replaceAll: true` ambele au fost înlocuite. `oldString` identic cu `newString` a fost respins.
- Executorul a acceptat pe un fișier `.py` înlocuirea `alpha = 1` cu `alpha = (` și a lăsat conținut Python invalid pe disc. Nu este automat o eroare de tool: `edit` este o unealtă de înlocuire textuală, nu o validare Python.
- În 30 de perechi `Promise.allSettled` cu înlocuiri simultane disjuncte asupra aceluiași fișier, ambele au reușit și ambele modificări au rămas. În 30 de perechi concurente care porneau de la același fragment și propuneau valori diferite, prima a reușit și a doua a fost respinsă. Această probă cu același executor, același proces și fixture-uri mici nu dovedește atomicitate generală sau comportament la acces concurent din alte procese; nu am inspectat întreaga implementare internă.

Rezultate brute: `[HOME]\AppData\Local\Temp\opencode\gyro-native-edit-python-20261110\native-results.json` și pluginul diagnostic aferent. O primă probă similară se află în `gyro-native-edit-20261110`.

## Remediu experimental

Am refolosit exclusiv în workspace-uri `safe_python_edit`: înlocuire literală unică pentru `txreconcile.py`, validare `ast.parse` și scriere pe același handle Windows exclusiv. `python -m unittest test_safe_edit -q`: **6/6** trecute, inclusiv invalid fără scriere, valid, fragment ambiguu/lipsă/no-op, CRLF și două cazuri de acces concurent cu alt proces. Este un tool separat, nu o caracterizare sau înlocuire globală a `edit`.

## Repetare benchmark scurt

Aceeași suită externă Task 1 și același task scurt ca `gyro-exclusive-edit-20261110`: un CLI existent cu regresie `currency.lower()` în loc de `upper()`, prompt identic în cele două brațe, Gyro-S/OpenCode V2 standalone, baze și workspaces izolate, deadline 120 s. Ordine inversată față de testul precedent: protejat A, control A, control B, protejat B. `safe_python_edit` a fost efectiv apelat în ambele rulări protejate prin Code Mode. SHA-256 suita externă `00bcddba2a3901ccac351e6edc9fefcfa6dd2b6a42060f19a00ec5d6217e95e6`.

| Rulare | Wall | Stare | Extern înainte → după | Test propriu rerulat | Erori tool |
|---|---:|---|---:|---:|---:|
| Protejat A | 48,379 s | finalizat | 13/20 → 20/20 | 2/2 | 0 |
| Control A | 24,808 s | finalizat | 13/20 → 20/20 | 1/1 | 0 |
| Control B | 27,540 s | finalizat | 13/20 → 20/20 | 3/3 | 0 |
| Protejat B | 27,944 s | finalizat | 13/20 → 20/20 | 2/2 | 0 |

În protejat A, agentul a scris și a rulat testul propriu în directorul temporar părinte `[HOME]\AppData\Local\Temp\opencode`, în afara workspace-ului, și l-a lăsat acolo. Testele proprii diferă în conținut, deci numărul lor nu este scor comparabil. Toate rulările au exit 0. Acceptanța indicată a fost executată independent de harness după fiecare execuție.

În prima pereche de două rulări per profil (`gyro-exclusive-edit-20261110`), timpii protejați erau mai mici; în repetarea de aici, controlul a fost mai rapid. N mic, trasee/tool calls diferite și un task foarte scurt nu susțin un speedup stabil sau concluzii despre Task 1 complet.

## Limitări

Nu există remediere globală validată: unealta protejată este restrânsă la un singur fișier, exact un match, UTF-8 și Windows; `write`/shell pot ocoli protecția. Un crash în timpul scrierii nu are garanție de rollback atomic; recuperarea excepțiilor este best-effort. Nu acoperă complet symlink/junction, matching OpenCode `replaceAll`, editări multi-fișier sau corectitudine semantică. Nu am aplicat setări globale. Dovezi brute în `results.json`, `*.jsonl`, `*-before-acceptance.txt`, `*-after-acceptance.txt`, `test_safe_edit.py`, `safe_edit.py`, `syntax-plugin.js`, `run.py` și workspaces; JSONL-urile pot conține cod.
