# Presiune RAM Gyro-S — diagnostic și încercare A/B

## Măsurători inițiale

- Windows: 31,62 GiB RAM total, circa 0,42 GiB disponibili și 98% memory load. Procesul Strata avea 21,77 GiB working set; logul runtime raporta 7,83 GiB experți rezidenți, blocați în RAM. Cache-ul conversațional era activ, dar logul raporta refuzuri de parking din cauza pragului de 2560 MiB plus memoria necesară snapshotului.
- Baseline secvențial, același task Cache și prompt ca în `gyro-repeat-20261110`, inclusiv pauza artificială de 12 s, OpenCode V2 standalone și output 16384: **204,665 s, finalizat exit 0, acceptanță externă 17/17, teste proprii rerulate 27/27**. 16 cereri engine, 2 zero-reuse, 19,895 s prefill, 167,786 s decode, două mesaje parking refuzat. A fost raportat un shell exit 1 în timpul execuției; logul complet este `baseline-headroom13.jsonl`.

## Tentativa cu headroom 16 GiB

S-a salvat backup al configurației native și s-a încercat creșterea temporară de la 13 la 16 GiB, fără a modifica contextul sau pragul de protecție. **Nu s-a putut rula benchmarkul cu 16 GiB.** La pornire, Strata a refuzat configurația: 23,1 GiB disponibili, dar **25,1 GiB necesari** = 16 GiB headroom + 5,6 GiB KV/staging + 3,5 GiB vision. Acesta este un refuz de siguranță, nu un rezultat de performanță.

Managerul a făcut rollback automat la un snapshot și a repornit modelul. Scriptul de test a restaurat fișierul original, dar restartul de restaurare a eșuat la plan deoarece trecerea de la snapshot la sursa inițială necesita `--allow-source-switch`. S-a executat apoi manual un restart gestionat și condiționat de identitate/revizie/hash, cu `--allow-source-switch`; succes, runtime `ready`. Planul final arată sursa curentă identică cu sursa originală. Configurația activă este identică byte cu backupul, headroom 13, context 131072, cache activ, gateway model `gyro-gyro-s`. Nu s-au redus pragurile de siguranță.

## Control după restaurare/restart

La repornirea cu setările originale, Strata a alocat 5,14 GiB experți rezidenți, nu 7,83 GiB; selecția automată depinde de resursele libere la încărcare. RAM-ul folosit raportat imediat după restart era 20,61 din 31,62 GiB. După următoarea execuție, Windows raporta circa 3,38 GiB disponibili și Strata 18,10 GiB working set.

Același task/prompt/suită externă, limită 210 s: **TIMEOUT la 210,163 s**; fișierul parțial trece 17/17 teste externe, dar agentul nu terminase și un test propriu TTL a eșuat. Nu este succes complet. 7 cereri engine terminate, 2 zero-reuse, 27,441 s prefill și 168,512 s decode, zero mesaje parking refuzat în captura engine. Monitorul a raportat activitate de parking. Primul prompt complet de 6060 tokeni a costat 15,132 s prefill față de 5,599 s în baseline.

## Concluzie și limite

Nu există o optimizare RAM validată: headroom 16 nu a pornit, iar controlul post-restart a fost mai lent și incomplet. Configurația originală nu a fost schimbată permanent. Diferența observată între cele două controale combină cache rece/cald, alocarea automată diferită a experților, ordinea rulărilor și generare variabilă; nu este un A/B curat și nu dovedește că restartul sau mai mult RAM liber accelerează modelul. Citirea mai frecventă din fișiere este un compromis plauzibil când încap mai puțini experți, nu o cauză cuantificată a întregii diferențe.

O evaluare reală a headroomului de 16 GiB ar necesita minimum 25,1 GiB disponibile la pornire conform verificării actuale Strata, ori o schimbare explicită a vision/hardware care să fie evaluată separat. Nu s-a încercat ocolirea preflightului, dezactivarea vision sau repornirea altor aplicații.

Dovezi: `baseline-results.json`, `after-restored-restart-results.json`, fișierele `*.jsonl`, `*-metrics.json`, `*-engine.log`, `*-acceptance.txt`, `headroom16-plan.json`, `test_headroom.py` și `native-before-headroom.json` (config local cu date sensibile, nu publicați). Eroarea startup și restaurarea sunt în `%LOCALAPPDATA%\Strata\runtime\app-1.server.log` și istoricul conversației.
