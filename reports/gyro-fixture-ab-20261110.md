# Task 1: verificarea fixture-urilor înainte de shell

## Diagnostic

În `gyro-title-reverse-20261110/explicit-title.jsonl`, o comandă a folosit `sample.csv` inexistent și a ieșit cu 2. În `gyro-title-ab-20261110/automatic-title.jsonl`, o altă sesiune a folosit același nume fără a-l crea, iar apoi a încercat să citească raportul inexistent. Ultima sesiune a expirat, deci nu era finalizată. Sunt două incidente observate, nu o dovadă că fiecare execuție le reproduce. Alte eșecuri inițiale de teste reflectă aserțiuni sau cod incorect și sunt probleme distincte.

## Benchmark secvențial

Aceeași specificație Task 1 și suită externă, prompt, încălzire, titlu explicit, output 16384, OpenCode V2 standalone și workspaces/baze izolate. A doua rulare a avut doar local un `AGENTS.md` care cere verificarea sau crearea inputului pentru smoke tests și păstrarea testelor reale; fără schimbări globale. Ordinea este baseline, apoi instrucțiune, timeout 240 s.

| Rulare | Stare | Acceptanță externă la oprire | Teste proprii la oprire |
|---|---|---:|---|
| Baseline | TIMEOUT 240,101 s | 2/20; implementare parțială cu `IndentationError` | nereușite: importul fișierului eșuează |
| Instrucțiune locală | TIMEOUT 240,102 s | 20/20 pe artefact parțial | 19/19 rerulate independent |

Baseline a avut un shell exit 1 cu `IndentationError`. Cu instrucțiune, trei rulări de `unittest` au eșuat inițial, apoi agentul le-a corectat; suita independentă ulterioară a trecut. Niciuna nu a executat o comandă de smoke test pe `sample.csv`, deci benchmarkul **nu testează direct** comportamentul vizat și cele două rezultate parțiale nu demonstrează că instrucțiunea a cauzat diferența. Timpul necesar finalizării este necunoscut.

## Probă direcționată

Într-un workspace separat, copiat de la varianta cu instrucțiune, `sample.csv` nu exista la pornire. Agentul a listat directorul, a declarat că lipsește, a creat un fixture valid și a rulat `python txreconcile.py sample.csv`, exit 0, în cadrul unei sesiuni încheiate în 33,778 s. A rulat și varianta `--output`, afișând exit 0. Este o singură probă cu instrucțiune, fără control pereche; nu demonstrează o reducere statistică a erorilor sau a latenței. A doua comandă a afișat `$LASTEXITCODE` fără propagare explicită, deci exit-ul shell 0 singur nu validează comanda Python; valoarea afișată a fost 0.

## Integritate și limitări

Suita externă a rămas nemodificată, SHA-256 `00bcddba2a3901ccac351e6edc9fefcfa6dd2b6a42060f19a00ec5d6217e95e6`. Nu s-a aplicat regula global: lipsesc finalizări ale benchmarkului și un control direcționat comparabil. `results.json`, `*.jsonl`, `*-acceptance.txt`, `http-metadata.json`, `run_fixture.py` și directoarele workspaces conțin dovezile; logurile JSONL pot conține cod, spre deosebire de metadatele HTTP redactate.
