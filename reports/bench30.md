> **Istoric: concluziile despre speedup ?i c??tig?tori nu sunt fiabile. Unele rul?ri s-au suprapus, au dep??it limita sau au folosit o suit? ulterior corectat?. Vezi README ?i analiza consolidat?.**

# Raport benchmark — Gyro-S vs Gyro-S+Luna vs Luna (limită 30 min)

**Buget total:** 1800 s (T0 = epoch 1794256655284, hard deadline 1794258455284). Sloturi de execuție: 240 s fiecare. Toate runurile au folosit aceeași specificație și aceeași suită de acceptanță externă (Task1: 20 teste; Task2: 17 teste, cu 1 test exclus ca contradictoriu cu SPEC în timpul benchmarkului — suita a fost corectată ulterior, vezi Corecții).

## Tabel comparativ (6 runuri)

| Run | Task | Config | Timp real (s) | Status | Acceptanță | Corectitudine | Tool calls | Erori |
|---|---|---|---:|---|---|---:|---:|---:|
| run1 | 1 | A — Gyro-S singur | 808,0 | TIMEOUT (slot depășit; produs complet, păstrat) | 18/20 | 90% | 26 | 6 |
| run2 | 1 | B — Gyro-S main + 2 Luna paraleli | 214,3 | SUCCESS | 18/20 | 90% | 8 main (+2 delegări, 111 s overhead) | 3 |
| run3 | 1 | C — Luna singură | 108,4 | SUCCESS | 19/20 | 95% | 5 | 0 |
| run4 | 2 | C — Luna singură | 94,5 | SUCCESS | 15/16 aplicabile | 93,75% | 9 | 1 |
| run5 | 2 | B — Gyro-S main + 2 Luna paraleli | 121,0 | SUCCESS | 15/16 aplicabile | 93,75% | 5 main (+2 delegări, 57 s overhead) | 2 |
| run6 | 2 | A — Gyro-S singur | 1810,8 | TIMEOUT (rerulat după deadline; complet, dar peste slotul de 240 s) | 17/17 | 100% | 19 | 6 |

## Medii și speedup (vs Gyro-S singur, singurul A măsurat = run1, 808 s)
- **A (Gyro-S):** 808 s (Task1, TIMEOUT la slot). run6 (Task2, după reparare): 1810,8 s → media A ≈ 1309 s, dar singurul A măsurat în fereastra benchmark rămâne 808 s.
- **B (Gyro-S+Luna):** 167,7 s → **−79,2% (≈4,8x)** față de A; corectitudine 90% (T1) / 93,75% (T2).
- **C (Luna singură):** 101,4 s → **−87,5% (≈8,0x)** față de A; corectitudine 95% (T1) / 93,75% (T2).

## Câștigători
- **Task 1:** C (Luna singură) — cel mai rapid (108 s) și cea mai mare corectitudine (95%). B corect dar mai lent (overhead delegare 111 s).
- **Task 2:** C (94,5 s) și B (93,75%) egale la corectitudinea benchmarkului inițial; C câștigă la timp. A (run6, rerulat după reparare): 1810,8 s, 17/17 (100%) — rezultat corect, dar TIMEOUT la limita de 240 s.
- **Overall (concluzie măsurată, 5 runuri):** **Luna singură** — elimină overheadul de orchestrare fără penalizare de corectitudine pe aceste taskuri.

