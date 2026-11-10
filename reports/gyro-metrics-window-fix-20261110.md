# Corecție locală a analizei metricilor cache Strata

## Cauză reproductibilă

În `Strata/control/serve/server.py`, `self.history` este un `deque(maxlen=500)`; `conversation_cache_view` setează `requests = len(hist)` și `requests_reused` la numărul de cereri cu reuse din fereastra respectivă. Aceste valori sunt indicatori ai unei **ferestre glisante**, nu contoare monotone de la pornire. Scripturile de benchmark anterioare au scăzut valorile lor între snapshoturi și au numit rezultatul `engine_request_delta`/`engine_reused_request_delta`, ceea ce este invalid când intră și ies elemente din fereastră.

În același server, `totals.requests`, `totals.reused` și `totals.prompt_tokens` sunt cumulative de la `totals.since`. `metrics_delta.py` calculează delte din aceste contoare numai când identitatea `since` este prezentă și identică, iar contoarele nu scad; altfel raportează necunoscut. Separat, numără linii engine capturate și linii cu reuse, fără a garanta acoperirea logului. Metricile cumulative pot include alte cereri din aceeași fereastră, deci atribuirea necesită absența traficului concurent. Nu se deduce numărul cumulativ de cereri cu reuse din `totals.reused` (acesta numără tokeni).

## Control: date reale arhivate, aceeași suită externă

Am analizat aceeași pereche secvențială deja executată în `gyro-state-guidance-20261110` (Task 2 scurt, ambele finalizate). Este comparația **calculului vechi față de cel corectat pe aceleași snapshoturi**, nu un nou A/B al inferenței:

| Rulare | Diferență veche: cereri / cereri cu reuse | Corectat: cereri cumulative | Linii engine capturate / cu reuse | Tokeni reutilizați cumulativ |
|---|---:|---:|---:|---:|
| Control | 0 / +2 | 5 | 5 / 4 | 48018 |
| Instrucțiune locală | 0 / −1 | 7 | 7 / 6 | 72398 |

În ambele, înainte și după au câte 500 intrări în fereastră, dar `totals.requests` crește de la 520 la 525, respectiv 526 la 533. În aceste două ferestre, numărul liniilor engine și suma tokenilor reutilizați din log coincid cu deltele cumulative; coincidența nu garantează asta pentru toate rulările. Datele de cronologie și HTTP sunt în dosarul original.

Suita externă Task 2 neschimbată a fost rerulată secvențial pe cele două artefacte: **17/17** și **17/17**. Ambele sesiuni originale au terminat, în 70,834 s și 63,462 s; timpii nu sunt afectați de această corecție a analizei și nu reprezintă dovadă de accelerare.

## Teste și limite

`python -m unittest -v test_metrics_delta`: **3/3** trecute, pentru rollover al ferestrei (inclusiv delta negativă), restart/scădere de contor și identitate `since` lipsă. Scriptul este local și reversibil; nu modifică Strata, bazele de date, configurația sau arhivele benchmark. Rezultatele istorice `engine_request_delta` bazate pe diferența ferestrei trebuie tratate cu rezervă; nu au fost rescrise automat. Celelalte măsurători de timp, acceptanță și log rămân independente.

Aceasta corectează o eroare de **telemetrie în harness**, nu o cauză dovedită a timeouturilor sau a erorilor Gyro-S și nu este o optimizare de performanță. Dovezi: `metrics_delta.py`, `test_metrics_delta.py`, snapshoturile și logurile din `gyro-state-guidance-20261110`.
