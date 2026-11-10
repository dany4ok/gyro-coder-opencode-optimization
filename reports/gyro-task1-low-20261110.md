# Gyro-S: Task 1, reasoning implicit vs low

## Protocol

Două rulări secvențiale OpenCode V2 standalone, Gyro-S pe aceeași instanță Strata, taskul distinct de reconciliere CSV/JSONL (`SPEC_TASK1.md`), prompt identic (inclusiv pauză artificială de 12 s), aceeași suită externă Task 1, workspace și bază izolate, output 16384, warming OpenCode oprit, timeout de proces 240 s. Ordinea a fost implicit apoi low. Încălzirea identică separată de 2422 tokeni a terminat cu `OK`; 3,198/2,666 s nu sunt incluse în timpii taskului. Prefixele KV nu sunt garantate identice.

Proxy localhost cu metadate whitelistate, fără prompturi/răspunsuri/antete: **8/8 cereri chat baseline** fără `reasoning_effort`, **12/12 low** cu `reasoning_effort: low`, toate HTTP 200. Bytes ale corpului au fost transmise nemodificate gateway-ului Strata. `*.jsonl` conțin în schimb cod și apeluri tool generate și nu sunt redactate.

## Rezultate

| Profil | Timp extern | Status | Acceptanță externă pe artefact parțial | Teste proprii independente | Pași / tool calls |
|---|---:|---|---:|---:|---:|
| Implicit | 240,112 s | TIMEOUT | 20/20 | 10/14 | 6 / 7 |
| Low | 240,088 s | TIMEOUT | 20/20 | 12/12 | 10 / 10 |

Ambele procese au fost terminate la deadline; timpul real până la finalizare este necunoscut și 20/20 pe artefactul existent nu înseamnă finalizare reușită. Suitele proprii au fost rerulate independent după oprire. Baseline a păstrat patru eșecuri în teste proprii; cel puțin unele așteptări par incompatibile cu SPEC, dar nu sunt clasificate fără analiză completă. Low a avut inițial nouă erori, inclusiv `Decimal.isfinite` în loc de `is_finite`, apoi un test eșuat și editări; la oprire suita proprie independentă a trecut. Suitele proprii sunt generate diferit, deci nu sunt comparații directe de calitate.

Acceptanța externă a fost rerulată independent, 20/20 fiecare, și are același SHA-256 înainte/după `00bcddba2a3901ccac351e6edc9fefcfa6dd2b6a42060f19a00ec5d6217e95e6`. SPEC SHA-256 `167fc46bb51b351a5d62e5c909a394cf5ad047e49f429c15ff949cd65aa5abbc`.

## Telemetrie

| Profil | Prefill engine capturat | Decode engine capturat | Zero reuse | Parking refuzat | Citiri fizice sistem | RAM minim disponibil |
|---|---:|---:|---:|---:|---:|---:|
| Implicit | 22,201 s | 198,552 s | 3 | 4 | 46.622 MiB / 240,9 s | 132,1 MiB |
| Low | 15,997 s | 201,899 s | 2 | 2 | 53.640 MiB / 241,0 s | 64,1 MiB |

Citirile `PhysicalDrive0` sunt la nivelul întregului sistem, nu exclusiv Strata, și sunt eșantionate la ~2 s. Metricile engine includ cereri auxiliare și nu includ complet generarea întreruptă. Baseline a emis un pas de 13275 tokeni, low unul de 12396 tokeni; acestea sunt sub plafonul output 16384. Nu se poate calcula un speedup cu două rulări timeout.

## Problemă Windows remediată

În baseline, `ls -la` a eșuat deoarece PowerShell mapează `ls` la `Get-ChildItem`, care nu acceptă parametrul Unix `-la`. Instrucțiunea globală condiționată pe Gyro-S din `~/.config/opencode/AGENTS.md` cere acum `Get-ChildItem -Force`. Test izolat ulterior: Gyro-S a folosit `Get-ChildItem -Force | Select-Object Name, Length, Mode`, exit 0, a listat atât fișierul vizibil cât și `.hidden-test`, fără modificări, în 14,456 s. Smoke testul nu dovedește dispariția tuturor erorilor shell.

## Concluzie

Task 1 nu oferă dovezi că `low` termină mai repede sau că păstrează calitatea la finalizare; ambele au expirat, iar scorurile pe artefacte parțiale nu pot susține alegerea unui câștigător. Testele Task 2 anterioare au rezultate variabile. `low` nu a fost aplicat global: modelul rămâne la output 16384, fără body de reasoning, warming off. Nu s-a modificat suita externă sau baza OpenCode partajată.

Date brute: `results.json`, `http-metadata.json`, `*-warmup.json`, `*.jsonl`, `*-engine.log`, `*-metrics.json`, `*-os-io-samples.json`, `*-acceptance.txt`, `list-probe.jsonl` și `run_task1.py`.
