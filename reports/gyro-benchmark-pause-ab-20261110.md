# Efectul pauzei artificiale din benchmarkul local

## Diagnostic

Specificația utilizatorului `Downloads/benchmark_gyro_luna_30min.md` cere timpi reali și aceleași taskuri, dar nu cere o pauză de 12 secunde. Mai multe benchmarkuri experimentale ulterioare au introdus intenționat `python -c "import time; time.sleep(12)"` pentru investigații de cache. Aceasta este o întârziere a protocolului experimental, nu o problemă intrinsecă Gyro-S/OpenCode. A nu o include în benchmarkurile viitoare care nu studiază pauze este o schimbare locală și reversibilă a promptului; nu schimbă modelul, uneltele sau configurația.

## Comparație secvențială

Task 2 complet cu aceeași specificație, suită externă și instrucțiuni de implementare/testare; singura diferență intenționată este cerința de a rula pauza înainte de implementare. OpenCode V2 standalone, Gyro-S, titlu explicit, output 16384, warming OpenCode oprit, încălzire separată, baze/workspaces izolate, limită 210 s. Ordine fixă: cu pauză, apoi fără. Proxy HTTP redactat. Suita externă neschimbată SHA-256 `94918e3c5f113f6ed3c896740aac007261c821c9aa281937fa0e9518c82fb205`.

| Profil | Wall | Stare | Extern rerulat | Teste proprii rerulate | Erori tool |
|---|---:|---|---:|---:|---|
| Cu pauză | 152,207 s | finalizat, exit 0 | 17/17 | 15/15 | un `edit` fără `newString`, un shell cu teste eșuate |
| Fără pauză | 157,983 s | finalizat, exit 0 | 17/17 | 23/23 | un shell cu teste eșuate |

Agentul a corectat ulterior testele eșuate în ambele sesiuni. Numărul de teste proprii nu este un scor comparabil de calitate. Pauza a fost observată la shell în control: timestamp start 1794290104486 ms, end 1794290117817 ms, adică **13,331 s** incluzând overheadul tool-ului, față de minimum 12 s cerute. Varianta fără pauză nu conținea acel apel. Nicio rulare nu a expirat.

## Interpretare

Chiar dacă pauza observată este muncă artificială, rularea fără pauză a durat cu 5,776 s mai mult: au existat trasee și cantități diferite de generare și teste. Nu se poate estima timpul contrafactual al aceleiași execuții prin simpla scădere a 12 sau 13,331 s; pauza poate influența schedulingul și cache-ul. O singură pereche nu demonstrează un speedup sau o îmbunătățire de calitate. Eliminarea ei în viitoare benchmarkuri de lucru obișnuit face protocolul mai reprezentativ și evită acel timp impus, dar nu este remediu al latenței modelului. Nu se compară direct cu istoricul care include pauza fără a menționa diferența.

Metricile `engine_request_delta`/`engine_reused_request_delta` din harness sunt invalide după saturarea ferestrei de 500 și nu au fost utilizate; vezi `gyro-metrics-window-fix-20261110`. Nu s-au schimbat setările globale. Dovezi: `results.json`, `*.jsonl`, `*-acceptance.txt`, `*-engine.log`, `http-metadata.json`, `run_title.py` și workspaces. JSONL-urile de agent pot conține cod.
