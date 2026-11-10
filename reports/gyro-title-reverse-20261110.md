# Task 1: titlu explicit versus automat, ordine inversă

## Protocol

Aceeași specificație și suită externă ca în `gyro-title-ab-20261110`, același prompt cu pauză artificială de 12 s și încălzire separată, OpenCode V2 standalone, output 16384, warming oprit. Rulări secvențiale în ordine inversă: titlu explicit, apoi automat; workspaces și baze izolate, limită 240 s. SHA-256 spec `167fc46bb51b351a5d62e5c909a394cf5ad047e49f429c15ff949cd65aa5abbc`; acceptanță `00bcddba2a3901ccac351e6edc9fefcfa6dd2b6a42060f19a00ec5d6217e95e6`.

## Rezultate și verificare independentă

| Profil | Wall | Stare | Acceptanță externă | Teste proprii | Erori de tool observate |
|---|---:|---|---:|---:|---|
| Explicit | 212,405 s | Finalizat, exit 0 | 20/20 | 12/12 | shell exit 1 și shell exit 2 |
| Automat | 214,713 s | Finalizat, exit 0 | 20/20 | 14/14 | shell exit 1 |

Ambele suite externe și proprii au fost rerulate independent după finalizare. În explicit, primul shell exit 1 a reflectat un test propriu eșuat, iar exit 2 a provenit din încercarea de a citi `sample.csv` inexistent; ulterior testele au trecut. În automat, shell exit 1 a reflectat un test propriu eșuat inițial, corectat ulterior. Suitele proprii sunt diferite, deci numărul de teste nu este comparație directă de calitate.

## Metadate și cache

- Explicit: 14 cereri chat, toate cu unelte și HTTP 200; nicio cerere fără unelte. Primul prompt engine a avut 6104 tokeni, 0 reutilizați, 4288 ms prefill; următorul a reutilizat 6173/6994 tokeni.
- Automat: 17 cereri chat, una fără unelte, toate HTTP 200. Cererea fără unelte a început la 0,922 s, cea principală la 0,938 s; engine a procesat mai întâi promptul scurt de 572 tokeni, 1129 ms prefill și 4246 ms generare, apoi promptul principal de 6104 tokeni, 0 reutilizați, 4116 ms prefill. Următorul prompt a reutilizat 6248/7069 tokeni. Metadatele nu conțin textul cererii, deci cererea fără unelte este compatibilă cu generarea titlului, dar nu o identifică în mod cert.
- În ambele execuții s-au observat refuzuri de parking din cauza pragului de RAM. Acestea nu dovedesc cauza diferenței de latență.

## Interpretare

Rezultatele inverse replică asocierea dintre `--title` și absența cererii fără unelte, dar nu demonstrează o accelerare: diferența de 2,308 s dintre rulările complete este mică față de variația observată, iar conținutul și numărul pașilor diferă. În perechea anterioară, titlul automat a expirat la 240,092 s, cu 20/20 pe artefact parțial, iar titlul explicit a finalizat la 179,010 s, cu 20/20; acel timeout nu este un timp complet și nu se folosește pentru calcularea unui speedup. Nu s-a aplicat nicio schimbare globală.

Metadatele HTTP salvate sunt redactate (fără conținutul cererilor, răspunsuri sau antete); `*.jsonl` pot conține cod și apeluri tool. Dovezi: `results.json`, `http-metadata.json`, `*-engine.log`, `*-metrics.json`, `*-acceptance.txt`, `*.jsonl`, workspaces și `run_title.py`.
