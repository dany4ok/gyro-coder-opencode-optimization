# Erori de teste: contoare mutabile după `get`

## Diagnostic și reproducere

În sesiunea finalizată `gyro-tempfile-generation-20261110/tempfile-guidance.jsonl`, un test a comparat statisticile restaurate cu cele salvate după un `get` reușit: `hits=1` versus `hits=0`. În `gyro-process-tools-ab-20261110/control.jsonl`, o altă sesiune a eșuat comparând contoare `hits` după apeluri ale cache-ului (`3 != 2`). Specificația Task 2 spune că un `get` reușit incrementează hits; acestea sunt erori observate în teste generate, nu un defect demonstrat al tool-ului OpenCode.

Probă deterministă pe implementarea seed: imediat după load, `restored.stats == cache.stats` este `True`, cu 0 hits; după `restored.get('a')`, comparația este `False`, cu 1 hit în cache-ul restaurat și 0 în cel original. Nu dovedește că toate eșecurile istorice au aceeași cauză.

## Comparație secvențială locală

Același task scurt din `gyro-tempfile-generation-20261110`: generare de teste pentru persistență, stats, expirare la load și trunchiere LRU pe aceeași implementare deja existentă. OpenCode V2 standalone, același prompt, titlu explicit, output 16384, warming OpenCode oprit, timeout 150 s, încălzire separată, baze/workspaces izolate. Ordinea: control, apoi `AGENTS.md` local care cere snapshot al contoarelor, verificare înainte de `get` și verificarea efectelor după `get`.

| Profil | Wall | Stare | Extern rerulat | Teste generate | Eroare inițială |
|---|---:|---|---:|---:|---|
| Control | 70,834 s | finalizat, exit 0 | 17/17 | 6/6 | niciuna raportată |
| Instrucțiune locală | 63,462 s | finalizat, exit 0 | 17/17 | 6/6 | `AttributeError`: `cache.advance`, corectată ulterior |

Ambele implementări au rămas byte-identice cu seed, SHA-256 `f9f1880dfecd0ea1ec06743a9d406262fb92d2d5e7232fc4421ca33ef6011db4`. Suita externă neschimbată Task 2 SHA-256 `94918e3c5f113f6ed3c896740aac007261c821c9aa281937fa0e9518c82fb205` a fost rerulată independent pentru fiecare. În varianta cu instrucțiune, testul final face snapshot `saved_stats`, verifică starea imediat după load și apoi testează incrementarea `hits`/`misses`. Primul run a afișat și un `ResourceWarning` pentru un fișier deschis fără context manager, distinct de eroarea fatală.

## Verificare independentă a testelor generate

`mutation_check.py` a rulat fiecare suită într-o copie izolată, nemodificând workspaces: ambele trec pe original (6/6) și ambele detectează fiecare dintre trei mutații separate: lipsa eliminării expiratelor la load, lipsa trunchierii LRU și salvarea statisticilor cu zero. Aceasta este o verificare țintită, nu dovada unei acoperiri complete.

## Interpretare

Controlul nu a produs eroarea vizată, iar varianta cu instrucțiune a produs o eroare diferită. O singură pereche cu ordine fixă și trasee diferite nu demonstrează că regula reduce erorile, nici că diferența de 7,372 s este cauzală. Nu se extrapolează la Task 1 complet și nu se aplică global. Câmpurile agregate de request engine din `results.json` sunt inconsecvente în fereastra măsurată și nu sunt folosite pentru concluzii cache.

Dovezi: `results.json`, `*.jsonl`, `*-acceptance.txt`, `mutation_check.py`, `mutation-results.json`, `mutation-tests/`, workspaces și `run_title.py`. JSONL-urile pot conține cod; metadatele HTTP sunt redactate.
