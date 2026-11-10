# Investigarea implementării parking-ului Strata

## Constatări verificabile

- Runtime-ul observat este `strata.exe` 0.1.57 din componenta instalată Strata. Căutarea sursei `generate.cpp` în `[HOME]\Desktop\Strata AI` nu a găsit implementarea engine-ului; textul exact al politicii interne de parking nu a fost inspectat. `control/serve/server.py` colectează evenimente din log și expune metrici, dar nu implementează admission-ul engine-ului.
- Metricile live read-only au raportat cache conversațional activ, buget 3840 MiB, 4 sloturi, 2 parcate, 481820660 bytes, 134 evenimente park și 18 restore de la pornire. `last_event=parked` este o valoare istorică, nu dovada că parking-ul reușește la RAM-ul disponibil actual. RAM aproximativ disponibil calculat din metricile Strata: 545 MiB; engine idle, coadă 0.
- Probele anterioare `gyro-parking-size-20261110/results.json` au documentat refuzuri cu floor 2560 MiB și reutilizare zero după cerere intercalată. Ele nu dovedesc că ridicarea RAM-ului ar rezolva problema și nu trebuie confundate cu octeții fizici citiți de pe disc.

## Cache SSD istoric: de ce nu este un remediu verificat aici

`docs/persistent-session-cache.md` descrie un cache SSD distinct, activat opt-in pentru conversații cu `sessionId`, iar `host/server/persistent-session-cache.mjs` implementează save/restore prin endpointul de slot și fallback la istoric complet. `node --test host/server/persistent-session-cache.test.mjs` a trecut **5/5** la această verificare; testele folosesc fetcher simulat și nu demonstrează funcționare live sau compatibilitate cu OpenCode.

În arborele `host` curent, căutarea `createPersistentSessionCache` găsește doar definiția și testele; căutarea importului `persistent-session-cache` găsește doar testul. Nu s-a stabilit că sursa `host` este exact binarul/procesul host activ, astfel absența referințelor nu dovedește singură comportamentul binarului instalat. În plus, benchmarkurile OpenCode din această investigație merg prin gateway-ul Chat Completions, nu s-a demonstrat că transmit un `sessionId` compatibil cu managerul respectiv.

Worklogul istoric `docs/persistent-session-cache-worklog-2026-11-06.txt` consemnează că SAVE a fost refuzat la floor 2560 MiB, iar soluția istorică opt-in a folosit floor 256 MiB și `session-save-reclaim`. Reducerea floor-ului încalcă restricția curentă de siguranță. Documentul SSD raportează un benchmark save/restore cu restart și cache rece, nu o comparație live OpenCode cu același prag RAM și aceeași suită externă. Nu se extrapolează cifrele sale la această sesiune.

## Decizie

Nu a fost identificată o intervenție nouă pentru engine-ul activ care să păstreze pragul de 2560 MiB și să poată fi validată în siguranță cu RAM-ul actual. Nu am activat cache SSD, nu am schimbat fișiere de configurare, nu am repornit procese și nu am făcut modificări ale bazei partajate. Nu am rulat un benchmark de acceptanță pentru o intervenție neverificată sau inexistentă.

O comparație cauzală ar necesita acces la sursa engine-ului sau un mecanism suportat de reclamare care menține floor-ul, plus suficient RAM disponibil ca un SAVE/park să treacă admission-ul și un traseu OpenCode cu identitate de sesiune demonstrată. Alternativ, utilizatorul ar putea elibera voluntar memorie ori furniza o mașină cu mai mult RAM. Orice rezultat ar trebui apoi comparat secvențial cu controlul pe aceleași suite externe; nu există încă dovadă de accelerare în acest caz.
