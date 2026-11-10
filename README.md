# Gyro-S și OpenCode — diagnostic și benchmark

Arhivă redactată a investigației pentru Gyro-S prin Strata și OpenCode pe Windows. Conține specificațiile și suitele externe, rapoarte experimentale, rezultate numerice selectate, un patch de contabilizare și teste. Nu conține baze de date, credențiale, conversații brute, output-uri complete ale modelului sau loguri JSONL.

**Concluzie:** au fost remediate probleme punctuale de trunchiere, contabilizare și utilizare a uneltelor pe Windows, dar nu s-a demonstrat o îmbunătățire constantă a performanței și calității pe toate taskurile. Task 1 a avut și timeouturi. Vezi [analiza consolidată](docs/analiza-consolidata.md) și [nota de continuare „optimizare engine”](notes/optimizare-engine.md).

## Structură

- `docs/analiza-consolidata.md` — rezultate, decizii, limite și riscuri.
- `notes/optimizare-engine.md` — punct de reluare și instrucțiuni pentru următoarea sesiune.
- `benchmark/` — cererea inițială, specificațiile și suitele externe nemodificate ale Task 1 și Task 2.
- `reports/` — rapoarte ale experimentelor, cu căi personale redactate; referințele lor la fișiere brute sunt istorice, nu linkuri către fișiere incluse.
- `data/summary.json` — subset numeric selectat din rezultatele disponibile, fără conținutul apelurilor. Nu înlocuiește rapoartele și nu dovedește egalitatea condițiilor dintre experimente.
- `fixes/` — patch-ul de raportare reasoning în Strata și testul aferent, nu o copie completă Strata.
- `experiments/` — prototipuri locale selectate de verificare/editare și testul `answer_room`; sunt exemple istorice, nu extensii recomandate pentru instalare.
- `tools/` — corecție locală a analizei contorilor cache și testele ei.

Rapoartele sunt documente istorice, nu recomandări actuale. În special `reports/bench30.md` conține calcule și concluzii inițiale invalidate sau limitate ulterior: rulări Gyro-S suprapuse, timeouturi tratate în unele calcule ca timpi compleți și o modificare ulterioară a suitei Task 2. **Nu folosi acele speedup-uri ca rezultate valide.** `engine_request_delta` calculat prin scăderea ferestrei de istoric de 500 de cereri este de asemenea invalid; vezi `reports/gyro-metrics-window-fix-20261110.md`.

## Testare

Python 3 cu `pytest` instalat. Testele de acceptanță rulează împotriva unui director separat cu implementarea respectivă; ele nu creează soluții:

```powershell
$env:BENCH_TASK_DIR = 'C:\path\to\task1-workspace'
python -m pytest -q benchmark/acceptance/test_task1_acceptance.py
$env:BENCH_TASK_DIR = 'C:\path\to\task2-workspace'
python -m pytest -q benchmark/acceptance/test_task2_acceptance.py
python -m unittest discover -s tools -p 'test_*.py' -v
```

Patch-ul și `fixes/test_chat_reasoning_usage.py` necesită arborele Strata compatibil; nu sunt executate automat din acest repository. Nu aplica automat patch-uri sau setări pe alte versiuni.

Prototipurile din `experiments/` sunt limitate la versiunile și mediul folosite în rapoartele lor: verificarea pre-edit are o fereastră de concurență, unealta cu handle exclusiv este Windows-only și limitată la un fișier, iar încercarea de reordonare a schemei prin plugin nu s-a aplicat în test. Ele nu trebuie activate global fără o nouă evaluare.

## Confidențialitate

Nu adăuga chei, configurații cu credențiale, fișiere `*.db`, loguri de conversație, fișiere temporare sau sursa completă Strata fără o analiză separată. Vezi `.gitignore`. Rapoartele conțin date de performanță și descrieri ale experimentelor și rămân în repository privat.
