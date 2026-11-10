# Diagnostic Gyro-S / OpenCode V2 — benchmark scurt

## Probleme observate

- CLI-ul din PATH este OpenCode 1.19.5 (V1), în timp ce Desktop folosește 2.2.6. V1 nu acceptă configurația V2 și nu trebuie conectat la baza V2. Testele de mai jos au folosit binarul V2 al Desktop, standalone, cu baze izolate.
- Warming era configurat la fiecare 3 minute timp de 45 minute: logurile arată cereri periodice cu 39.988 de tokeni și un miss de circa 19,6 s. Cu RAM liber puțin pot apărea competiție și recitirea contextului; nu s-a demonstrat că warming a produs toate întârzierile. A fost dezactivat numai pentru Gyro-S; cache-ul Strata rămâne activ.
- PowerShell poate raporta exit 1 pentru `unittest` care a trecut, deoarece progresul merge pe stderr. Rularea 8192 inițială a arătat atât două teste care chiar au eșuat și au fost corectate, cât și ulterior `OK` cu shell exit 1. Soluție: cmd /c cu redirect în cmd și `exit $LASTEXITCODE` în PowerShell; verificată cu succes și eșec real. Instrucțiuni Gyro-S adăugate în AGENTS.md.
- Testul 16384 a inclus un edit fără schimbări; instrucțiunea cere verificarea editărilor. Nu se pretinde dispariția tuturor greșelilor de model.
- Run1 rerun și run6 inițial din raportul istoric s-au suprapus: 1794260977573–1794262659944, respectiv 1794260925026–1794262735860. Timpii nu izolează o singură execuție Gyro-S. Raportul istoric nu dovedește cât ar dura aceeași sarcină fără competiție.

## Rulări secvențiale: taskul Cache original și aceeași acceptanță externă

| Profil | Timp | Pași / tool calls | Output total | Teste proprii | Acceptanță externă |
|---|---:|---:|---:|---:|---:|
| 8192, înainte de instrucțiuni Windows | 145,204 s | 8 / 10 | 9721 | 26/26 | 17/17 |
| 16384, înainte de instrucțiuni Windows | 179,148 s | 10 / 10 | 13116 | 13/13 | 17/17 |
| 8192, după instrucțiuni Windows | 166,305 s | 9 / 9 | 12540 | 26/26 | 17/17 |

Toate exit 0, deadline extern 180 s. Rularea ulterioară a folosit cmd corect, dar a afișat codul în loc de a-l propaga; instrucțiunea a fost corectată. Test suplimentar agent, 35,416 s: suită 26/26 exit 0, modul inexistent exit 1, raportare corectă. Loguri JSONL și metadata alăturate; suita de acceptanță este externă.

## Limitări

- Nu este un A/B statistic: câte o singură rulare pe profil, ordine fixă și teste proprii diferite. Nu dovedește că 8192 este cauza vitezei mai mari. 8192 era deja setat înainte de acest benchmark; poate trunchia răspunsuri lungi.
- Warming este dezactivat pentru toate cele trei rulări V2, deci reducerea latenței cauzată de dezactivare nu a fost măsurată separat. Dezactivarea poate crește latența la reluarea unei sesiuni inactive dacă memoria cache a fost evacuată.
- Acestea nu sunt comparații directe cu Luna, care nu a fost rerulată în aceleași condiții. Un task nu validează proiecte mari și nu dovedește că toate problemele sunt remediate.
- Runtime efectiv observat: Strata 0.1.57, DFlash2, `--vram-reserve-mib 2048`, 131072 context. Nu s-a schimbat configurația Strata sau baza de date OpenCode partajată. V2 standalone a primit OPENCODE_DB și directoare de date/state/cache dedicate.
