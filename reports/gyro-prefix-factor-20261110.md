# Test sintetic secvențial: pierderea reutilizării prefixului

## Protocol

Cereri sintetice Chat Completions către aceeași instanță Gyro-S, strict secvențiale, cu istoric artificial de assistant tool call și tool result. Fiecare braț pornește cu o cerere de ~10330 tokeni, incluzând 22949 caractere de reasoning sintetic; continuarea adaugă răspunsul real al primei cereri și un mesaj user. `temperature=0`, generare fără thinking, maximum 16 tokeni și aceleași tool definitions; aceste setări sunt doar pentru această probă artificială, nu benchmark de calitate. Fiecare condiție a fost repetată de două ori în ordine inversă. S-a verificat idle înaintea fiecărei cereri. Nu s-au salvat prompturi sau răspunsuri, doar structura, lungimile și contoarele de usage/engine.

## Rezultate continuare

| Schimbare între prime și continuare | Reutilizare 1 | Wall 1 | Reutilizare 2 | Wall 2 |
|---|---:|---:|---:|---:|
| Nicio schimbare a istoricului; doar continuare | 10332/10351 | 0,268 s | 10332/10351 | 0,165 s |
| O cerere auxiliară separată de 22 tokeni între ele | 0/10351 | 5,564 s | 0/10351 | 5,558 s |
| Modificare de 7 caractere în reasoning-ul istoric | 0/10354 | 5,548 s | 0/10354 | 5,751 s |
| Modificare a textului rezultatului tool istoric | 0/10353 | 5,586 s | 0/10353 | 5,527 s |

Toate cererile au avut HTTP 200 și `finish_reason=stop`; `usage.prompt_tokens_details.cached_tokens` a coincis cu `engine_last_reused` la probele înregistrate. RAM disponibil raportat în timpul continuărilor a fost aproximativ 511–821 MiB. Fiecare prime a fost un context distinct și rece, cu 0 reuse. În varianta auxiliară, cererea intercalată a avut ea însăși 0 reuse. Acesta este un experiment controlat pentru traseul sintetic și starea runtime-ului observată: demonstrează că o cerere diferită intercalată poate distruge reuse-ul următoarei continuări în aceste condiții, nu că orice cerere auxiliară face asta în orice condiții sau că reasoning-ul lung în sine e defect.

Schimbarea unui mesaj istoric și intercalarea unei cereri sunt factori diferiți testați separat; nu sunt modificări ale outputului agentului în benchmark. Scăderea la zero nu arată mecanismul intern precis de invalidare și poate depinde de politica de cache și memoria disponibilă. Nu s-au redus pragurile de RAM și nu s-a modificat configurația globală.

## Verificare pe benchmark

Soluția limitată testată pentru evitarea generării automate a titlului în CLI este `--title`; aceasta nu elimină alte cereri auxiliare și nu schimbă Desktop global. Testul ulterior pe Task 2 este în `[HOME]\AppData\Local\Temp\opencode\gyro-prefix-title-task2-20261110\REPORT.md`, cu aceeași suită externă. O cerere fără unelte nu este identificată sigur ca titlu numai pe baza metadatelor redactate.

Dovezi: `results.json`, `probe.py`. Datele de pe disc conțin numai structura/contorii sintetici, nu textul prompturilor/răspunsurilor. Inferențele au fost secvențiale.
