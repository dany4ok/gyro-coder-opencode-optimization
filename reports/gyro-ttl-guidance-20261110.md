# Teste TTL: cronologie locală pentru ceasul simulat

## Diagnostic

În `gyro-edit-followup-20261110/REPORT.md` este descris un test eșuat deoarece două intrări cu același TTL, inserate la același timp, erau tratate ca și cum ar expira diferit. `gyro-tempfile-ab-20261110/seed/test_cachekit.py` reproduce o altă aserțiune similară, împreună cu probleme Windows independente. Aceasta este o greșeală recuperabilă de raționament în teste, nu un defect dovedit în interfața OpenCode.

## Experiment local

Task derivat din Task 2: aceeași implementare `cachekit.py` existentă, aceeași specificație, fără teste inițiale; agentul scrie și rulează teste pentru TTL, graniță, intrări inserate la momente diferite, purge și expirare la load. Controlul și varianta cu `AGENTS.md` local care cere calcularea explicită a momentelor de inserare/expirare rulează secvențial în această ordine. OpenCode V2 standalone, Gyro-S, titlu explicit, output 16384, warming OpenCode oprit, încălzire separată, baze și workspaces izolate, limită 150 s.

| Profil | Wall | Stare | Extern rerulat | Teste generate rerulate | Erori inițiale |
|---|---:|---|---:|---:|---|
| Control | 87,109 s | finalizat | 17/17 | 14/14 | 3 aserțiuni eșuate, corectate |
| Cronologie locală | 107,457 s | finalizat | 17/17 | 10/10 | 1 aserțiune stats eșuată, corectată |

Ambele procese au exit 0; nicio sesiune nu a expirat. În control, un eșec privea așteptarea expirării unei intrări încă valabile, iar celelalte două priveau valorile implicite ale `get`. În varianta cu instrucțiune, eșecul era o comparație de `misses` după un apel care incrementa contorul, nu același caz TTL. Numărul testelor generate nu măsoară comparabil calitatea, iar o singură pereche nu arată că instrucțiunea a cauzat diferențele.

Implementarea este identică byte cu byte cu seed, SHA-256 `f9f1880dfecd0ea1ec06743a9d406262fb92d2d5e7232fc4421ca33ef6011db4`. Suita externă Task 2 originală, SHA-256 `94918e3c5f113f6ed3c896740aac007261c821c9aa281937fa0e9518c82fb205`, a fost rerulată independent pe ambele directoare.

## Verificarea independentă a acoperirii

`mutation_check.py` rulează testele în copii separate; ambele suite trec pe codul original și detectează fiecare dintre trei mutații individuale: eliminarea filtrării expiratelor la load, schimbarea limitei `>=` în `>`, respectiv calcularea eronată a expirării absolute. Aceasta acoperă doar defectele selectate și nu garantează corectitudinea tuturor testelor.

## Concluzie

Intervenția nu demonstrează accelerare (a fost cu 20,348 s mai lentă în această pereche), reducere fiabilă a erorilor sau calitate generală. Traseele și testele generate diferă; a fost o singură pereche în ordine fixă pe un task scurt. Nicio instrucțiune nu a fost aplicată global. `engine_request_delta` și `engine_reused_request_delta` din harness scad o fereastră de 500 de intrări și nu sunt contoare cumulative valide; ele nu sunt folosite în interpretare, conform `gyro-metrics-window-fix-20261110/REPORT.md`.

Dovezi: `results.json`, `*.jsonl`, `*-acceptance.txt`, `mutation_check.py`, `mutation-results.json`, `mutation-tests/`, `run_title.py` și workspaces. Logurile agenților pot conține cod; metadatele HTTP sunt redactate.
