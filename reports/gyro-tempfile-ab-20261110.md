# Erori de fișiere temporare Windows în teste de persistență

## Reproducere

Sesiunea finalizată `gyro-title-hook-local-20261110/title-hook.jsonl` a avut patru `PermissionError` în testele de persistență: testele țineau deschis un `NamedTemporaryFile`, apoi `LRUCache.save`/`load` încerca să redeschidă aceeași cale pe Windows. Agentul le-a corectat ulterior. Este un incident observat în istoricul analizat, nu o frecvență stabilită pe toate sesiunile.

Am reconstruit în `seed/` primele apeluri `write` pentru `cachekit.py` și `test_cachekit.py` din acea sesiune, fără a schimba fișierele originale. `python -m pytest -q --tb=short test_cachekit.py`: **13 trecute, 5 eșuate**, dintre care patru `PermissionError` și o aserțiune TTL greșită independentă. Implementarea inițială trece suita externă Task 2 **17/17**. Aceasta reproduce eșecul pe Windows, nu dovedește un defect al tool-ului OpenCode.

## Comparație locală

Sarcină scurtă identică: pornește din cele două fișiere seed, rulează testele existente, repară-le păstrând scopul și nu modifica implementarea. OpenCode V2 standalone, Gyro-S, rulări secvențiale cu titlu explicit, încălzire separată, output 16384 și timeout 150 s; workspaces și baze izolate. Varianta a doua are doar un `AGENTS.md` local care explică redeschiderea `NamedTemporaryFile` pe Windows și sugerează `TemporaryDirectory` sau închiderea handle-ului, fără a slăbi testele. Suitele externe Task 2 sunt identice și nemodificate, SHA-256 `94918e3c5f113f6ed3c896740aac007261c821c9aa281937fa0e9518c82fb205`.

| Profil | Wall | Stare | Extern rerulat | Teste proprii rerulate | Prima rulare a testelor |
|---|---:|---|---:|---:|---|
| Control | 149,513 s | finalizat, exit 0 | 17/17 | 19/19 | shell exit 1, patru `PermissionError` |
| Instrucțiune locală | 100,023 s | finalizat, exit 0 | 17/17 | 18/18 | shell exit 1, patru `PermissionError` |

Fișierul `cachekit.py` are același SHA-256 `f9f1880dfecd0ea1ec06743a9d406262fb92d2d5e7232fc4421ca33ef6011db4` în seed și ambele rezultate. Ambele suite finale păstrează toate cele 18 nume de teste inițiale; controlul adaugă unul. Numărul de teste și aserțiuni nu demonstrează singur păstrarea acoperirii.

## Analiză de calitate

Controlul a închis handle-ul `mkstemp` înainte de redeschidere și a corectat ceasul de expirare la limita relevantă, adăugând un test distinct de trunchiere LRU. Varianta cu instrucțiune a folosit `TemporaryDirectory` pentru a evita problema Windows și a corectat o altă aserțiune TTL; totuși în `test_load_drops_expired_entries_and_trims_to_max_size` ceasul rămâne 0, în timp ce presupusul element expirat are `expires_at=10.0`. Testul poate trece prin eliminarea celui mai vechi element la depășirea limitei, fără a demonstra eliminarea unui element expirat. Astfel **18/18 nu validează complet intenția testului**, iar diferența de acoperire face comparația de timp neechivalentă.

Promptul cerea explicit rularea testelor inițiale, deci ambele variante au întâlnit în mod așteptat cele patru erori înainte de remediere; experimentul nu măsoară prevenirea lor la generarea de teste noi. O singură pereche, ordine fixă și trasee diferite nu demonstrează că instrucțiunea accelerează execuția sau îmbunătățește calitatea. Nu s-a aplicat global; rezultatul mai rapid nu justifică această schimbare.

Date: `seed/`, `baseline/`, `tempfile-guidance/`, `results.json`, `*-acceptance.txt`, `http-metadata.json`, `*.jsonl`, `run_title.py`. JSONL-urile pot conține cod; metadatele HTTP sunt redactate. Contoarele engine pot varia din cauza ferestrei de captură; nu sunt folosite aici pentru o concluzie de performanță.
