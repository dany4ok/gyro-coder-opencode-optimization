# Task 1: diagnostic de generare și test buget temporar 4096

## Diagnostic din rulările anterioare Task 1

Strata a raportat înainte de primul `write` al implementării aproximativ **10660 tokeni de thinking în 122 s** în profilul implicit, iar cu `reasoning_effort=low` aproximativ **10539 tokeni în 122 s**. Pașii compleți au generat 13275 tokeni în 147,555 s și 12396 în 142,863 s, incluzând thinking și apelul de scriere. OpenCode a raportat `reasoning: 0` în contabilizarea acelor pași; logul Strata este sursa pentru separarea thinking de scriere. `low` nu a impus un plafon dur de thinking.

Pentru aceeași rulare, logurile arată multe accesări de experți pe file tier; un exemplu low raporta 326539 `file_blobs` și 342735,3 MB file-tier pentru pasul de 12396 tokeni. Acest număr **nu trebuie interpretat ca volum fizic SSD**, deoarece accesările pot fi servite din cache-ul Windows. Contoarele fizice pe întregul sistem pe ferestrele celor două rulări Task 1 anterioare au fost aproximativ 46622/53640 MiB; nu pot fi atribuite exclusiv Strata. Erorile tool au inclus `ls -la` invalid în PowerShell, corectat ulterior prin instrucțiune, și eșecuri reale ale testelor proprii.

## Testul nou

Două rulări OpenCode V2 secvențiale cu aceeași specificație Task 1, suită externă, prompt (incluzând pauza artificială de 12 s), încălzire, workspace/bază izolată, output 16384 și deadline de proces 240 s. Varianta `budget4096` adaugă numai în configurația proiectului `body.reasoning_budget_tokens=4096`; baseline nu are acel câmp. Proxy-ul local redactat confirmă **9/9 cereri chat baseline fără câmp** și **9/9 în varianta experimentală cu valoarea 4096**, toate cu HTTP 200. Strata a raportat `thinking budget reached (4096 tokens): wrapping up the thinking`. Nu s-au salvat prompturi, răspunsuri sau antete în `http-metadata.json`.

| Profil | Wall | Status | Acceptanță externă pe artefact parțial | Teste proprii după oprire |
|---|---:|---|---:|---:|
| Baseline | 240,118 s | TIMEOUT | 20/20 | 8/13 |
| Buget 4096 | 240,098 s | TIMEOUT | 7/20 | Nicio suită proprie creată |

Ambele procese au fost oprite la deadline. Acceptanța externă a fost rerulată independent și are aceleași rezultate; ea evaluează doar fișierul existent la acel moment. În varianta 4096, implementarea era în curs de editare și avea probleme de procesare CSV/antet; nu se poate presupune că acestea ar fi rămas în rezultatul final. Nici 20/20 pentru baseline nu îl transformă în execuție finalizată. Suita externă nu a fost modificată, SHA-256 `00bcddba2a3901ccac351e6edc9fefcfa6dd2b6a42060f19a00ec5d6217e95e6`.

| Profil | Prefill engine capturat | Decode capturat | Cereri / zero reuse | Parking refuzat | Citiri fizice sistem | RAM disponibil minim |
|---|---:|---:|---:|---:|---:|---:|
| Baseline | 12,070 s | 212,967 s | 8 / 2 | 3 | 51963,6 MiB | 189,2 MiB |
| Buget 4096 | 9,782 s | 174,282 s | 10 / 2 | 2 | 43353,2 MiB | 172,2 MiB |

Aceste sume includ cereri auxiliare și exclud o eventuală cerere întreruptă. Citirile fizice Windows sunt la nivel de sistem, pe ferestre de ~240,8/240,9 s, nu exclusiv Strata. Valorile nu sunt suficient de controlate pentru atribuirea cauzală a diferenței.

## Decizie

Plafonul 4096 nu a demonstrat finalizare în slot sau corectitudine comparabilă pentru Task 1 și **nu a fost aplicat global**. Un singur test, artefacte parțiale și diferențe stocastice nu dovedesc că plafonul produce întotdeauna eșecuri sau că afectează calitatea finală, dar oferă un motiv concret să nu fie adoptat fără mai multe teste. Configurația globală rămâne output 16384, fără buget explicit de reasoning, warming off.

Date: `results.json`, `http-metadata.json`, `*.jsonl`, `*-engine.log`, `*-metrics.json`, `*-os-io-samples.json`, `*-acceptance.txt`, workspaces și `run_task1_budget.py`. Logurile JSONL obișnuite pot conține cod/apeluri generate; doar metadatele HTTP sunt redactate.
