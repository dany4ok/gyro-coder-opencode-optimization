# Task 1: titlu automat versus explicit

OpenCode V2 standalone, Gyro-S, aceeași specificație Task 1, aceeași suită externă, încălzire și prompt cu pauză artificială de 12 s. Rulări secvențiale, baze și workspace-uri izolate, output 16384, warming oprit, deadline 240 s. Singura diferență intenționată: `--title "Transaction benchmark"` în a doua rulare. Metadatele HTTP sunt redactate; logurile de agent pot conține cod.

| Profil | Timp | Stare | Acceptanță externă rerulată | Teste proprii rerulate | Erori tool |
|---|---:|---|---:|---:|---|
| Titlu automat | 240,092 s | TIMEOUT | 20/20 pe artefact parțial | 9/9 | trei shell exit 1 |
| Titlu explicit | 179,010 s | Finalizat, exit 0 | 20/20 | 14/14 | zero raportate |

La timeout, testele evaluează doar fișierele existente și nu demonstrează finalizarea. Testele proprii sunt generate diferit și numărul lor nu măsoară comparativ calitatea.

## Cereri auxiliare și cache

În varianta automată, captura conține 18 cereri chat, dintre care una fără unelte, începută la 1,301 s; prima cerere cu 12 unelte a început la 1,315 s. Logul engine arată mai întâi cererea de 572 tokeni, 0 reutilizați, 1124 ms prefill și 4300 ms generare, apoi promptul principal de 6102 tokeni, 0 reutilizați și 4466 ms prefill. Cererea fără unelte este compatibilă cu generarea titlului, dar metadatele capturate nu includ conținut și nu identifică singure rolul ei cu certitudine. În acest caz ea a fost procesată înaintea promptului principal, nu între doi pași principali, astfel nu se demonstrează aici o întrerupere a cache-ului unui task deja început.

În varianta cu titlu explicit s-au capturat 10 cereri, toate cu unelte: nicio cerere fără unelte. Primul prompt principal a avut 6102 tokeni, 0 reutilizați și 4106 ms prefill; următorul a reutilizat 6172/6992 tokeni. Rezultatul este compatibil cu evitarea cererii auxiliare prin `--title`, pentru această sesiune CLI. Într-o rulare anterioară diferită, o cerere auxiliară scurtă a fost procesată între cereri principale și a fost urmată de 0/7121 reutilizați; asocierea temporală nu dovedește de una singură cauzalitatea.

## Limite

Nu se poate atribui diferența de timp sau de erori opțiunii de titlu: o singură pereche, ordine fixă, o rulare cenzurată la timeout și trasee de generare diferite. `--title` este o opțiune pentru rulări CLI, nu o remediere generală demonstrată pentru Desktop. Nu s-a schimbat configurația globală și nu se recomandă o schimbare persistentă din această probă. Detalii în `results.json`, `http-metadata.json`, `*-metrics.json`, `*-engine.log`, `*.jsonl`, `*-acceptance.txt` și `run_title.py`.
