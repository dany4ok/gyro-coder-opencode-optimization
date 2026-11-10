# Limită implicită de thinking Strata la output 16384

## Constatare și corecție de interpretare

Două rulări Task 1 au raportat exact 12305 tokeni reasoning pentru un pas, în `gyro-tools-reverse-task1-20261110/restricted-task1.jsonl` și `gyro-replay-ab-20261110/normal-replay.jsonl`. Nu este corect să interpretăm absența unui `reasoning_budget_tokens` explicit drept absența oricărei limite aplicate intern.

`Strata/control/serve/server.py` liniile 5894–5904 arată că, atunci când thinking este activ, nu există buget explicit și `answer_room` este activ, wrapperul rezervă loc pentru răspuns: la `max_new=16384`, pragul de încheiere a thinking-ului este `16384 - 4096 = 12288`. Codul ulterior poate continua cu un text de închidere înainte de răspuns. În `AppData/Local/Strata/runtime/app-1.server.log` există două mesaje `thinking budget reached (12288 tokens): wrapping up the thinking`, urmate de `writing a tool call: write`; progresul anterior indică aproximativ 140–142 s până la prag în aceste execuții. Aceste mesaje stabilesc activarea mecanismului la acel prag, nu o asociere certificată la milisecundă cu fiecare JSONL și nici o explicație exactă pentru toți cei 17 tokeni peste prag.

## Experiment local cu engine simulat

`test_answer_room_16384.py` folosește `ThinkingEngine` și `ByteTokenizer` din suita de teste Strata, în proces de test izolat, nu modelul real și nu serviciul activ. Cu context simulat 131072, output 16384 și aceeași secvență artificială lungă de thinking:

- `answer_room` activ: mesaj `thinking limited to 12288`, buget atins, **HTTP 200 / finish stop / răspuns prezent**, două segmente engine.
- `answer_room` dezactivat pe instanța fake, după aceea: **HTTP 200 / finish length / răspuns absent**, un segment engine.

Comanda `python -m unittest -v test_answer_room_16384`, cu `PYTHONPATH` spre `Strata/control` și Python-ul Strata, a trecut **1/1**. O primă încercare a folosit context fake implicit 4096, deci serverul a redus output-ul la 3840; testul a fost corectat explicit la 131072 și rerulat. Testul fake ilustrează de ce oprirea protecției poate crea o regresie de calitate; nu prezice că orice răspuns real va fi gol, nici nu este benchmark de performanță GPU.

## Acceptanță și concluzie

În rularea reală `normal-replay` cu protecția activă, Task 1 a terminat în 274,874 s; acceptanța externă a fost rerulată independent **20/20**, iar testele proprii **12/12**. Varianta istorică de eliminare a reasoning-ului din replay este o intervenție diferită și a expirat la 360 s; nu este un control `answer_room` on/off.

Nu a fost rulat un A/B live cu protecția dezactivată: proba fake arată risc concret de răspuns trunchiat, iar userul a cerut păstrarea calității. Nu există o remediere sau accelerare demonstrată aici. Nu s-au schimbat setările active, bugetul de reasoning sau configurația globală. Rezultatul rafinează diagnosticul: 16384 output și lipsa bugetului explicit pot coexista cu un plafon automat intern de 12288 tokeni de thinking. Orice comparație viitoare trebuie să verifice această politică separat de bugetele explicite și să distingă timeout, output trunchiat și corectitudinea artefactelor parțiale.
