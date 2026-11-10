# Gyro-S: repetări OpenCode și comparație Codex

## Protocol

Gyro-S, același Strata local, același task cache, aceleași instrucțiuni (inclusiv pauza artificială de 12 s), aceleași teste externe și workspaces noi. Rulări secvențiale, cu Strata idle înainte de fiecare, fără inferență intenționat suprapusă. Limita reală de proces: 210 s. OpenCode V2 2.2.6 în standalone cu baze izolate, warming oprit. Ordine ABBA: 8192, 16384, 16384, 8192. Codex 0.167.0-alpha.3.2 a rulat ultimul, cu CODEX_HOME izolat, prin aceeași instanță Strata și API Responses; OpenCode a folosit Chat Completions. Testele externe nu au fost schimbate: SHA-256 `94918e3c5f113f6ed3c896740aac007261c821c9aa281937fa0e9518c82fb205`.

## Rezultate

| Agent / output limit | Wall | Status | Teste proprii independente | Acceptanță externă | Erori observate |
|---|---:|---|---:|---:|---|
| OpenCode 8192 A | 210,108 s | TIMEOUT | nu a fost evaluată ca rezultat complet | 17/17 pe artefact parțial | două edit-uri cu `path` lipsă; două shell exit 1 |
| OpenCode 16384 A | 157,351 s | finalizat | 22/22 | 17/17 | un shell exit 1 |
| OpenCode 16384 B | 185,015 s | finalizat | 20/20 | 17/17 | un edit fără `newString`; două shell exit 1 |
| OpenCode 8192 B | 153,169 s | finalizat | 17/17 | 17/17 | un shell exit 1 |
| Codex, limită efectivă necunoscută | 146,896 s | finalizat | 18/18 | 17/17 | două `apply_patch` invalide; un shell exit 1 în ciuda `unittest OK` |

Nu echivalați shell exit 1 cu o eroare a aplicației generate fără a citi logul. În Codex, `unittest` a trecut, dar PowerShell a raportat stderr ca eroare; agentul a verificat ulterior. La OpenCode, unele shell exit 1 reflectă teste proprii eșuate. La timeout, acceptanța măsoară numai fișierul existent, nu finalizarea agentului.

## Analiză

- Niciuna dintre aceste patru repetări nu a atins limita de 8192: cele mai mari generări/pas au fost 4239, 6221, 5746 și respectiv 4192 tokeni. Prin urmare, variația temporală din aceste patru rulări nu demonstrează un avantaj cauzat de limita 16384. În testul precedent, ambele rulări la 8192 au atins efectiv plafonul și au avut `write` trunchiat: pericol real, dar nu permanent.
- Pe OpenCode 16384 ambele rulări au terminat și au trecut acceptanța, dar n=2 nu dovedește fiabilitate generală. Variația rămâne vizibilă; Codex are un singur rezultat. Nu se pot trage concluzii statistice sau atribui integral diferența de viteză agentului: API-ul, promptul de sistem, tool-urile, reasoning effort și overheadul nu sunt identice. Codex folosește `model_reasoning_effort=low`, OpenCode profilul implicit.
- În OpenCode au apărut două `edit` cu `path` lipsă și unul cu `newString` lipsă. Instrucțiunea Gyro-S din `~/.config/opencode/AGENTS.md` cere acum explicit toate cele trei câmpuri. Verificare separată, o sesiune: trei apeluri edit, fiecare cu `path`, `oldString`, `newString`, toate completate; fișierul conține cele trei modificări corecte, în 23,291 s. Acesta este un smoke test, nu o dovadă că eroarea a dispărut statistic.
- Codex a avut două erori de sintaxă `apply_patch` vizibile în stderr, a recuperat și a terminat. Nu susține afirmația că Gyro-S nu greșește niciodată cu alți agenți.
- Configurația globală rămâne output 16384, warming off; bazele comune OpenCode și Codex nu au fost modificate intenționat. Toate rezultatele brute, inclusiv timeouturile și stderr, sunt în acest director.

## Dovezi

`results.json`, `limit*.jsonl`, `limit*-engine.log`, `limit*-acceptance.txt`, `codex.jsonl`, `codex-stderr.log`, `codex-results.json`, `codex-acceptance.txt`, `edit-probe-results.json` și `edit-probe.jsonl`. Scripturi: `run_repeat.py`, `run_codex.py`. Configurația Codex și catalogul izolate sunt în `codex-home/`.
