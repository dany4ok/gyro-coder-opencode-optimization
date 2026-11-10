# Verificare experimentală Python înainte de editare

## Implementare și scop

Plugin local OpenCode V2 `syntax-plugin.js`, încărcat numai în workspace-ul experimental, pe `tool.execute.before`. Pentru un apel `edit` pe un fișier `.py` din workspace, cu `oldString` nevid care apare exact o dată, construiește în memorie o înlocuire și rulează `ast.parse` pe textul propus, trimis prin stdin către Python. Dacă verificarea eșuează, oprește apelul înaintea scrierii. Nu schimbă fișierul original, configurația globală sau baza partajată.

## Probă live de respingere și acceptare

Într-un workspace separat, agentul a propus intenționat `CENT = (`. Tool-ul `edit` a raportat eroare de sintaxă, iar următoarea editare a văzut același SHA-256 original ca înaintea respingerii: `cd511a62fd8c769ae62926a8d40b32eab95c20238bd80e97431bf9e2f4090a8b`. Apoi agentul a propus o editare validă a aceleiași linii, care a fost acceptată; hash-ul final `b3888f64d5ccb8d83be18b4463e583bd7b6999612c527124c7205859bdc96797` coincide cu hash-ul candidatului valid în logul hook-ului. `py_compile` a trecut, iar suita externă a trecut 20/20. Probe: `probe.jsonl`, `rejection-probe/syntax-hook.jsonl`, workspace și verificările independente din conversație. Sesiunea a terminat în 31,624 s, exit 0.

## Comparație secvențială pe task scurt

Același task derivat din Task 1 ca în `gyro-auto-syntax-20261110`: o regresie controlată într-un CLI existent, care înlocuiește `currency.upper()` cu `currency.lower()`, apoi cere agentului să o repare. Aceeași suită externă Task 1 a rulat înainte și după, același model, prompt, titlu explicit, output configurat global 16384, workspaces și baze izolate, timeout 120 s. Ordine control apoi plugin.

| Variantă | Extern înainte | Wall | Stare | Extern după | Tool calls / editări | Erori tool |
|---|---:|---:|---|---:|---:|---:|
| Control | 13/20 | 35,571 s | finalizat, exit 0 | 20/20 | 6 / 1 | 1 shell exit 2 |
| Pre-edit | 13/20 | 52,317 s | finalizat, exit 0 | 20/20 | 12 / 3 | shell exit 1, `edit` fără `newString`, shell exit 2 |

Hook-ul a verificat două editări valide; un apel `edit` fără argument obligatoriu a fost respins de schema tool-ului. Nu au existat editări cu sintaxă invalidă în benchmarkul scurt, deci calea de respingere a fost testată separat, nu ca efect cauzal în benchmark. Două trasee generate diferite și n=1 nu permit atribuirea diferenței de timp pluginului. Suita externă nu a fost modificată; SHA-256 `00bcddba2a3901ccac351e6edc9fefcfa6dd2b6a42060f19a00ec5d6217e95e6`.

## Limitări de siguranță

Pluginul este doar un prototip local: verifică o înlocuire literală unică, iar alte mecanisme de potrivire ale tool-ului, înlocuiri multiple, editări prin shell sau `write` nu sunt acoperite. Verificarea și scrierea nu sunt atomice; o modificare concurentă între ele poate invalida concluzia. Nu tratează complet symlink-uri sau fișiere Python deja invalide și poate împiedica o reparație incrementală. `ast.parse` nu verifică erori funcționale. Testele nu demonstrează o îmbunătățire generală de fiabilitate sau performanță; nu se recomandă aplicarea globală în această formă.

Dovezi: `results.json`, `*-before-acceptance.txt`, `*-after-acceptance.txt`, `baseline.jsonl`, `automatic-check.jsonl`, `probe.jsonl`, `rejection-probe/syntax-hook.jsonl`, `syntax-plugin.js`, `run.py`, workspaces. JSONL-urile pot conține cod și mesaje; nu sunt metadate redactate.
