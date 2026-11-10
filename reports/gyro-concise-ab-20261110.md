# Gyro-S — telemetrie experți și A/B instrucțiune concisă

## Diagnostic înainte de test

Snapshot Strata 0.1.57 / DFlash2, idle: RAM total 31,62 GiB, disponibil Windows ~0,8 GiB; GPU 16.303 MiB, folosiți 14.610 MiB, liberi 1.386 MiB. Cache experți GPU raportat 6595 MiB, context 131072, KV resident 32768. În logurile de decodare recente, hit rate GPU a variat aproximativ 79%–91%, iar o parte din experți a fost accesată prin RAM/PCIe și file tier. KV streaming raporta până la 99,9% hit în VRAM pe sesiunea observată. Sunt instantanee, nu limite fixe.

Exemplu request: 7035 tokeni prompt, 7017 reutilizați, prefill 0,157 s, 5235 tokeni generați în 59,106 s, GPU expert hit 91,1%; metricile Strata raportau numeroase `file_blobs` și `file_mb`. Acestea indică accesări prin file tier, **nu neapărat citiri fizice SSD**: Windows poate servi fișierele din cache. Nu există măsurare atribuită procesului care să demonstreze în mod izolat un blocaj fizic SSD sau să stabilească partea exactă din latență datorată discului.

În alte măsurători salvate, prompturi reci de ~6060 tokeni au luat de la ~4,6 până la 41,2 s. Factorii pot include stare cache, RAM, I/O și încărcare, dar datele existente nu separă cauzal aceste efecte. Nu s-au schimbat setările engine, RAM, VRAM, contextul sau plafonul de reasoning.

## Experiment

Două rulări secvențiale OpenCode V2 standalone, același Gyro-S, task Cache, spec, prompt (inclusiv pauza artificială de 12 s), suită externă, output 16384 și warming OpenCode off. Workspaces și baze izolate. Fiecare a primit în prealabil aceeași cerere de încălzire (2422 tokeni, răspuns exact OK); durata de 3,150/3,382 s a încălzirii nu este inclusă în timpii de task. Singura schimbare a fost un `AGENTS.md` local doar în varianta `concise`: cere implementare și teste concise, dar toate cerințele, edge cases și verificarea să fie păstrate. Nu a fost aplicat global.

| Profil | Wall | Status | Acceptanță externă | Teste proprii independente | Pași / tool calls | Erori tool |
|---|---:|---|---:|---:|---:|---|
| Baseline | 172,831 s | finalizat, exit 0 | 17/17 | 21/21 | 12 / 16 | 2 edit no-op; 1 shell exit 1 |
| Instrucțiune concisă | 174,022 s | finalizat, exit 0 | 17/17 | 24/24 | 15 / 14 | 1 shell exit 1 |

Primul shell exit 1 al fiecărui profil reflecta teste proprii eșuate (1 la baseline, 2 failures și 1 error la concise), pe care agenții le-au corectat. Testele de acceptanță au rămas în afara workspace-urilor și neschimbate: SHA-256 `94918e3c5f113f6ed3c896740aac007261c821c9aa281937fa0e9518c82fb205`.

| Profil | Cereri engine capturate | Prefill | Decode | Tokeni generați engine | Zero reuse | Parking refuzat |
|---|---:|---:|---:|---:|---:|---:|
| Baseline | 13 | 15,960 s | 141,067 s | 12744 | 2 | 2 |
| Concise | 16 | 15,038 s | 143,205 s | 12555 | 2 | 2 |

Aceste totaluri includ cereri auxiliare; sumele pentru pașii OpenCode sunt 12711 și 12379 tokeni. Răspunsurile generate și testele proprii diferă, ordinea este fixă, iar încălzirea nu face identic cache-ul KV. n=1 per profil nu dovedește performanță statistică sau generală.

## Concluzie

Instrucțiunea concisă nu a demonstrat reducerea latenței în această pereche și nu a fost aplicată global. Presiunea RAM, refuzurile de parking și variația hit rate sunt observate, dar nu există dovadă suficientă pentru a identifica un singur blocaj hardware sau pentru a elimina cache-ul/protecțiile. Configurația globală rămâne output 16384, fără buget explicit de reasoning, warming off.

Dovezi: `results.json`, `*-warmup.json`, `*.jsonl`, `*-engine.log`, `*-metrics.json`, `*-acceptance.txt`, `run_concise.py` și workspace-urile. Telemetria acceselor la experți este și în `%LOCALAPPDATA%\Strata\install\strata-gyro-gyro-s.log`.
