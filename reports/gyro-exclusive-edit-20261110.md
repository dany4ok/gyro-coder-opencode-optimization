# Unealtă experimentală de editare Python cu handle exclusiv

## Ce am investigat

Documentația OpenCode V2 descrie hook-uri `execute.before` și `execute.after`, dar nu garantează că validarea unui hook `before` și scrierea tool-ului `edit` sunt o singură tranzacție. În investigația anterioară, `edit` a acceptat un `oldString` care apărea o singură dată dar acoperea doar începutul unui bloc și a lăsat restul vechi în fișier, producând `IndentationError`; în acea probă tool-ul a aplicat textul cerut. Nu am verificat exhaustiv algoritmul intern OpenCode de potrivire flexibilă sau toate cazurile de editări concurente ale tool-ului nativ. Prototipul anterior bazat pe hook poate verifica un text diferit de cel aplicat dacă semantica de matching diferă sau fișierul se schimbă între verificare și scriere.

## Prototip local și teste deterministe

În workspaces experimentale, pluginul înlocuiește `edit` cu `safe_python_edit`, limitat deliberat la `txreconcile.py`. Programul `safe_edit.py` deschide fișierul existent cu Windows `CreateFileW`, share mode 0, citește, aplică o singură înlocuire literală unică în memorie, rulează `ast.parse`, apoi scrie prin același handle exclusiv. Respinge lipsă/ambiguitate, no-op, non-UTF-8 și sintaxă invalidă. Nu este o implementare generală a OpenCode `edit`.

`python -m unittest test_safe_edit -v`: **6/6** trecute, inclusiv edit invalid fără schimbarea fișierului, edit valid, fragment ambiguu/lipsă/no-op, păstrarea CRLF, refuzul unui al doilea proces de a deschide fișierul în timpul handle-ului exclusiv și refuzul editării când există un handle extern incompatibil. Acestea sunt probe ale mecanismului local pe Windows, nu o caracterizare completă a concurenței din OpenCode.

## Benchmark scurt secvențial

Taskul repară aceeași regresie controlată `currency.lower()` în loc de `upper()` într-un CLI deja existent din Task 1; aceeași suită externă originală de 20 teste înainte și după, Gyro-S/OpenCode V2 standalone, workspaces și baze izolate, 120 s limită. Ordine contrabalansată control A, protejat A, protejat B, control B. Promptul cere folosirea unei unelte de editare; pluginul există doar în variantele protejate. SHA-256 suita externă `00bcddba2a3901ccac351e6edc9fefcfa6dd2b6a42060f19a00ec5d6217e95e6`.

| Rulare | Wall | Status | Extern înainte → după | Tool calls | Erori raportate |
|---|---:|---|---:|---:|---|
| Control A | 49,998 s | exit 0 | 13/20 → 20/20 | 10 | un shell exit 1 la test propriu, corectat |
| Protejat A | 33,994 s | exit 0 | 13/20 → 20/20 | 5 | zero raportate |
| Protejat B | 22,846 s | exit 0 | 13/20 → 20/20 | 4 | zero raportate |
| Control B | 51,980 s | exit 0 | 13/20 → 20/20 | 8 | zero raportate |

Ambele rulări protejate au apelat efectiv `safe_python_edit`, prin Code Mode. În protejat A agentul a scris un test propriu în directorul `scratch` din afara workspace-ului și nu l-a rulat; rerularea independentă a rezultat **3/4**, cu o așteptare pentru o monedă doar `pending` contrară semanticii specificației. În protejat B testul propriu a trecut 3/3. Prin urmare exit 0 și 20/20 extern nu dovedesc că testele proprii au fost rulate sau sunt corecte.

Diferențele de timp nu demonstrează un speedup fiabil: câte două execuții pe o singură reparație simplă, trasee și cantități de teste diferite, iar una dintre variante nu și-a rulat propriul test. Nu se extrapolează la Task 1 complet.

## Limite și siguranță

Unealta e un experiment opt-in, nu o remediere globală: acoperă un singur fișier și potrivire literală unică, în timp ce `write`, shell și alte unelte pot modifica fișierul pe alte căi. `ast.parse` nu verifică semantica. Handle-ul exclusiv protejează intervalul de acces împotriva altor deschideri incompatibile, dar nu oferă tranzacție rezistentă la căderi ale procesului/sistemului în timpul scrierii; rollback-ul din cod este doar best-effort pentru excepții prinse. Tratamentul linkurilor/joncțiunilor și al encodingurilor este intenționat restrâns. Nu se recomandă folosirea globală fără implementare și teste mai ample.

Date: `results.json`, `*-before-acceptance.txt`, `*-after-acceptance.txt`, `*.jsonl`, `safe_edit.py`, `test_safe_edit.py`, `syntax-plugin.js`, `run.py` și workspaces. JSONL-urile conțin cod/apeluri, nu sunt redactate.
