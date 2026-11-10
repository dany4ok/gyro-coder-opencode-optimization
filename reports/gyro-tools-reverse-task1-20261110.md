# Task 2: ordine inversă a uneltelor; Task 1 cu unelte restrânse

## Protocol

Repetarea inversă a perechii din `gyro-process-tools-ab-20261110`: OpenCode V2 standalone, Gyro-S, aceleași specificații și suite externe, prompt identic cu pauză artificială de 12 s, titlu explicit, warming OpenCode off, output 16384, aceeași cerere de încălzire separat. Rulări secvențiale, baze și workspaces izolate. Întâi Task 2 cu plugin local care păstrează 4 unelte, apoi Task 2 control cu 12, deadline 210 s fiecare; apoi Task 1 cu 4 unelte, deadline 240 s. Nu s-a rulat aici un control Task 1 contemporan. Pluginul și configurația sunt exclusiv în workspace-urile experimentale.

Suita Task 2 SHA-256 `94918e3c5f113f6ed3c896740aac007261c821c9aa281937fa0e9518c82fb205`; Task 1 SHA-256 `00bcddba2a3901ccac351e6edc9fefcfa6dd2b6a42060f19a00ec5d6217e95e6`. Hash-urile au fost reverificate. Captura HTTP locală redactată confirmă 4 unelte în 11/11 cereri Task 2 restrâns și 8/8 Task 1 restrâns, respectiv 12 în 10/10 control; toate HTTP 200.

## Rezultate verificate independent

| Rulare | Wall | Stare | Acceptanță externă | Teste proprii | Erori tool |
|---|---:|---|---:|---:|---|
| Task 2, 4 unelte | 185,125 s | finalizat, exit 0 | 17/17 | 30/30 | 0 raportate |
| Task 2, 12 unelte | 142,074 s | finalizat, exit 0 | 17/17 | 23/23 | un shell exit 1 la test propriu, apoi corectat |
| Task 1, 4 unelte | 240,105 s | TIMEOUT | 20/20 pe artefact parțial | 11/14 pe artefact parțial | un shell exit 1 la teste proprii |

Suitele externe și proprii au fost rerulate independent după execuții. La Task 1 agentul a fost întrerupt, astfel că rezultatul final și timpul complet sunt necunoscute; 20/20 extern nu face din timeout un succes. Suitele proprii sunt generate diferit și numărul lor nu este scor comparabil de calitate.

## Cache, I/O și latență

| Rulare | Prefill engine capturat | Decode capturat | Prompt inițial | Citiri contorizate procesului Strata | RAM sistem minim |
|---|---:|---:|---:|---:|---:|
| Task 2, 4 unelte | 12,488 s | 158,118 s | 4023 tokeni / 5,156 s | 507,7 MiB / 184,97 s | 99,3 MiB |
| Task 2, 12 unelte | 10,849 s | 116,367 s | 6109 tokeni / 4,014 s | 400,4 MiB / 140,77 s | 35,5 MiB |
| Task 1, 4 unelte | 25,112 s | 197,112 s | 4024 tokeni / 3,592 s | 931,8 MiB / 241,35 s | 74,1 MiB |

I/O este `psutil.Process.io_counters()` pentru același PID Strata 2020 și dată de creare în toate ferestrele: contabilizare pe proces, nu probă directă de citiri fizice SSD. Eșantionarea este la ~2 s și ferestrele nu sunt identice; nu comparați volumele ca trafic al aceleiași cantități de lucru. Timpii engine includ cereri auxiliare și pot omite cererea întreruptă; în Task 1 sunt 8 linii engine capturate, dar delta contorului este 7, posibil din limitele ferestrei/logului. Au fost 1/1/4 mesaje de refuz parking pentru rulările din tabel.

## Interpretare

În perechea inițială Task 2, 4 unelte au fost 155,495 s față de 175,240 s control. În repetarea inversă, au fost 185,125 s față de 142,074 s control. Toate patru au terminat și au avut 17/17 extern, însă variația se suprapune, iar numărul de pași/teste generate diferă. O singură pereche în fiecare ordine nu demonstrează un efect statistic sau absența regresiilor pe alte sarcini. Task 1 cu 4 unelte a expirat și a avut teste proprii eșuate la oprire, deci nu validează intervenția. Eliminarea `glob`, `grep`, `webfetch` și a altor unelte poate dăuna sarcinilor care le necesită. Nu s-a aplicat nicio restrângere globală.

Dovezi: `results.json`, `http-metadata.json` redactat, `*-metrics.json`, `*-engine.log`, `*-os-io-samples.json`, `*-acceptance.txt`, `*.jsonl`, `run_process.py`, `tool-filter.js` și workspaces. JSONL-urile de agent pot conține cod, spre deosebire de metadatele HTTP redactate.
