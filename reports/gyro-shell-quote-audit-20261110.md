# Audit scanner shell: ghilimea PowerShell neînchisă

În controlul Task 1 incremental, `shell` a refuzat o comandă cu `Portable shell scanner cannot analyze command: unterminated-quote`. Comanda conținea un backtick imediat înainte de ghilimeaua care trebuia să închidă un șir PowerShell. Parserul nativ PowerShell 5.1 (`Parser.ParseInput`, fără execuție) a raportat `TerminatorExpectedAtEndOfString` pentru original și zero erori după eliminarea acelui backtick.

Corecția a fost rulată într-un sandbox cu o copie a implementării Task 1; cele trei scenarii au afișat exit intern 0 pentru input procesat, 1 pentru extensie nesuportată și 2 pentru argument lipsă. Raportul JSON conținea 3 înregistrări, 1 validă, 1 invalidă și un duplicat, conform datelor introduse. Exit-ul procesului PowerShell exterior era 0 și nu înlocuiește verificarea fiecărui cod intern.

Într-un diagnostic separat al executorului shell nativ, o comandă simplă validă și una validă cu ghilimea escape-uită au ieșit 0; un caz minimal invalid a fost respins. Apelarea executorului dintr-un tool diagnostic nu dovedește că acea cale a exercitat exact același scanner ca apelul original. Nu s-a stabilit un fals pozitiv al scannerului și nu s-au slăbit permisiuni sau verificări. Testele nu demonstrează că Gyro-S nu va mai genera comenzi invalide.
