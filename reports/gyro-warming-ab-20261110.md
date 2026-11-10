# Gyro-S / OpenCode V2 — A/B warming și output trunchiat

## Metodă

Taskul Cache (`SPEC_TASK2.md`) și suita externă de 17 teste sunt identice între rulări. OpenCode V2 2.2.6, sesiuni standalone și baze izolate, trei directoare curate, rulări secvențiale. Toate solicită o pauză artificială identică de 12 secunde prin shell, pentru a putea observa warming într-un test scurt. Limită externă 210 secunde, cu taskkill al procesului și copiilor sale. Warming on a folosit interval experimental de 5 secunde / durată 2 minute, nu setarea istorică de 3 minute. Rulările off/on foloseau limita globală 8192; rularea fixed folosește 16384 și warming off. Strata era idle înaintea fiecărei rulări. SHA-256 spec: `ad35032dc8ae372a83b4a5b12329c8e06234972bdaef101416f103d3b924fd9d`; acceptanță: `94918e3c5f113f6ed3c896740aac007261c821c9aa281937fa0e9518c82fb205` (confirmat după test).

## Rezultate

| Rulare | Warming | Output max | Wall | Status | Acceptanță | Pași / tool calls | Erori tool |
|---|---|---:|---:|---|---:|---:|---|
| off | off | 8192 | 210,090 s | TIMEOUT | 17/17 pe artefact parțial | 10 / 12 | 2 write trunchiate; 1 edit no-op |
| on | 5 s | 8192 | 210,086 s | TIMEOUT | 17/17 pe artefact parțial | 17 / 19 | 2 write trunchiate; 1 shell cu exit 1 |
| fixed-16384 | off | 16384 | 154,600 s | finalizat, exit 0 | 17/17 | 11 / 13 | 1 shell exit 1, teste proprii eșuate și corectate |

Pentru fixed, testele proprii au fost rerulate independent: 23/23. O primă rulare a testelor proprii a avut trei eșecuri; agentul a făcut corecții. Nu este o dovadă că modelul nu mai greșește.

## Cache și integrare

| Rulare | Cereri engine terminate | Cereri cu reuse | Zero reuse | Prefill total | Parking refuzat |
|---|---:|---:|---:|---:|---:|
| off | 11 | 9 | 2 | 14,654 s | 3 |
| on | 20 | 18 | 2 | 19,525 s | 7 |
| fixed-16384 | 12 | 10 | 2 | 14,333 s | 2 |

Rularea on conține două cereri scurte suplimentare în pauza controlată, cu 6007/6039 și 6034/6039 tokeni reutilizați. Diferența totală de cereri dintre on/off nu poate fi atribuită integral warming-ului: agenții au făcut un număr diferit de pași. Pe parcursul rulărilor, logurile raportează frecvent sute de MiB RAM disponibile, sub pragul de siguranță pentru parking. Cache hit-urile pașilor succesivi au rămas totuși active. Prefillul include toate cererile engine capturate, inclusiv cereri auxiliare; timpii nu trebuie atribuiți integral aceluiași pas de agent.

În ambele rulări la 8192, un pas a generat exact 8192 tokeni, iar OpenCode a raportat pentru două apeluri `write`: `output token limit (stop reason: length)` și argumente incomplete. Agentul a trebuit să reîncerce. Acest lucru este o cauză reproductibilă de erori de integrare, nu dovada că orice eșec Gyro-S are aceeași cauză. La 16384, cel mai mare pas a fost de 5353 tokeni și nu a existat acea eroare. Configurația globală Gyro-S a fost restaurată la output 16384, context 131072, warming off; backup la `[HOME]\.config\opencode\opencode.json.bak-before-output-fix-20261110-022431`.

## Limitări

- Off și on au fost ambele oprite la 210 s: timpii finali compleți sunt necunoscuți. 17/17 pe artefact parțial nu transformă timeoutul în succes.
- Nu există un câștig măsurat prin dezactivarea warming-ului. Testul a folosit 5 secunde și o pauză artificială, nu 3 minute; ordinea fixă și diferențele stocastice de generare limitează comparația.
- Fixed-16384 este doar o singură rulare; pasul maxim a fost sub 8192, astfel că diferența temporală nu cuantifică efectul schimbării. Nu s-a făcut o comparație simultan controlată cu alt agent sau Luna.
- Memoria insuficientă pentru parking este observată, dar nu dovedește că toate întârzierile provin din ea. Nu s-au dezactivat protecțiile de memorie sau cache-ul Strata, și nu s-a modificat baza de date partajată.

Loguri: `off.jsonl`, `on.jsonl`, `fixed-16384.jsonl`, fișierele `*-engine.log`, `*-metrics.json`, `*-acceptance.txt`, `results.json` și `fixed-results.json`. Script reproductibil: `run_ab.py`.
