# Gyro-S: verificare HTTP redactată și A/B reasoning low

## Metodă și confidențialitate

Proxy temporar `127.0.0.1` → Strata gateway `127.0.0.1:47831`, cu streaming transmis mai departe. Proxy-ul a păstrat doar metadate whitelistate: profil, tipul endpointului, model, prezența/valoarea `reasoning_effort`, prezența bugetului de reasoning, limitele de output, stream și status HTTP. Nu a scris prompturi, răspunsuri sau antete în `http-metadata.json`. Atenție: logurile obișnuite ale benchmarkului `*.jsonl` conțin apeluri tool și codul generat, ca în testele anterioare; metadatele redactate nu trebuie confundate cu acele loguri.

Rulări secvențiale, OpenCode V2 standalone, aceeași instanță Gyro-S, același task/prompt și pauză artificială 12 s, workspaces și baze izolate, output 16384, warming OpenCode oprit. Înaintea fiecăreia: aceeași încălzire separată de 2422 tokeni, răspuns OK, 3,164/2,837 s, excluse din timpii taskurilor. `effort-low` are `body.reasoning_effort=low` numai în proiect; baseline nu are acest câmp.

## Verificarea pe fir

- Baseline: **11/11** cereri chat prin proxy fără câmpul `reasoning_effort`; HTTP 200 pentru toate.
- Varianta locală: **9/9** cereri chat au avut `reasoning_effort: low`; HTTP 200 pentru toate. Bytes ai requestului au fost transmiși nemodificați în upstream; astfel configurarea chiar a ajuns la gateway, nu este doar un fișier de configurare.
- Câte o cerere auxiliară din fiecare profil nu avea o limită output explicită; ceilalți pași aveau `max_completion_tokens=16384`.

## Corectitudine și latență

| Profil | Wall | Status | Acceptanță externă independentă | Teste proprii independente | Pași / tool calls | Erori |
|---|---:|---|---:|---:|---:|---|
| Implicit | 142,762 s | finalizat, exit 0 | 17/17 | 24/24 | 10 / 9 | 1 shell exit 1: două teste proprii eșuate inițial, corectate |
| Low | 103,326 s | finalizat, exit 0 | 17/17 | 17/17 | 8 / 7 | 0 tool errors observate |

Acceptanța externă a fost rerulată independent după execuții; suita a rămas nemodificată, SHA-256 `94918e3c5f113f6ed3c896740aac007261c821c9aa281937fa0e9518c82fb205`. Testele proprii sunt generate diferit și numărul lor nu este un scor comparabil al calității.

## I/O și engine

| Profil | Citiri fizice sistem | Operații citire | RAM disponibil minim | Prefill capturat | Decode capturat | Decode ponderat | Tokeni engine |
|---|---:|---:|---:|---:|---:|---:|---:|
| Implicit | 27.530 MiB | 450.886 | 180,7 MiB | 12,574 s | 115,649 s | 93,07 tok/s | 10764 |
| Low | 22.155 MiB | 319.835 | 183,8 MiB | 11,888 s | 77,317 s | 92,17 tok/s | 7126 |

Citirile sunt contoare Windows `PhysicalDrive0` pentru întregul sistem, eșantionate la ~2 s pe ferestre de 142,59/102,40 s; nu pot fi atribuite exclusiv Strata și ferestrele au lungimi diferite. Metricile engine includ cereri auxiliare. Ambele au avut câte 2 cereri fără reuse și câte 2 mesaje de parking refuzat. Diferența de volum citit trebuie interpretată împreună cu durata și numărul diferit de pași; nu dovedește că low reduce I/O pentru același număr de tokeni.

## Concluzie și limite

În această pereche low a terminat mai repede și a generat mai puțini tokeni, dar este n=1 per profil, ordine fixă, cu cache/încărcare și soluții generate diferite. Testul precedent `gyro-disk-low-ab-20261110` a avut rezultatul invers (158,7 s implicit vs 168,8 s configurat low), deși acolo aplicarea pe fir nu a fost confirmată. Alte teste au arătat variație. Nu este demonstrată o optimizare fiabilă sau păstrarea calității în proiecte mai dificile; `low` nu a fost aplicat global.

Date brute: `http-metadata.json`, `results.json`, `*-os-io-samples.json`, `*-warmup.json`, `*.jsonl`, `*-engine.log`, `*-metrics.json`, `*-acceptance.txt`, workspaces și `run_http_ab.py`. Limita globală rămâne output 16384, fără `body`, warming off.
