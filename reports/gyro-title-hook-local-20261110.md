# Hook local pentru titlu: comparație Task 2

## Protocol

Două rulări secvențiale Gyro-S/OpenCode V2 standalone, întâi titlu automat, apoi hook local `ctx.session.hook('title')` care setează `event.result` la un titlu fix. Niciuna nu folosește `--title`. Aceeași specificație Task 2, prompt cu pauză artificială de 12 secunde, încălzire separată, 12 unelte, output 16384, warming OpenCode oprit și deadline 210 s. Workspaces și baze izolate; pluginul există exclusiv în workspace-ul experimental. Proxy-ul captează metadate HTTP, nu conținutul cererilor sau antete.

Suita externă neschimbată are SHA-256 `94918e3c5f113f6ed3c896740aac007261c821c9aa281937fa0e9518c82fb205`.

| Profil | Wall | Stare | Extern rerulat | Teste proprii rerulate | Erori tool |
|---|---:|---|---:|---:|---|
| Automat | 139,231 s | finalizat, exit 0 | 17/17 | 21/21 | 0 raportate |
| Hook local | 156,658 s | finalizat, exit 0 | 17/17 | 18/18 | un shell exit 1 la teste proprii, ulterior trecute |

Eșecul inițial al testelor proprii în varianta hook include `PermissionError` pe un fișier temporar și o aserțiune de expirare; nu s-a stabilit că hook-ul l-a cauzat. Suitele proprii diferă și numărul lor nu este un scor comparabil.

## Cronologie și cache

- Control: 8 cereri chat, toate HTTP 200. Singura fără unelte a început la 0,898 s de la startul CLI, iar prima cu 12 unelte la 0,918 s. Logul engine arată mai întâi promptul scurt de 571 tokeni (0 reutilizați), apoi promptul principal de 6103 tokeni (0 reutilizați); următorul prompt principal a reutilizat 6259/7162 tokeni. Cererea fără unelte este compatibilă cu generarea titlului, dar metadatele nu îi dovedesc conținutul sau scopul.
- Hook: a fost invocat o dată, la aproximativ 0,987 s de la start; 10 cereri chat, toate cu 12 unelte și HTTP 200, prima la 1,009 s. Prima cerere a reutilizat 0/6103 tokeni, iar a doua 6177/6964. În această sesiune nu s-a observat cerere fără unelte.
- Controlul a procesat cererea scurtă înaintea primei cereri principale, nu între două cereri principale; experimentul nu demonstrează evitarea unui cache miss intercalat în timpul taskului. Refuzurile de parking apar în log, însă nu stabilesc singure cauza latenței.

## Concluzie și limite

Hook-ul local a furnizat titlul și a coincis cu absența cererii fără unelte, dar nu a demonstrat un câștig de performanță: varianta hook a durat cu 17,427 s mai mult, pe traseu diferit, o singură pereche și ordine fixă. Proba sintetică anterioară arată că intercalarea poate cauza cache miss în condițiile respective, nu că acest lucru s-a întâmplat sau a fost prevenit aici. Nu se recomandă activarea globală; un titlu fix compromite titlurile descriptive, iar alte cereri auxiliare nu sunt eliminate.

Dovezi: `results.json`, `http-metadata.json`, `*-engine.log`, `*-metrics.json`, `*-acceptance.txt`, `title-hook/title-hook.jsonl`, `title-plugin.js`, `run_title.py` și workspaces. Logurile de agent `*.jsonl` pot conține cod; metadatele HTTP sunt redactate.