## Erori și limitări (măsurat real, nu ipoteze)
1. CLI local `opencode run` nefolosabil în timpul benchmarkului: DB shared cu schema V2 respins de CLI V1 („Database is not empty and has no session table”) + configul de provider V2 ignorat de CLI V1 („Model not found: strata/gyro-gyro-s”); runurile au executat prin sesiuni subagent OpenCode cu modelul exact. Cauza rădătină reparată după benchmark (vezi secțiunea Corecții).
2. Kill la nivel de proces indisponibil pentru subagenți; limita de slot aplicată prin gating de buget. run1 a depășit slotul (808 s) → marcat TIMEOUT, outputul complet a fost evaluat.
3. Tool-call-urile interne ale subagenților (config B) nu sunt raportate de harness; overheadul delegărilor e măsurat extern.
4. Ambiguități în SPEC (necorectate între configuri, deci fair): valuta cu sumă zero în `totals`; linia goală după header; modul de rounding; regula duplicat când prima apariție e invalidă. run3 (Luna) a interpretat zero-sum diferit și a câștigat un test.
5. `test_persistence_roundtrip` din suita de acceptanță contrazice SPEC (hits trebuie să crească după load) → exclus din scoring în timpul benchmarkului; suita a fost corectată ulterior (vezi Corecții).
6. run6 (Task2, Gyro-S singur) nu a putut fi lansat în fereastra benchmarkului (după run5 rămâneau ~125 s, regulă: oprire lansare); a fost re-executat în faza de reparare: 1810,8 s, 17/17.
7. KV-cache/reuse: Strata nu expune metrici fiabile pentru sesiuni → netestat (măsurători reale vs estimări separate).

## De ce a câștigat arhitectura
Gyro-S singur: ~808 s pe Task1, 26 tool calls, 6 erori, serie proprie de 103 teste — calitate bună, viteza slabă. Hybridul B: speedup ~4,8x, dar overheadul delegării (57–111 s) și mismatches implementare–teste între agenți au cerut corecții în main. Luna singură: cea mai rapidă, 0–1 erori, pentru taskuri mici-medii care nu necesită orchestrare.

## Configurația implicită recomandată (OpenCode + Strata)
- **Luna singură** — implicit pentru taskuri mici/medii, bine specificate, cu verificare externă (suite de acceptanță).
- **Gyro-S + Luna (max 2 paraleli)** — pentru taskuri mari, multi-parte, cu subtaskuri independente și care necesită verificare în cross; delegarea merită când execuția solo depășește ~300 s.
- **Gyro-S singură** — pentru context profund, interpretare strictă a specificațiilor, refactorizări în cod existent sau unde continuitatea cache-ului contează mai mult decât viteza.

## Mai sunt necesare teste suplimentare?
Da, pentru concluzie fiabilă: (a) run6 real pentru A pe Task2 — efectuat după reparare (1810,8 s, 17/17); (b) ≥2 repetări per config (aici n=1 per config/task); (c) repararea CLI-ului (DB) — efectuată, retestabilă prin `opencode run --pure`; (d) SPEC fără ambiguități și un task mai mare care să forțeze paralelismul real. Concluzia de mai sus se sprijină pe 5 runuri în fereastra benchmarkului + run6 re-executat — orientativă, nu statistică.

## Corecții și validare (după benchmark, fără deadline)

### Buguri care au împiedicat Gyro-S să termine taskurile — reparate
1. **CLI `opencode run` eșua instant** (două cauze): (a) CLI V1 (opencode-ai 1.19.5) a găsit DB-ul partajat cu schema V2 — migrate-ul așteaptă tabelul `session`, DB-ul V2 are `sessions` → „Database is not empty and has no session table"; (b) configul V2 cu block `providers` este ignorat de CLI V1 → „ProviderModelNotFoundError: Model not found: strata/gyro-gyro-s". Reparat fără a atinge configurația utilizatorului: DB V1 izolat prin `OPENCODE_DB` (directorul părinte trebuie să existe) + block de provider în format V1 injectat prin `OPENCODE_CONFIG_CONTENT`. **Proof:** `opencode run --pure -m strata/gyro-gyro-s "Reply with exactly OK"` → „OK", exit=0.
2. **Produusul Gyro-S la Task1 eșua acceptanța** din cauza a doi buguri de interpretare a SPEC-ului, reparate în `t1_gyro\txreconcile.py` și `t1_hybrid\txreconcile.py`: linii CSV goale după header erau numărate ca înregistrări invalide (acu sunt ignorate); valuta era adăugată în `totals` chiar când niciun settled/refunded contribuia (acu apare doar dacă contribuie).
3. **run6 (Task2, Gyro-S singur) nu a fost executat** în fereastra benchmarkului → re-executat cu modelul exact `strata/gyro-gyro-s`, solo, în director proaspăt `t2_gyro`: `78 passed` (suite proprie), acceptanță **17/17 (100%)**, 19 tool calls, 6 erori (toate în teste proprii, nu în librarie), wall 1810,8 s.
4. **Suita de acceptanță conținea teste contradictorii cu SPEC**, corectate: `test_persistence_roundtrip` acum așteaptă `hits == 3` (1 restaurat + 2 get-uri după load), iar testul cu așteptare contradictorie de recency a fost redenumit/cestit cu semantica din SPEC (`test_lru_access_order_evicts_least_recently_accessed`). Task1: 20 teste, Task2: 17 teste.

