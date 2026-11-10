# Task 1 complet: implementare incrementală versus control

## Protocol

Gyro-S prin OpenCode V2 standalone, aceeași specificație Task 1, aceeași suită externă, același prompt de implementare și testare **fără pauza artificială**, titlu explicit, output 16384, warming OpenCode oprit, încălzire separată. Baze și workspaces izolate; rulări secvențiale: control, apoi intervenție. Limită de 360 s pe sesiune. Varianta experimentală adaugă numai un `AGENTS.md` local care cere implementare Python în secțiuni mici, verificări focalizate și testare finală, fără slăbirea cerințelor. Nu s-au schimbat protecția `answer_room`, pragurile de memorie, modelul sau uneltele.

| Profil | Wall | Stare | Acceptanță externă rerulată | Teste proprii rerulate | Pași / tool calls | Erori tool |
|---|---:|---|---:|---:|---:|---:|
| Control | 245,529 s | finalizat, exit 0 | 20/20 | 11/11 | 9 / 9 | 1 |
| Incremental | 287,155 s | finalizat, exit 0 | 20/20 | 13/13 | 33 / 33 | 4 |

Niciuna nu a expirat. Suita externă neschimbată, SHA-256 `00bcddba2a3901ccac351e6edc9fefcfa6dd2b6a42060f19a00ec5d6217e95e6`, și testele proprii au fost rerulate independent. Testele proprii nu sunt identice și numărul lor nu demonstrează acoperire echivalentă sau calitate mai bună.

## Ce s-a observat

- Prima scriere finalizată a `txreconcile.py`, din timestampul evenimentului tool, a fost la 175,334 s în control și 100,681 s în incremental. Aceste momente arată când apare un fișier, nu când devine complet sau corect. Sesiunea incrementală a executat mai multe `edit`/`write` ulterioare.
- Reasoning maxim raportat pe un pas OpenCode: 12305 tokeni control, 6660 incremental. Logul engine al controlului include un segment de 12288 tokeni generați în 144,860 s; politica automată `answer_room` și limitele interpretării sunt documentate în `gyro-answer-room-audit-20261110`. Aceasta este o singură observație per profil, nu dovada unui efect stabil al instrucțiunii.
- Controlul a avut un shell respins de scanner (`unterminated-quote`). Incrementalul a avut un `edit` fără `path`, un `edit` fără potrivire exactă, o comandă Python cu citare greșită și un test propriu inițial cu aserțiune greșită; ulterior ambele suite au trecut. Testele externe nu dovedesc dispariția tuturor problemelor.
- `engine_request_delta` și `engine_reused_request_delta` din `results.json` scad o fereastră glisantă de 500 de intrări și nu sunt utilizabile ca delte cumulative; vezi `gyro-metrics-window-fix-20261110`.

## Concluzie

Instrucțiunea incrementală a coincis cu o primă scriere mai timpurie și un maxim de reasoning pe pas mai mic, dar sesiunea a fost cu 41,626 s mai lentă și a avut mai multe erori recuperabile în această pereche. Ordinea este fixă și traseele sunt diferite; n=1 nu demonstrează cauzalitate, îmbunătățire sau regresie generală. Nu s-a aplicat instrucțiunea global. Detalii: `results.json`, `*.jsonl`, `*-engine.log`, `*-acceptance.txt`, `http-metadata.json`, `run_title.py`, `summarize.py` și workspaces; JSONL-urile de agent pot conține cod.
