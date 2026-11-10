# Gyro-S: I/O fizic și test temporar reasoning low

## Protocol

Rulări secvențiale OpenCode V2 standalone pe Gyro-S și aceeași instanță Strata, cu workspaces și baze izolate. Taskul Cache, promptul (inclusiv pauza artificială de 12 s), suita externă, output 16384 și warming OpenCode off sunt aceleași. Fiecare rulare a avut aceeași încălzire separată de 2422 tokeni (3,004/3,359 s, neincluse în timpii taskului). Singura schimbare experimentală a fost `providers.strata.models.gyro-gyro-s.body.reasoning_effort: low` în configurația proiectului `effort-low`; baseline nu avea body. Nu s-a modificat configurația globală.

S-a folosit psutil 7.2.2 din Python-ul Strata pentru a eșantiona la ~2 s contoarele Windows ale discurilor fizice și memoria disponibilă. Contoarele `PhysicalDrive0` reprezintă citiri ale întregului sistem, nu doar ale procesului Strata. Intervalul acoperă execuția CLI și scurtul pas de evaluare după CLI; ultimul eșantion poate preceda sfârșitul cu până la ~2 s. Aceste valori sunt distincte de `file_mb`/`file_blobs` din Strata, care pot include accesări deservite de cache-ul Windows.

## Rezultate

| Profil | Wall | Status | Acceptanță externă independentă | Teste proprii independente | Pași / tool calls |
|---|---:|---|---:|---:|---:|
| Baseline | 158,682 s | finalizat, exit 0 | 17/17 | 21/21 | 8 / 8 |
| Efort low | 168,818 s | finalizat, exit 0 | 17/17 | 23/23 | 14 / 13 |

Acceptanța din `results.json` este o eroare de harness: Python-ul Strata nu are pytest. Vezi `VERIFICATION.md` pentru rerularea independentă folosind `C:\Python315\python.exe`. Suita externă nu a fost modificată (SHA-256 `94918e3c5f113f6ed3c896740aac007261c821c9aa281937fa0e9518c82fb205`). Baseline a avut un shell exit 1 pentru un test TTL propriu greșit; low a avut un shell exit 1 (două failures, patru errors în testele proprii) și un edit cu oldString nepotrivit; agenții au corectat și au finalizat.

## Disk, RAM și engine

| Profil | Citiri fizice sistem | Operații citire | Debit mediu eșantionat | RAM disponibil minim | Prefill engine | Decode engine | Decode ponderat |
|---|---:|---:|---:|---:|---:|---:|---:|
| Baseline | 34.733 MiB | 537.433 | 219,22 MiB/s | 150 MiB | 13,275 s | 130,020 s | 93,88 tokeni/s |
| Efort low | 41.025 MiB | 638.001 | 243,65 MiB/s | 53 MiB | 22,206 s | 128,459 s | 96,61 tokeni/s |

Sunt totaluri din eșantioanele acelei execuții, nu viteze ale unui singur pas. Cererile terminate capturate au fost 9 și 15; ambele au avut câte 2 zero-reuse. Logul arată 2 vs 3 refuzuri de parking. Ratele de decodare sunt suma tokenilor generați împărțită la suma timpilor de decode ai cererilor engine capturate, inclusiv cereri auxiliare; nu includ timpul de prefill și nu sunt throughput constant garantat.

Windows a raportat citiri fizice de ordinul zecilor de GiB în ambele ferestre și RAM foarte scăzut, însă măsurarea este la nivel de sistem. Nu demonstrează cât aparține Strata și nu dovedește singură că SSD-ul este cauza principală a latenței. File-tier `file_mb` poate include citiri servite din cache, deci nu se adună cu citirile fizice ca volume independente.

## Limitări și concluzie

`reasoning_effort=low` este prezent în configurația proiectului și este acceptat de codul frontend Strata, dar acest test nu a capturat independent corpul HTTP efectiv; aplicarea efectivă pentru fiecare cerere nu este demonstrată separat. În această pereche, varianta configurată low nu a fost mai rapidă și nu a fost aplicată global. Sunt doar câte o execuție, ordine fixă, cache KV/încărcare sistem variabile și soluții/teste generate diferit; nu există o concluzie statistică sau garanție de calitate. Configurația globală rămâne output 16384, fără body și warming off.

Date brute: `results.json`, `*-os-io-samples.json`, `*.jsonl`, `*-engine.log`, `*-metrics.json`, fișierele originale `*-acceptance.txt`, `VERIFICATION.md`, workspaces și `run_disk_low.py`.