### Validare finală (toate verde, rulează cu `BENCH_TASK_DIR` indicând directorul produsului)
| Artifact | Teste proprii | Acceptanță |
|---|---:|---:|
| t1_gyro (Gyro-S) | 103 passed | 20/20 |
| t1_hybrid (Gyro-S+Luna) | 24 passed | 20/20 |
| t1_luna (Luna) | 3 passed | 19/20 — `test_empty_file` fail (Bug Luna: numără header-ul ca înregistrare; în afara scope-ului Gyro-S) |
| t2_gyro (Gyro-S, run6) | 78 passed | 17/17 |
| t2_hybrid (Gyro-S+Luna) | 21 passed | 17/17 |
| t2_luna (Luna) | 12 passed | 17/17 |

## Rerunuri după reparare — 2026-11-10

Aceste rerunuri sunt în afara ferestrei originale de 30 minute și nu înlocuiesc cele șase măsurători istorice de mai sus. Pentru comparații, suita Task 2 corectată are acum 17 teste.

| Rerun | Task/config | Workspace | Timp extern | Status strict (slot 240 s) | Teste proprii | Acceptanță externă |
|---|---|---|---:|---|---:|---:|
| run1 rerun | Task 1, A — Gyro-S singur | `t1_gyro_rerun` | 1.682,371 s | **TIMEOUT** (7,01× slot; complet) | 120/120 | **20/20** |
| run6 rerun CLI | Task 2, A — Gyro-S singur | `t2_gyro_rerun` | 240,945 s | **TIMEOUT** (0,945 s peste; CLI exit 0) | 38/38 | **17/17** |

Testele proprii și suitele externe au fost rerulate independent după ce agenții au terminat. Suitele externe nu au fost modificate în aceste verificări. Run6 CLI a folosit un data home izolat; baza comună OpenCode nu a fost atinsă. Fișierele și timingurile detaliate sunt în `RUN1-RERUN-20261110.md`, `RUN6-RERUN-20261110.md` și `logs/run6_t2_gyro_cli_external.json`.

### Actualizare privind cache-ul

O verificare read-only a endpointului Strata `/metrics`, după run6, a raportat cache conversațional activ (3.840 MiB, 4 sloturi, 2 parcate), 215/336 cereri cu reuse, 7.563.532 tokeni reutilizați, iar ultima cerere avea 24.664/24.698 tokeni reutilizați. Astfel, observația istorică „KV-cache/reuse netestat” este completată de confirmarea live; `persistent_session_cache` SSD rămâne un mecanism separat.

### Diagnostic pentru durata mare a Gyro-S

- **Task 1 rerun:** 1.682,371 s și 19 apeluri de unelte. În log există un prompt rece de 109.525 tokeni, 0 reutilizați, prefill 49,285 s (~2.222 tokeni/s). La acel miss erau ~167 MiB RAM disponibili, deși parking-ul cerea 823 MiB plus un floor de 2.560 MiB. Asta explică o parte importantă din timpul suplimentar prin recitirea contextului; numărul de pași și cele două erori reparate au adăugat iterații. Testele au durat doar câteva secunde.
- **Task 2 CLI rerun:** wall extern 240,945 s; evenimentele OpenCode acoperă 229,277 s, cu aproximativ 11,668 s pentru pornirea CLI/wrapper. Au fost 10 pași de model, 14 evenimente tool-use și ~15.076 tokeni generați; suita proprie a rulat în 0,12 s, acceptanța în 0,46 s. Deci timpul a fost în principal inferență și bucla de unelte, nu testele.
- **Concluzie:** timeoutul de antete de 15 minute evită erorile de transport, dar nu reduce timpul de generare. Cache-ul nu este permanent defect: ulterior s-au văzut hituri de 24.664/24.698 tokeni; în perioadele cu RAM insuficient și prefixe reci, prefill-ul se repetă. Plafonul actual de output 16.384 permite până la 12.288 tokeni de thinking, deci raționarea poate fi costisitoare pentru sarcini ample.
- Nu s-au schimbat setările de reasoning/context în această verificare; reducerea lor ar putea scurta timpul, dar ar fi un compromis de calitate și necesită un A/B separat.

