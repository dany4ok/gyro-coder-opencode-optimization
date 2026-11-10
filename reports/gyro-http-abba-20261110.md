# Gyro-S: două perechi contrabalansate reasoning implicit / low

## Protocol

Patru rulări secvențiale OpenCode V2 2.2.6 standalone, în ordinea **low A → implicit A → implicit B → low B**, aceeași instanță Gyro-S, task Cache, prompt și pauză artificială de 12 s, suite externe, workspaces/baze izolate, output 16384, warming OpenCode off, timeout 210 s. Înaintea fiecăreia, aceeași cerere de încălzire de 2422 tokeni, răspuns exact OK; timpii de încălzire nu sunt incluși în wall. Aceasta nu garantează același prefix KV pentru task. Low este configurat numai în proiect.

Proxy-ul temporar localhost a salvat doar metadate whitelistate, nu prompturi, răspunsuri sau antete. `http-metadata.json` confirmă **21/21 cereri chat low** cu `reasoning_effort: low`, **28/28 cereri chat implicite** fără acel câmp, toate HTTP 200. Bytes ai cererilor au fost transmiși nemodificați la gateway. `*.jsonl` sunt logurile agentului și pot conține cod, spre deosebire de metadatele redactate.

## Rezultate

| Rulare | Wall | Status | Acceptanță externă | Teste proprii rerulate independent | Tool errors |
|---|---:|---|---:|---:|---|
| low A | 165,155 s | exit 0 | 17/17 | 20/20 | un shell exit 1, două teste proprii eșuate inițial |
| implicit A | 129,927 s | exit 0 | 17/17 | 24/24 | niciuna raportată |
| implicit B | 190,867 s | exit 0 | 17/17 | 16/16 | două shell exit 1, teste proprii eșuate inițial |
| low B | 106,842 s | exit 0 | 17/17 | 17/17 | un shell exit 1, test propriu eșuat inițial |

Toate testele proprii au fost corectate și rerulate independent; suitele proprii sunt diferite între execuții. Suita externă a rămas nemodificată, SHA-256 `94918e3c5f113f6ed3c896740aac007261c821c9aa281937fa0e9518c82fb205`. Media descriptivă a celor două rulări: low **135,999 s**, implicit **160,397 s**. Diferența de 24,398 s (~15,2%) nu este o estimare statistic fiabilă; intervalele individuale sunt 106,842–165,155 și 129,927–190,867 s.

## Cache, decodare și I/O

| Rulare | Prefill engine | Decode engine | Decode ponderat | Citiri fizice sistem | RAM liber minim | Zero reuse / parking refuzat |
|---|---:|---:|---:|---:|---:|---:|
| low A | 19,860 s | 130,149 s | 75,4 tok/s | 40.790 MiB | 83,8 MiB | 2 / 3 |
| implicit A | 13,502 s | 98,506 s | 90,0 tok/s | 27.124 MiB | 57,7 MiB | 2 / 2 |
| implicit B | 14,714 s | 156,980 s | 83,3 tok/s | 41.647 MiB | 80,1 MiB | 2 / 2 |
| low B | 11,135 s | 79,922 s | 96,6 tok/s | 23.478 MiB | 136,0 MiB | 2 / 2 |

Contoarele Windows `PhysicalDrive0` includ întregul sistem, nu doar Strata, iar durata ferestrelor diferă. Valorile sunt diferențe între primul și ultimul eșantion ~2 s; pot omite ultimele două secunde. Metricile engine includ cereri auxiliare. Citirile fizice și `file_blobs` nu trebuie adunate; file tier poate fi servit din cache Windows.

## Decizie și limite

Nu s-a aplicat `low` global. Două rulări per profil, un singur task și suite proprii generate diferit nu demonstrează absența regresiilor de calitate pe proiecte mai dificile. Timpii variază mult, condițiile RAM/cache nu sunt identice și există un test precedent cu ordine inversă în care setarea configurată low a fost mai lentă; acolo transmiterea HTTP nu a fost verificată. Testul anterior confirmat HTTP a favorizat low, dar rămâne tot un singur task. Împreună, probele justifică experimente suplimentare, nu o promisiune de optimizare fiabilă.

Dovezi: `results.json`, `http-metadata.json`, `*-warmup.json`, `*.jsonl`, `*-acceptance.txt`, `*-engine.log`, `*-metrics.json`, `*-os-io-samples.json`, workspaces și `run_http_abba.py`. Configurația globală a rămas la output 16384, fără body de reasoning și warming off.
