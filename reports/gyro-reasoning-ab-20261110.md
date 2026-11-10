# Gyro-S: diagnostic latență și buget temporar de reasoning

## Telemetrie anterioară

În cele două rulări complete `gyro-edit-followup-20261110`, cererile engine terminate au însumat 11,119/13,824 s de prefill și 157,780/171,509 s de decodare. Într-o rulare ulterioară, un prompt rece de 6066 tokeni a avut singur 37,031 s prefill. În ambele cazuri sunt incluși pași auxiliari ai engine-ului; acestea nu dovedesc o cauză unică sau timpi constanți.

## Test

Două sesiuni OpenCode V2 standalone, secvențiale, aceleași task, prompt (inclusiv pauza artificială de 12 s), specificație și suită externă, directoare și baze separate, output 16384 și warming off. Limita reală de proces este 210 s. Singura modificare experimentală în configurația proiectului este `providers.strata.models.gyro-gyro-s.body.reasoning_budget_tokens: 2048`. Strata permite această cheie la nivel de request; logul serverului a arătat `thinking budget reached (2048 tokens): wrapping up the thinking`, cu `max 16384`, deci setarea a fost efectiv aplicată. Setarea nu a fost adăugată global.

| Config | Wall extern | Rezultat | Teste externe | Teste proprii independente |
|---|---:|---|---:|---:|
| Fără buget explicit | 220,329 s | TIMEOUT; include timpul de oprire | Nu a putut colecta: nu exista `cachekit.py` | Nu exista suită completă |
| Buget 2048 | 181,974 s | finalizat, exit 0 | 17/17 | 26/26 |

Agentul cu buget redus a avut două execuții de teste proprii cu exit 1 și le-a corectat: prima includea șase erori, inclusiv utilizarea greșită `tempfile.mktemp` în implementare; a doua, o așteptare TTL greșită într-un test. Testele au trecut ulterior, independent, fără modificarea acceptanței externe. SHA-256 acceptanță `94918e3c5f113f6ed3c896740aac007261c821c9aa281937fa0e9518c82fb205` înainte/după.

## Metrici și limitări

- Baseline: doar 2 cereri engine terminate capturate, 2 fără reuse, prefill total 43,977 s, decode total 9,844 s; agentul a fost oprit în timpul unei cereri. Tokenii/decodarea cererii întrerupte nu sunt incluși în acestea. Promptul de 6054 tokeni a avut prefill 41,167 s.
- Buget 2048: 16 cereri engine terminate, 1 fără reuse, prefill total 22,436 s, decode total 143,427 s, două refuzuri de parking. Un prompt de 6062 tokeni a avut prefill 7,609 s. Contorul include și cereri auxiliare; OpenCode a raportat 14 pași principali.
- Ordinea fixă, cache rece/cald și diferența uriașă de prefill fac imposibilă atribuirea rezultatului exclusiv bugetului. Baseline-ul este cenzurat de timeout și nu are timp complet cunoscut; nu se calculează speedup. Un singur task care trece nu demonstrează menținerea calității pe sarcini mai mari.
- 2048 limitează raționamentul per cerere, nu întreaga sesiune și nu outputul de 16384 tokeni. Poate degrada calitatea sau impune iterații suplimentare. Nu s-a schimbat configurația globală: output 16384, fără `body.reasoning_budget_tokens`, warming off.

Dovezi: `results.json`, `baseline.jsonl`, `budget2048.jsonl`, `*-engine.log`, `*-metrics.json`, `*-acceptance.txt`, configurațiile locale ale workspacelor și `run_reasoning.py`. Logul Strata `%LOCALAPPDATA%\Strata\runtime\app-1.server.log` conține bugetul efectiv și atingerea lui.
