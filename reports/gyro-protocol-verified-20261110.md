# Gyro-S — integrarea reasoning / tool calls

## Înainte de corecție

O probă cu același Gyro-S și câte un apel shell a folosit OpenCode V2 prin Chat Completions și Codex CLI prin Responses, secvențial. Proxy-ul localhost a păstrat numai numere și prezența câmpurilor, nu textul de reasoning, prompturile, răspunsurile sau antetele. OpenCode a primit 144 caractere de `reasoning_content` în streamul răspunsului cu tool call; următoarea cerere a conținut 144 caractere în câmpul anterior și un tool result. Codex a primit 154 caractere reasoning și le-a inclus în următorul request Responses, împreună cu tool call/result. Ambele au răspuns corect `RESULT: 837`. Nu s-a reprodus pierdere de reasoning la hand-off.

În schimb, OpenCode a raportat `reasoning: 0` pentru ambele etape, deși existau reasoning deltas. `serve/server.py` calcula intern `reasoning_tokens`, dar `openai_chunks` nu includea `usage.completion_tokens_details.reasoning_tokens`. Ruta Responses îl includea deja în `output_tokens_details`. Înainte de corecție, testul `test_usage.py` a avut două `KeyError` reproductibile pentru valoare nenulă și zero.

## Remediere

În `[HOME]\Desktop\Strata AI\Strata\control\serve\server.py`, Chat Completions transmite acum contorul intern existent în `usage.completion_tokens_details.reasoning_tokens`. Câmpul rămâne absent dacă numărul lipsește, nu este întreg valid sau depășește `completion_tokens`; nu se estimează tokenii din text. Nu s-au schimbat generarea, reasoning-ul, modelul sau contextul. Backupul exact al sursei este `[HOME]\AppData\Local\Temp\opencode\gyro-protocol-redacted-20261110\server-before-usage-fix.py` (SHA-256 `589ec01c3f11587296c5a54535084bfda129c3c299507d413c376581a3e9d2b3`); sursa curentă SHA-256 `22959ba10b46db29beda578129b9a54ff1db1e3b8f3f978310904aa858cf59f5`. Sursa nu este într-un repository Git; diff-ul constă exclusiv în cele cinci linii de raportare/comentariu. S-a adăugat testul `serve/test_chat_reasoning_usage.py`.

Restartul Strata a fost gestionat prin profilul `app-1`, după verificarea idle, identității și hash-ului configurației; runtime a revenit `ready`, același model și context 131072. Această modificare este în sursa locală Strata și poate fi suprascrisă de un update Strata; nu este o modificare a parametrilor globali de generare.

## Verificare după corecție

- Probe secvențiale prin proxy: OpenCode shell exit 0, `RESULT: 837`, wall 14,883 s; Codex shell exit 0, același rezultat, 24,911 s. Pe OpenCode, streamul a raportat 55 și 22 tokeni reasoning în cele două etape; câmpurile de reasoning au fost retransmise. Codex a continuat să primească propriile contoare Responses. Timpii unor probe atât de mici nu sunt benchmark comparabil între agenți.
- Test de regresie Strata: `python -m unittest serve.test_chat_reasoning_usage serve.test_request_accounting -q` → **13/13**, inclusiv Chat streaming/non-streaming, plus `serve.test_responses` → **47 teste OK, 1 skipped**. Testele rulează cu Python-ul inclus în Strata.
- Același Task 2 Cache din benchmark, OpenCode V2 standalone: **140,712 s, exit 0**, acceptanță externă **17/17**, teste proprii **27/27**. A fost observat un shell exit 1 pe parcurs, urmat de o execuție shell exit 0; conținutul testului eșuat nu a fost păstrat deoarece captura acestui diagnostic este redactată. `acceptance-summary.json` conține `correct_final: false`, care verifică exclusiv șirul `RESULT: 837` al smoke-testului anterior și este **neaplicabil Task 2**; nu este rezultatul acceptanței. Scriptul a fost corectat după rulare pentru a nu mai genera acel indicator pe benchmark.
- Pe Task 2: 14 cereri chat redactate, toate HTTP 200 și cu `reasoning_tokens` în usage; toate cele 13 etape principale au raportat reasoning nenul. Cele 12 cereri ce conțineau tool results au inclus câmpurile de reasoning anterioare. Acestea sunt verificări de prezență și lungime, nu comparație a conținutului reasoning.

## Limitări

Aceasta repară **contabilizarea tokenilor de thinking**, nu dovedește o îmbunătățire a vitezei sau eliminarea erorilor Gyro-S. Timpii precedenți rămân afectați de variația de memorie/cache; un singur benchmark Task 2 nu demonstrează fiabilitatea generală. Nu s-au aplicat global limite noi de reasoning. Sursa de acceptanță nu a fost modificată, SHA-256 `94918e3c5f113f6ed3c896740aac007261c821c9aa281937fa0e9518c82fb205`.

`metadata.json`, `smoke-metadata.json`, `*-summary.json`, `acceptance-summary.json`, `probe.py`, `benchmark.py` conțin doar metadate/procedură; implementarea și testele generate sunt în `acceptance-work/`. Bazele SQLite izolate ale acestor probe au fost eliminate după test; baza de date OpenCode partajată nu a fost modificată de probe.
