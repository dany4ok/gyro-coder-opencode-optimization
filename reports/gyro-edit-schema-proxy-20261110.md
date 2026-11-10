# Schema `edit`: ordine diferită a câmpurilor, proxy experimental

## Diagnostic

În sesiunile finalizate `gyro-preedit-syntax-20261110/automatic-check` și `gyro-repeat-20261110/limit16384-b`, tool-ul `edit` a respins apeluri fără `newString`. Pasul asociat s-a încheiat cu `reason=tool-calls`, iar OpenCode raporta 192, respectiv 330 tokeni output, cu plafon configurat 16384. Aceasta nu susține ipoteza unei trunchieri simple la limita output, deși valorile singure nu identifică locul exact unde s-a pierdut câmpul. Validarea a respins apelurile, iar agenții au continuat.

O primă tentativă de schimbare prin plugin `gyro-edit-schema-order-20261110` nu a modificat schema: `tool.input` în versiunea instalată expune `fields`, `mapFields`, `ast`, nu JSON Schema direct. Captura HTTP a rămas identică în ambele brațe. Cele două rulări au terminat cu 20/20 extern, dar **nu constituie un A/B valid pentru intervenție**.

## A/B efectiv prin proxy local

Task scurt derivat din Task 1: reparația regresiei controlate `currency.lower()` în loc de `upper()` într-un CLI existent; același prompt, output 16384, OpenCode V2 standalone, titlu explicit, warming oprit, încălzire separată, baze și workspaces izolate, 120 s deadline. Controlul este urmat secvențial de o variantă cu proxy local care schimbă exclusiv ordinea proprietăților JSON ale schemei `edit` în cererile către Strata: `newString, path, oldString, replaceAll` în loc de `path, oldString, newString, replaceAll`. Schema canonicalizată cu chei sortate este verificată egală înainte/după, iar lista `required` și executorul nativ nu sunt modificate. Proxy-ul este doar al benchmarkului și nu schimbă configurația globală. Ordinea de pe fir a fost verificată; nu se cunoaște dacă template-ul engine păstrează această ordine la tokenizare.

| Profil | Wall | Stare | Acceptanță externă | Teste proprii rerulate | Erori raportate |
|---|---:|---|---:|---:|---|
| Control | 60,657 s | finalizat, exit 0 | 20/20 | 2/2 | 2 shell exit 1 |
| Ordine experimentală | 72,435 s | finalizat, exit 0 | 20/20 | script propriu exit 0 | un `edit` invalid și un shell exit 1 |

Suita externă Task 1 a fost rerulată independent în ambele workspace-uri, SHA-256 neschimbat `00bcddba2a3901ccac351e6edc9fefcfa6dd2b6a42060f19a00ec5d6217e95e6`. În control, eșecurile shell au fost un JSON cu BOM și un `SyntaxError` de cale Windows; apoi testele proprii trec 2/2. În experiment, agentul a trimis un apel `edit` cu `path` și `content`, fără `oldString` și `newString`: schema nativă l-a respins. A creat apoi `currency_check.py` în directorul experimental părinte, în afara workspace-ului; prima lui rulare a eșuat la o aserțiune de număr de înregistrări, corectată ulterior. Scriptul a fost rerulat independent, exit 0. Nu au fost șterse fișierele create.

Captura HTTP redactată: 13/13 cereri control cu ordinea originală, 14/14 experimentale cu ordinea propusă și transformarea marcată ca aplicată; toate cererile capturate au HTTP 200. Numărul și conținutul testelor proprii diferă; trecerea lor nu este o comparație completă de calitate. Câmpurile `engine_request_delta`/`engine_reused_request_delta` din harness scad o fereastră glisantă și nu sunt utilizate pentru concluzii.

## Concluzie

Omiterea argumentelor a reapărut chiar cu ordinea experimentală; nu se dovedește că transformarea a provocat-o sau că va eșua în toate cazurile. O singură pereche, ordine fixă și trasee diferite nu demonstrează o schimbare fiabilă a latenței sau calității. Varianta experimentală a fost mai lentă în această pereche și a avut o eroare de edit recuperabilă, deci nu este recomandată global. Nu s-au modificat sursa Strata sau configurația utilizatorului.

Dovezi: `results.json`, `http-metadata.json` redactat, `*.jsonl`, `*-acceptance.txt`, `*-engine.log`, `run_title.py`, workspace-uri și `currency_check.py`. Logurile de agent pot conține cod.
