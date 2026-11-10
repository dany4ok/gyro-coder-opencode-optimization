# Analiză consolidată și setări alese

## Stare și concluzie

Nu a fost demonstrată o optimizare fiabilă, repetabilă, care să îmbunătățească simultan latența și calitatea pe Task 1 complet. Au fost corectate probleme punctuale; erorile recuperabile și variația timpului rămân. Studiile locale au folosit, în general, OpenCode Desktop V2 standalone, Gyro-S secvențial și baze izolate; nu sunt o comparație statistică exhaustivă cu alți agenți.

## Modificări active și justificare

| Setare / remediere | Stare verificată | Justificare și limită |
|---|---|---|
| Context 131072, output 16384 | existentă în configurația OpenCode | Output 8192 a trunchiat un apel `write`; 16384 reduce riscul, fără garanție absolută. |
| `headerTimeout=900000` | existent, la nivelul providerului | Evită un timeout de antet prea scurt; nu accelerează inferența. |
| Warming OpenCode dezactivat doar pentru Gyro-S | existent | Evită cereri auxiliare periodice; efectul asupra latenței la reluare nu a fost măsurat fiabil. Cache-ul Strata nu a fost dezactivat. |
| Instrucțiuni Windows pentru Gyro-S | existente în `AGENTS.md` global | PowerShell, propagarea exit-ului `unittest`, argumentele `edit` și evitarea no-op; nu elimină toate erorile. |
| `reasoning_tokens` în Chat Completions | modificare în sursa Strata locală, testată | Repară raportarea, nu timpul de inferență; poate fi suprascrisă de un update. Patch-ul este în `fixes/`. |
| Rezervă VRAM 2048 MiB | observată la runtime în această investigație | Modificare anterioară, cu acordul utilizatorului, de la 1536 MiB; marja și performanța rămân variabile. Nu reduce pragul de siguranță. |

Configurația curentă păstrează protecția Strata `answer_room`, contextul și pragurile RAM. Nu există un buget de reasoning *explicit* în configurația OpenCode; totuși `answer_room` poate închide automat thinking-ul la 12288 tokeni când limita output este 16384, pentru a rezerva spațiu răspunsului. Un test cu engine simulat a arătat un răspuns gol la dezactivarea protecției; nu s-a demonstrat că asta se întâmplă pentru fiecare cerere reală.

## Dovezi reprezentative

- Task 1 complet, control versus instrucțiune incrementală: 245,529 s și 287,155 s, ambele finalizate cu 20/20 extern; testele proprii 11/11 și 13/13. O singură pereche cu trasee diferite nu susține cauzalitate. `reports/gyro-incremental-task1-20261110.md`.
- Task 1 cu replay normal a terminat în 274,874 s cu 20/20 extern; eliminarea experimentală a reasoning-ului istoric a expirat la 360 s, cu 20/20 pe artefactul parțial și fără teste proprii. Timeoutul nu este un timp complet. `reports/gyro-replay-ab-20261110.md`.
- Task 2, 4 versus 12 unelte: în două perechi ordinea diferenței de timp s-a inversat; toate patru au finalizat 17/17 extern. Nu se restrâng uneltele global. `reports/gyro-tools-reverse-task1-20261110.md`.
- Într-o probă sintetică, după cereri intercalate s-a pierdut reutilizarea prefixului pe fundal de presiune RAM. Probele de titlu nu au demonstrat că intercalarea apărea în pașii principali sau că soluția accelera stabil un benchmark real. `reports/gyro-parking-size-20261110.md` și `reports/gyro-title-hook-local-20261110.md`.
- În rulări observate, prima scriere a Task 1 poate fi precedată de multe mii de tokeni thinking; lungimea reasoning-ului nu implică automat cache miss. `reports/gyro-answer-room-audit-20261110.md`.
- CLI-ul V1 de pe PATH și Desktop V2 au folosit formate incompatibile de configurație/bază. Benchmarkurile ulterioare au folosit V2 standalone și baze separate; nu se îndreaptă V1 către baza partajată V2. `reports/gyro-v2-short-20261110.md`.

## Ce nu s-a aplicat

Nu s-au aplicat global `reasoning_effort=low`, bugete mai mici, temperatură zero, restrângerea uneltelor, eliminarea reasoning-ului istoric, pluginurile de editare/titlu sau reducerea pragurilor RAM. Testele au fost insuficiente, contradictorii sau au arătat risc de calitate. Ordinea proprietăților schemei `edit` nu a prevenit o eroare de argumente lipsă în singura pereche validă. Verificările de sintaxă prototip au limitări de atomicitate/acoperire.

Pauza artificială de 12 secunde din unele prompturi experimentale nu face parte din cerința inițială. Comparațiile noi de performanță obișnuită ar trebui să o omită și să nu fie comparate direct cu cele care o includ.

## I/O și cache: interpretare

Tokenii cache Strata, contoarele I/O atribuite procesului și citirile fizice Windows la nivel de sistem sunt categorii diferite. Octeții citiți atribuiți procesului nu dovedesc cât s-a citit fizic de pe SSD; cifrele de file tier pot fi servite din cache-ul OS. Nu le însuma și nu le prezenta drept aceeași măsură. O diferență a `conversation_cache.requests` poate fi zero sau negativă după rotirea istoricului și nu este contor cumulativ; folosește `totals` cu verificarea identității `since` și loguri complete.

Rapoartele istorice pot conține concluzii supersedate, referințe la fișiere neincluse și calcule bazate pe timeout sau pe valori necomparabile. Folosește tabelele cu starea sesiunii și verifică protocolul original înainte de a calcula vreun speedup.
