# Gyro-S: test local `temperature=0`

## Ipoteză și metodă

Rulările istorice au produs trasee de generare și greșeli diferite, dar nu stabilesc samplingul drept cauză. Am testat ca ipoteză `temperature=0` numai în configurația proiectului, fără a schimba bugetul de reasoning, contextul sau outputul global. Rulări secvențiale OpenCode V2 standalone, Gyro-S, titlu explicit, warming OpenCode oprit; înainte de fiecare, aceeași cerere de încălzire, neinclusă în timpii de mai jos. Proxy localhost a păstrat doar metadate whitelistate, fără prompturi/răspunsuri/antete.

Sarcina scurtă este aceeași regresie controlată de normalizare a monedei într-un CLI existent folosită în `gyro-exclusive-repeat-20261110`; atât controlul, cât și temperatura zero au primit aceeași sursă inițială defectă și același prompt. Urmează o rulare cu temperatura zero a Task 1 complet, cu specificația originală și pauză artificială de 12 s; limita per proces a fost 240 s. Workspaces și baze izolate. Proxy: **6/6 cereri control fără câmpul temperature**, **9/9 cereri short-greedy și 17/17 full-greedy cu `temperature: 0`**, toate HTTP 200. Aceasta demonstrează câmpul trimis către gateway, nu determinism complet al runtime-ului.

## Rezultate

| Rulare | Wall | Stare | Acceptanță externă | Teste proprii independente | Erori tool |
|---|---:|---|---:|---:|---:|
| Task scurt, implicit | 33,334 s | finalizat, exit 0 | 20/20 | 4/4 | 0 |
| Task scurt, temperatura 0 | 43,812 s | finalizat, exit 0 | 20/20 | 2/2 | 0 |
| Task 1 complet, temperatura 0 | 240,262 s | TIMEOUT | 20/20 pe artefact parțial | 10/12 pe artefact parțial | 0 raportate |

La taskul complet, agentul a fost întrerupt la deadline înainte să-și execute testele proprii. Acestea au fost rulate independent după oprire și două eșuează. Acceptanța externă a fost rerulată independent, 20/20 pe fișierul parțial. Nu se confundă aceasta cu finalizarea. Testele proprii ale taskurilor scurte diferă și nu reprezintă scoruri comparabile ale calității.

## Cache și limite

Taskul complet a avut 16 cereri engine terminate în captura de log, 15 cu reuse. După o cerere ce a generat 8250 tokeni, următoarea a reutilizat 7299/15577 tokeni și a avut prefill de 5,988 s; logul include un refuz de parking în acea zonă. Aceasta nu stabilește cauza exactă a pierderii parțiale de prefix. Contoarele includ cereri auxiliare. Suitei externe nu i s-a modificat conținutul: SHA-256 `00bcddba2a3901ccac351e6edc9fefcfa6dd2b6a42060f19a00ec5d6217e95e6`.

O singură pereche scurtă și o singură rulare completă cenzurată de timeout nu demonstrează impactul asupra performanței sau calității. Varianta scurtă cu temperatura zero a fost mai lentă în această pereche și agentul a făcut 9 față de 7 tool calls. Nu s-a rulat un control complet contemporan în acest experiment, iar timpii istorici nu sunt A/B curat. Setarea nu a fost aplicată global; nu se recomandă pe baza acestor rezultate.

Dovezi: `results.json`, `http-metadata.json`, `*-warmup.json`, `*.jsonl`, `*-engine.log`, `*-metrics.json`, `*-acceptance.txt`, `*-os-io-samples.json`, workspaces și `run_temperature.py`. JSONL-urile pot conține cod; metadatele HTTP sunt redactate.
