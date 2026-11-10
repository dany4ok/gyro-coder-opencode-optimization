# Verificare automată de sintaxă: task scurt derivat din Task 1

## Protocol

Pornind de la `txreconcile.py` care trecea suita externă Task 1, am introdus aceeași regresie controlată în ambele directoare: normalizarea monedei folosea `lower()` în loc de `upper()`. Agentul a primit aceeași cerere scurtă de reparare și verificare, cu OpenCode V2 standalone, Gyro-S, titlu explicit, baze/workspaces izolate, rulări secvențiale și timeout 120 s. Suita externă originală Task 1 a fost rulată înainte și după fiecare sesiune, fără a fi expusă agentului. SHA-256: `00bcddba2a3901ccac351e6edc9fefcfa6dd2b6a42060f19a00ec5d6217e95e6`.

Doar în a doua variantă s-a încărcat un plugin V2 local, reversibil, care rulează `ast.parse` automat după fiecare editare reușită, verificând exclusiv `txreconcile.py` în workspace-ul de test. Nu modifică setările globale. Agentul nu a fost instruit să compileze manual după fiecare editare.

| Variantă | Înainte, extern | Wall | Stare | După, extern | Editări / erori tool | Hook |
|---|---:|---:|---|---:|---:|---|
| Control | 13/20 | 28,847 s | finalizat, exit 0 | 20/20 | 1 / 0 | dezactivat |
| Verificare automată | 13/20 | 50,070 s | finalizat, exit 0 | 20/20 | 1 / 0 | 1 verificare `ok` |

Acceptanța după finalizare a fost rerulată independent: 20/20 pentru fiecare. Taskul este mult mai scurt decât implementarea completă, fiind o reparație țintită, și nu dovedește fiabilitatea pe Task 1 complet. Agenții au folosit 4 versus 9 tool calls; n=1 per variantă și traseele diferite nu permit estimarea overheadului pluginului sau a unei îmbunătățiri de performanță.

## Probă a căii de eroare

Într-o sesiune separată și un al treilea workspace, agentul a introdus intenționat prin `edit` o linie Python incompletă, apoi a reparat-o. Hook-ul a raportat `syntax_error`, iar tool-ul a returnat eroarea de sintaxă; la editarea de reparare hook-ul a raportat `ok`. După reparare, `ast.parse` și acceptanța externă au trecut, 20/20.

**Limitare importantă:** hook-ul rulează după execuția editării. Deși tool-ul a raportat eroare, fișierul cu sintaxă invalidă fusese deja scris pe disc și a necesitat o altă editare pentru reparare. Un agent ar putea confunda mesajul cu un rollback. Această implementare este un diagnostic local, nu o protecție tranzacțională, nu acoperă alte fișiere Python sau editări prin shell și nu este sigur de recomandat global în forma sa actuală. Verificarea sintaxei nu verifică semantica.

Date și dovezi: `results.json`, `*-before-acceptance.txt`, `*-after-acceptance.txt`, `baseline.jsonl`, `automatic-check.jsonl`, `probe.jsonl`, `failure-probe/syntax-hook.jsonl`, workspaces, `syntax-plugin.js`, `run.py`. Logurile JSONL pot conține cod și mesaje; pluginul este prezent doar în workspaces experimentale.
