# Gyro-S — comparație reasoning cu încălzire identică

## Protocol

OpenCode V2 2.2.6 standalone, Gyro-S pe aceeași instanță Strata, taskul Cache și suita externă identice cu benchmarkul precedent, sesiuni/workspaces/baze izolate și rulări secvențiale. Promptul include aceeași pauză artificială de 12 s. Fiecare execuție are timeout extern 210 s, output 16384 și warming OpenCode oprit. Prima folosește doar pentru proiect `body.reasoning_budget_tokens=2048`, a doua implicit. Configurația globală rămâne nemodificată.

Înainte de fiecare s-a trimis aceeași cerere independentă de încălzire: 2422 tokeni prompt, `reasoning_effort=none`, răspuns exact OK, finish `stop`. A durat 3,088 s, respectiv 3,031 s, excluse din timpii de task. Aceasta încălzește engine-ul, **nu garantează același prefix KV al taskului**. Ambele cereri principale au avut prefixe inițiale fără reuse. Suita externă, nemodificată, SHA-256 `94918e3c5f113f6ed3c896740aac007261c821c9aa281937fa0e9518c82fb205`.

## Rezultate

| Profil | Wall task | Status | Acceptanță externă | Teste proprii independente | Pași / tool calls | Erori |
|---|---:|---|---:|---:|---:|---|
| Buget reasoning 2048 | 152,861 s | finalizat, exit 0 | 17/17 | 21/21 | 13 / 12 | un shell exit 1: două teste proprii eșuate, corectate |
| Reasoning implicit | 145,602 s | finalizat, exit 0 | 17/17 | 15/15 | 9 / 8 | un shell exit 1: două teste proprii eșuate, corectate |

Un apel a fost recuperat în ambele cazuri după o suită proprie cu exit 1 real; nu au fost erori de tool tip `edit` raportate. Nu se compară numărul de teste proprii ca indicator de calitate: suitele au fost scrise diferit de model.

Logul Strata a arătat `thinking: ... of budget 2048 (max 16384)` și `thinking budget reached (2048 tokens)`, deci plafonul request a fost primit. Bugetul privește reasoning per cerere, nu limitează întregul output al sesiunii.

## Prefill / decode

| Profil | Prefill total engine capturat | Decode total engine capturat | Reuse zero | Refuzuri parking |
|---|---:|---:|---:|---:|
| Buget 2048 | 16,914 s | 118,771 s | 2 | 3 |
| Implicit | 12,933 s | 118,141 s | 2 | 2 |

Prompturile reci principale au fost 6066 tokeni în 4,592 s, respectiv 6058 în 5,704 s. Metricile engine includ cereri auxiliare, nu doar pașii agenților. Pentru buget, fișierul engine conține 15 linii de prompt terminate, dar contorul de request-uri din snapshot a crescut cu 14: o linie poate fi la limita ferestrei de captură sau o cerere auxiliară; totalurile din log trebuie interpretate cu această rezervă. Implicit: 10 linii, delta 10. Nu se presupune că numărul diferit de cereri reflectă doar setarea de reasoning.

## Concluzie

În această singură pereche încălzită, bugetul 2048 **nu a fost mai rapid**; nu este justificată o modificare globală. n=1 per profil, ordine fixă, conținut și suite proprii generate diferit, presiune RAM și cache KV variabile: rezultatul nu stabilește performanța statistică sau calitatea pe taskuri mai dificile. Rezultatul diferă de testul anterior cu baseline timeout și prefill rece de 41,167 s, ceea ce subliniază importanța condițiilor de cache; nici acel test nu dovedește un speedup.

Date: `results.json`, `*-warmup.json`, `*.jsonl`, `*-engine.log`, `*-metrics.json`, `*-acceptance.txt`, `run_warm_ab.py`; implementările sunt în directoarele profilurilor. Global: output 16384, fără body de buget, warming off.
