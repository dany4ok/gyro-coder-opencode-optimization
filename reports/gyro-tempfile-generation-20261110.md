# Generarea testelor de persistență pe Windows

## Protocol

Task scurt derivat din Task 2: aceeași implementare `cachekit.py` existentă și aceeași specificație, fără teste inițiale. Agentul trebuie să genereze și să ruleze teste pentru save/load, stats, expirare la încărcare și trunchiere LRU, fără modificarea implementării. Controlul și varianta cu `AGENTS.md` local despre folosirea căilor temporare pe Windows au rulat secvențial, în această ordine, cu baze/workspaces izolate, titlu explicit, output 16384, warming OpenCode oprit și deadline 150 s. Nu s-au modificat configurația globală sau suita externă.

| Profil | Wall | Stare | Extern rerulat | Teste generate rerulate | Erori inițiale |
|---|---:|---|---:|---:|---|
| Control | 70,759 s | finalizat, exit 0 | 17/17 | 10/10 | o aserțiune de expirare greșită, corectată |
| Instrucțiune locală | 71,793 s | finalizat, exit 0 | 17/17 | 8/8 plus 3 subtests | o aserțiune de stats greșită, corectată |

Ambele implementări au rămas byte-identice cu seed, SHA-256 `f9f1880dfecd0ea1ec06743a9d406262fb92d2d5e7232fc4421ca33ef6011db4`. Suita externă neschimbată SHA-256 `94918e3c5f113f6ed3c896740aac007261c821c9aa281937fa0e9518c82fb205` a fost rerulată independent pentru ambele. Suitele proprii diferă, astfel că numărul testelor nu este scor comparabil.

## A fost prevenită eroarea Windows?

Niciuna dintre sesiuni nu a avut `PermissionError`. Controlul a generat inițial fixture cu `tempfile.mkdtemp`, iar profilul cu instrucțiune a folosit `tempfile.TemporaryDirectory`; ambele permit redeschiderea fișierelor. Mențiunea `NamedTemporaryFile` din varianta cu instrucțiune este într-un comentariu explicativ, nu un apel. Agentul cu instrucțiune a exprimat regula în comentariu, dar și controlul a ales un mecanism compatibil. Prin urmare nu se poate atribui absența erorii instrucțiunii și nu există dovadă că o previne mai fiabil.

## Verificare independentă prin mutații

`mutation_check.py` a copiat separat testele și implementarea și a rulat fiecare suită pe trei defecte introduse individual, plus controlul nemodificat. Workspaces agenților au rămas neschimbate.

| Mutație izolată | Control | Instrucțiune |
|---|---|---|
| Fără mutație | 10/10 trecute | 8/8 și 3 subtests trecute |
| Nu elimină expiratele la load | 2 eșecuri | 1 eșec |
| Nu trunchiază la max_size la load | 1 eșec | 2 eșecuri |
| Salvează stats ca zero | 3 eșecuri | 2 eșecuri |

Ambele suite detectează aceste trei defecte concrete. Mutațiile sunt un eșantion limitat și nu demonstrează acoperire completă, robustețe generală sau calitate egală.

## Concluzie

O singură pereche de execuții, fără `PermissionError` în control, nu poate demonstra efect preventiv sau îmbunătățire de performanță. Timpul cu instrucțiune a fost cu 1,034 s mai mare, dar traseele diferă; nu se interpretează ca overhead cauzal. Testul anterior de reparare a arătat și o posibilă pierdere de acoperire, deci instrucțiunea rămâne locală. Metricile agregate de request engine din `results.json` sunt inconsecvente în această fereastră și nu sunt folosite drept dovezi de cache.

Dovezi: `results.json`, `*.jsonl`, `*-acceptance.txt`, `mutation_check.py`, `mutation-results.json`, `mutation-tests/`, workspaces și `run_title.py`. Logurile agentului pot conține cod; metadatele HTTP sunt redactate.
