# I/O al procesului Strata și restrângerea temporară a uneltelor

## Protocol

Taskul Cache Task 2 și suita externă neschimbată, același prompt inclusiv pauza artificială de 12 s, Gyro-S/OpenCode V2 standalone, titlu explicit, output 16384, warming OpenCode oprit. Două rulări secvențiale cu încălzire identică separată, workspaces și baze izolate, timeout 210 s. Singura intervenție experimentală: plugin V2 în workspace-ul `restricted-tools`, cu hook `context` care păstrează doar `read`, `write`, `edit`, `shell`; fără modificări globale. Aceasta elimină inclusiv unelte utile pentru alte sarcini și nu este o recomandare generală.

Proxy-ul local a păstrat doar metadate HTTP redactate. Control: **11/11 cereri cu 12 unelte**; varianta restrânsă: **15/15 cereri cu 4 unelte**; toate HTTP 200. Pluginul a înregistrat ce nume a eliminat, nu conținutul cererilor. Suita externă SHA-256 `94918e3c5f113f6ed3c896740aac007261c821c9aa281937fa0e9518c82fb205`.

## Rezultate

| Variantă | Wall | Stare | Extern | Teste proprii rerulate | Pași / tool calls | Erori |
|---|---:|---|---:|---:|---:|---|
| Control | 175,240 s | finalizat, exit 0 | 17/17 | 25/25 | 11 / 10 | un shell exit 1 inițial: două teste proprii eșuate |
| 4 unelte | 155,495 s | finalizat, exit 0 | 17/17 | 26/26 | 15 / 14 | un shell exit 1 inițial: un test propriu eșuat |

Ambele suite externe și proprii au fost rerulate independent. Testele proprii sunt generate diferit și numărul lor nu este o comparație directă de calitate. În ambele cazuri agentul a corectat testele proprii eșuate.

## Telemetrie proces și engine

Procesul unic `strata.exe`, PID 2020 și aceeași dată de creare în ambele ferestre, a fost eșantionat la ~2 s cu `psutil.Process.io_counters()`, `memory_info()` și `cpu_times()`; contoarele sunt atribuite procesului, nu sistemului. Acestea reprezintă I/O de citire contabilizat procesului Windows și **nu sunt o măsurătoare sigură a citirilor fizice de pe SSD**; cache-ul, mapările de memorie și alte mecanisme pot afecta atribuirea. Nu se adună cu `file_blobs`/`file_mb` ale engine-ului.

| Măsură | Control | 4 unelte |
|---|---:|---:|
| Fereastră eșantionată | 174,97 s | 154,95 s |
| Citiri contabilizate procesului | 768,6 MiB; 192627 operații | 462,1 MiB; 115850 operații |
| CPU proces user + system | 1152,73 s | 979,28 s |
| Working set proces, interval | 20,27–22,00 GiB | 20,99–22,62 GiB |
| Minim RAM disponibil sistem | 170,7 MiB | 139,3 MiB |
| Prefill engine însumat | 11,065 s | 16,175 s |
| Decode engine însumat | 149,185 s | 122,466 s |
| Tokeni generați în cereri engine terminate | 13738 | 11235 |

CPU-ul însumat peste fire poate depăși timpul wall. Ultimul eșantion poate preceda finalul cu aproximativ două secunde; testele și verificările externe nu sunt incluse uniform în durata CLI. Cererile engine includ și cereri auxiliare. Primul prompt al controlului a avut 6101 tokeni / 4073 ms prefill, iar cu patru unelte 4017 tokeni / 4293 ms: ~2084 tokeni mai puțin, dar fără reducere de prefill în acea pereche. Hook-ul a redus schema și schimbă simultan posibilitățile agentului.

## Concluzie

Varianta restrânsă a terminat cu 19,745 s mai repede în această singură pereche și a generat mai puțini tokeni, dar controlul și intervenția au avut trasee diferite, număr diferit de pași, ordine fixă și ferestre I/O diferite. Nu se poate atribui diferența exclusiv numărului de unelte sau discului și nu se dovedește absența regresiilor. Un singur task Cache nu arată dacă lipsa `grep`, `glob`, `webfetch` sau a altor unelte dăunează altor sarcini. Intervenția rămâne exclusiv locală; nu s-a modificat configurația globală.

Dovezi: `results.json`, `http-metadata.json`, `*-os-io-samples.json`, `*-engine.log`, `*-metrics.json`, `*-acceptance.txt`, `*.jsonl`, `restricted-tools/tool-filter.jsonl`, `run_process.py`, `tool-filter.js`. JSONL-urile obișnuite pot conține cod și mesaje; `http-metadata.json` nu conține corpuri sau antete.