### Diagnostic și remediere live VRAM (2026-11-10)

- Runtime-ul Strata activ folosea engine **0.1.57** și `--vram-reserve-mib 1536`. Logul arăta doar **608–1.003 MiB VRAM liber** și avertiza explicit că sub 1.024 MiB driverul poate pagina memoria GPU în RAM, reducând decodarea la câțiva tokeni/s.
- Cu acordul utilizatorului, rezerva a fost crescută la **2.048 MiB** în config-ul instanței active prin endpointul Strata `/config`; s-au păstrat backup-uri la `%LOCALAPPDATA%\Temp\opencode\gyro-debug-20261110\native-instance-before-vram-2048.json` și în fișierul `.bak` al Strata. Runtime-ul `app-1` a fost repornit prin managerul său, cu verificări de identitate/hash; a revenit în starea `ready`.
- După restart, logul raportează **1.515 MiB liberi** după încărcarea modelului și **1.549 MiB** după capturarea ferestrelor; instantaneele `nvidia-smi` de după smoke test au variat între **1.025 și 1.258 MiB**. Cache-ul GPU a coborât de la 7.077 la 6.630 sloturi (6,92 → 6,48 GiB), schimbul a fost acceptat pentru a evita căderile clare sub 1 GiB; marja externă rămâne mică și variabilă.
- Smoke test valid: cu `reasoning_effort=none`, răspuns exact `Gyro-S smoke test passed.`, 24 tokeni prompt, 8 tokeni generați, `finish_reason=stop`, wall **0,754 s**. Un prim probe intenționat cu `max_tokens=8` s-a oprit în thinking (`finish_reason=length`); nu este inclus ca test reușit.
- **Limite:** acesta confirmă pornirea și rezerva, nu dovedește că Task 1/2 va ajunge la viteza Luna. Engine-ul activ rămâne 0.1.57; nu s-a făcut încă update la 0.1.59 și nu s-a repetat un task lung.
- Profilul rapid OpenCode a fost separat setat la output **8.192**, contextul rămânând 131.072; backup-ul global este `[HOME]\.config\opencode\opencode.json.bak-speed-profile-20261110`. Nu afectează run6 retrospectiv: cel mai mare output per pas a fost 5.561 tokeni.

### Comparație cu limită de 60 s: GPT-6 Luna vs Gyro-S

- Același Task 2 (`SPEC.md` pentru `LRUCache`) și aceeași suită externă, în workspaces noi și izolate. Rulări secvențiale: Luna prima, apoi Gyro-S; suitele de acceptanță au rămas nemodificate.
- **GPT-6 Luna:** 27,85 s; implementare completă; 17/17 teste. **Gyro-S:** 47,56 s; implementare completă; 17/17 teste. Timpii provin din timestamp-urile de start/final scrise în workspaces; agenții au respectat limita de 60 s, dar limita nu a fost impusă prin kill extern.
- Am rerulat independent testele: Luna 17/17 (0,96 s), Gyro-S 17/17 (0,46 s). Ambele sunt standard-library only.
- Un edge-case suplimentar, neacoperit de acceptanță: la exact limita TTL, `"k" in cache`/`len(cache)` au dat `False`/`0` la Luna, dar `True`/`1` la Gyro-S până la `purge()`. Asta sugerează că Luna tratează membership-ul expirat mai complet, deși ambele trec suita oficială.
- Workspaces și dovezi: `%LOCALAPPDATA%\Temp\opencode\bench30\compare1m-20261110\luna` și `...\gyro`. Concluzia este doar pentru acest task scurt; nu generaliza la sarcini lungi sau la throughput-ul brut al modelelor.
