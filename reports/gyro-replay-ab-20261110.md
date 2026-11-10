# Task 1: reasoning istoric, reutilizare prefix și test local

## Diagnostic din rularea anterioară

În `gyro-tools-reverse-task1-20261110/restricted-task1`, un pas înainte de `write` a raportat 12305 tokeni reasoning în OpenCode. Următoarele două cereri engine au reutilizat doar 5375/17686 și 5375/19487 tokeni; logul a raportat refuzuri de parking asociate presiunii RAM. Această asociere nu arată singură dacă recitirea provine din serializarea reasoning-ului, starea cache-ului sau altă diferență.

## Protocol nou

Două rulări secvențiale Task 1 complet în OpenCode V2 standalone, Gyro-S, aceeași spec și suită externă, același prompt inclusiv pauza artificială de 12 s, titlu explicit, output 16384, warming OpenCode oprit și deadline mărit la 360 s. Încălzire separată identică, neinclusă în wall. Workspaces și baze izolate. Controlul retransmite normal cererile. În varianta experimentală, un proxy localhost elimină `reasoning_content` numai din mesajele assistant care conțin tool calls, înainte de a le transmite către Strata; reasoning-ul nou nu este limitat. Această schimbare poate pierde context relevant și nu este activată global.

Proxy-ul salvează doar prezența/numărul de câmpuri, lungimi, poziția primei diferențe dintre mesaje și alte metadate whitelistate, nu conținutul lor, hash-uri sau antete. Comparația mesajelor se face în memorie; `first_changed_message: null` după prima cerere înseamnă că niciun mesaj dintre cele comparate nu a avut conținut JSON diferit, dar nu garantează că tool schema, requestul integral sau promptul tokenizat au rămas identice. Logurile obișnuite `*.jsonl` conțin cod și mesaje generate.

## Rezultate

| Variantă | Wall | Stare | Extern | Teste proprii independente | Erori tool |
|---|---:|---|---:|---:|---|
| Replay normal | 274,874 s | finalizat, exit 0 | 20/20 | 12/12 | shell exit 1 la teste proprii, apoi corectate; shell exit 2 pe `in.csv` inexistent |
| Fără reasoning istoric al tool calls | 360,115 s | TIMEOUT | 20/20 pe artefact parțial | niciun fișier de teste proprii creat | `edit` cu `oldString` și `newString` lipsă |

Acceptanța externă a fost rerulată independent, cu același rezultat. Timeoutul nu este succes: agentul experimental nu terminase și nu crease teste proprii. Nu se poate calcula speedup față de un timp de finalizare necunoscut. Suita externă a rămas neschimbată, SHA-256 `00bcddba2a3901ccac351e6edc9fefcfa6dd2b6a42060f19a00ec5d6217e95e6`.

## Telemetrie și verificarea intervenției

- Controlul a avut 12 cereri chat capturate, toate HTTP 200; metadatele arată reasoning istoric păstrat. După un pas cu 12305 tokeni reasoning raportați de OpenCode, următoarea cerere engine a reutilizat **19560/19578 tokeni**. Așadar reasoning-ul lung nu provoacă inevitabil o pierdere de prefix. Cererile de control au avut prefixul mesajelor JSON anterioare neschimbat în comparația redactată.
- Experimental: 9 cereri chat capturate, toate HTTP 200. În ultima, 71530 caractere de reasoning istoric pe 8 mesaje de tool call existau înaintea intervenției și 0 după; sunt caractere, nu tokeni. Proxy-ul a transmis efectiv corpul modificat cu `Content-Length` actualizat.
- Log engine capturat: control 11,827 s prefill și 245,174 s decode, 13 linii terminate și un refuz parking; experimental 18,379 s prefill și 267,469 s decode, 8 linii terminate și nouă mesaje de refuz parking. Liniile de log pot include cereri de la limitele ferestrei, iar cererea întreruptă nu este contabilizată complet. Presiunea RAM și traseele diferă; nu se poate atribui diferența de latență exclusiv eliminării reasoning-ului.
- Controlul a generat 21971 tokeni în liniile engine capturate, experimentalul 24280 înainte de oprire. Rularea experimentală a avut pași cu 6622 și 7226 tokeni reasoning raportați, deci eliminarea istoricului nu a limitat generarea nouă.

## Concluzie

Eliminarea reasoning-ului istoric nu este validată ca optimizare: în această singură pereche a expirat și a lăsat fără teste proprii, în timp ce controlul a terminat. Nu se demonstrează că intervenția a cauzat timeoutul sau că ar avea mereu același rezultat, deoarece generarea și condițiile de cache variază. Nu s-a schimbat configurația globală și nu se recomandă eliminarea reasoning-ului istoric pe baza acestui test.

Dovezi: `results.json`, `http-metadata.json`, `*-engine.log`, `*-metrics.json`, `*-acceptance.txt`, `*-os-io-samples.json`, `*.jsonl`, workspaces și `run_replay.py`.
