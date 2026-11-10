# Gyro-S OpenCode — verificare după instrucțiunea pentru edit

## Protocol

Două rulări secvențiale OpenCode V2 2.2.6, Gyro-S prin aceeași instanță Strata, output 16384, warming oprit, sesiuni și baze standalone izolate, directoare curate. Taskul Cache și promptul sunt aceleași ca în `gyro-repeat-20261110`, inclusiv pauza artificială de 12 s. Deadline extern de 210 s. Testul extern a rămas nemodificat: SHA-256 `94918e3c5f113f6ed3c896740aac007261c821c9aa281937fa0e9518c82fb205`.

| Rulare | Timp | Status | Acceptanță externă | Teste proprii rerulate | Apeluri edit | Erori tool |
|---|---:|---|---:|---:|---:|---|
| after-edit-a | 183,253 s | finalizat, exit 0 | 17/17 | 22/22 | 3/3 corecte | 0 |
| after-edit-b | 199,971 s | finalizat, exit 0 | 17/17 | 25/25 | 6/6 corecte | un shell exit 1 la primul test propriu |

Toate cele 9 apeluri `edit` conțineau `path`, `oldString`, `newString` și au fost completate fără eroare. Nu este dovadă statistică a eliminării tuturor erorilor: doar două sarcini, iar alte forme de editare pot eșua.

## Eșecul rămas

La after-edit-b, primul `unittest` a eșuat corect cu exit 1: `test_load_drops_expired_entries` se aștepta ca un element să fie încă valid, deși ambele elemente fuseseră adăugate simultan și aveau același TTL. Agentul a corectat testul prin avansarea ceasului între setări și a verificat separat expirarea lor, după care toate cele 25 de teste proprii și cele 17 externe au trecut. Aceasta este o greșeală de test/raționare recuperată, nu un eșec demonstrat al protocolului sau un exit fals PowerShell.

## Latență și cache

Engine logs: A — 10 cereri terminate, 2 cu zero reuse, 11,119 s prefill și 157,780 s decodare; B — 14 cereri, 2 cu zero reuse, 13,824 s prefill și 171,509 s decodare. Contoarele includ cereri auxiliare, nu doar pașii principali. Limitele maxime pe un pas au fost 7811 și 6867 tokeni; niciuna nu a trunchiat output. Au existat câte două mesaje de parking refuzat din cauza RAM-ului insuficient; hit-urile de prefix au continuat în rest. Aceste măsurători nu stabilesc cauza fiecărei variații de timp.

Rularea A nu a raportat erori tool; B a raportat eșecul real de test de mai sus. În comparația istorică pre-instrucțiune, au existat editări cu argumente lipsă, dar seturile sunt mici și stocastice: nu cuantifică efectul instrucțiunii.

## Dovezi

`results.json`, `after-edit-a.jsonl`, `after-edit-b.jsonl`, fișierele `*-engine.log`, `*-metrics.json`, `*-acceptance.txt` și directoarele fiecărei rulări. Rulările au folosit scriptul `gyro-repeat-20261110/run_repeat.py`. Nu s-a modificat baza de date OpenCode comună sau configurația Strata.
