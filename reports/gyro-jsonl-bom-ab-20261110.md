# PowerShell 5.1, UTF-8 BOM și fixture JSONL

## Reproducere controlată

În `gyro-edit-schema-proxy-20261110/baseline.jsonl`, agentul a scris un fișier JSONL cu `Set-Content -Encoding UTF8` și a observat apoi `JSONDecodeError: Unexpected UTF-8 BOM`; a remediat fixture-ul. Pe PowerShell Windows 5.1.26100.9711, aceeași operație asupra unei singure tranzacții valide scrie prefixul `ef bb bf`. `txreconcile.py` a ieșit 0, dar raportul a indicat **0 valide / 1 invalidă**. Cu `[System.IO.File]::WriteAllText(path, text, [System.Text.UTF8Encoding]::new($false))`, fișierul începe cu `7b 22 69`, iar raportul indică **1 validă / 0 invalide**. Acest comportament de ieșire este conform cerinței CLI: procesarea unei înregistrări invalide poate totuși ieși 0; validitatea datelor se verifică în raport.

Proba este izolată în `probe/`, păstrează Unicode și nu schimbă CLI-ul sau setările sistemului. Demonstrează interacțiunea versiunii PowerShell cu un cititor care nu acceptă BOM, nu că toate JSONL-urile cu BOM sunt invalide conform oricărui contract.

## Comparație secvențială

Task scurt derivat din Task 1: același CLI existent, creare `sample.jsonl` cu o tranzacție conținând `résumé`, rulare CLI și verificarea raportului semantic 1 validă / 0 invalide; fără modificarea CLI-ului. OpenCode V2 standalone, Gyro-S, titlu explicit, output 16384, warming OpenCode oprit, încălzire separată, deadline 120 s și baze/workspaces izolate. Controlul este urmat de un workspace cu `AGENTS.md` local care recomandă UTF-8 fără BOM când BOM nu este cerut și verificarea raportului, nu doar a exit-ului.

| Profil | Wall | Stare | Suită externă Task 1 | Fixture verificat independent | Erori tool |
|---|---:|---|---:|---|---:|
| Control | 28,439 s | finalizat, exit 0 | 20/20 | fără BOM; Unicode intact; 1 validă / 0 invalide | 0 |
| Instrucțiune locală | 21,089 s | finalizat, exit 0 | 20/20 | fără BOM; Unicode intact; 1 validă / 0 invalide | 0 |

Ambele suite externe au fost rerulate independent și au SHA-256 neschimbat `00bcddba2a3901ccac351e6edc9fefcfa6dd2b6a42060f19a00ec5d6217e95e6`. Implementările CLI rămân byte-identice, SHA-256 `ba8bbd3f66076629d589fab4df3afc674767b511c1b52d85a27d760eb0ff605b`. Ambele fixture-uri au `id` cu codepoints `72 e9 73 75 6d e9`, suma 12.34, moneda usd, status settled și data 2026-01-01. Prima verificare independentă a Unicode a afișat în mod greșit `unicode_correct=False` din cauza codării scriptului transmis prin PowerShell; o a doua verificare cu escape-uri `\u00e9` și inspecția codepoint-urilor a confirmat integritatea.

## Interpretare

Ambele variante au folosit tool-ul `write` pentru a crea fișierul, nu `Set-Content`; controlul nu a reprodus problema. Astfel absența BOM nu demonstrează că instrucțiunea previne erori mai fiabil, iar o pereche cu trasee diferite nu stabilește efectul de 7,350 s asupra latenței. Nu se extrapolează la Task 1 complet. Nu s-a aplicat global instrucțiunea. Delta ferestrei de cereri din `results.json` este invalidă ca contor cumulativ după 500 de intrări și nu este utilizată.

Dovezi: `probe/`, `baseline/`, `utf8-guidance/`, `results.json`, `*.jsonl`, `*-acceptance.txt`, `http-metadata.json`, `run_title.py`. JSONL-urile de agent pot conține cod și mesaje; metadatele HTTP sunt redactate.
