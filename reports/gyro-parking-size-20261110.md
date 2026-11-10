# Parking Strata sub presiune RAM: mărimea prefixului

## Protocol

Probe sintetice Chat Completions strict secvențiale pe instanța existentă, fără restart, fără schimbarea configurației sau a pragurilor RAM. Pentru trei mărimi de istoric de tool, am comparat o continuare directă cu una precedată de o cerere auxiliară diferită de 26–27 tokeni. Două repetări per condiție, a doua în ordine inversă; markerii diferiți împiedică reutilizarea accidentală între brațe. Fiecare cerere verifică în prealabil că engine-ul este idle. Generarea sintetică este limitată la 16 tokeni, thinking oprit și temperatură 0, exclusiv pentru a măsura cache-ul, nu calitatea agentului.

| Tokeni în continuare | Fără intercalare: reutilizați, timp | Cu intercalare: reutilizați, timp |
|---:|---|---|
| 1055 | 1036 în ambele; 0,341 / 0,185 s | 0 în ambele; 1,113 / 1,068 s |
| 3936 | 3917 în ambele; 0,242 / 0,157 s | 0 în ambele; 1,999 / 1,977 s |
| 8736 | 8717 în ambele; 0,228 / 0,192 s | 0 în ambele; 4,225 / 4,362 s |

Toate cele 30 cereri au terminat HTTP 200 cu `finish_reason=stop` și câte o cerere contabilizată de engine. Timpul este wall al continuării, nu include cererea auxiliară. Cifrele de reutilizare sunt `usage.prompt_tokens_details.cached_tokens`; în date coincid cu `engine_last_reused`. Nu s-au salvat conținuturi ale prompturilor/răspunsurilor, doar structuri și contoare sintetice.

## Parking și interpretare

Engine-ul a raportat refuzuri `physical RAM admission` în toate cele 12 ferestre; în brațele cu intercalare, logul conține câte trei refuzuri pe fereastră, cu `0 still parked`. Exemple: la 8736 tokeni, refuzul a indicat `need 343 MiB plus 2560 MiB floor, 639 MiB available`, urmat de reutilizare zero. În continuările directe, reutilizarea rămâne mare chiar dacă logul conține un refuz de parking; păstrarea prefixului activ și parking-ul sunt mecanisme distincte.

La început Windows raporta 31,62 GiB RAM fizic și 0,51 GiB disponibil. Un eșantion psutil a atribuit procesului `strata.exe` 21.693 MiB working set și 28.725 MiB private bytes: acestea măsoară lucruri diferite și nu se adună. RAM-ul în `results.json` este aproximarea `ram_total - ram_used` din metricile Strata, distinctă de `psutil.virtual_memory().available`; refuzurile folosesc valoarea engine `meminfo`. Nu am închis aplicații, nu am modificat siguranța și nu am redus contextul.

Intercalarea este singurul factor intenționat diferit în cadrul fiecărei perechi, dar starea sistemului și markerii diferă. Rezultatele reproduc cache miss-ul chiar și la cel mai mic prefix testat și arată creșterea latenței continuării cu dimensiunea prefixului în acest experiment. Nu demonstrează prin ele însele că parking-ul refuzat este singura cauză, nici că un spor de RAM va corecta problema: n-am avut condiții comparabile cu suficient RAM liber pentru admission. Istoricul arată că testele de headroom prin restart nu au demonstrat un câștig (`gyro-ram-ab-20261110/REPORT.md`, `gyro-ram135-ab-20261110/REPORT.md`).

## Decizie

Nu a rezultat o intervenție nouă verificată, sigură și reversibilă pe sistemul utilizatorului. Evitarea unei cereri auxiliare intercalate îmbunătățește evident această probă sintetică, dar comparațiile reale anterioare cu titlu explicit sau hook nu au arătat o astfel de intercalare în timpul taskului și nu au demonstrat un speedup. Prin urmare nu pretindem o remediere și nu repetăm un benchmark de acceptanță pentru o schimbare inexistentă. Pentru o comparație cauzală sub pragurile intacte ar fi nevoie de RAM suplimentar disponibil sau de o posibilitate autorizată de a elibera memorie, cu menținerea aceluiași model și aceluiași runtime; nu am modificat procesele utilizatorului.

Dovezi: `probe_sizes.py`, `results.json`; probele folosesc codul comun `gyro-prefix-factor-20261110/probe.py`. Contoarele de I/O ale procesului și citirile fizice ale sistemului nu au fost măsurate în acest experiment și nu sunt deduse din cache.
