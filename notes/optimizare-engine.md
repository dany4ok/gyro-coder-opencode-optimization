# Optimizare engine — notă de continuare

## Obiectiv

Investighează și îmbunătățește utilizarea Gyro-S în OpenCode/Strata pe Windows, cu accent pe erori recuperabile, latență și consistență. Baza este `benchmark/benchmark_gyro_luna_30min.md`; folosește specificațiile și suitele externe fixe din `benchmark/`. Utilizatorul dorește teste mai scurte când sunt reprezentative.

## Ce este deja făcut

- Output Gyro-S 16384 și context 131072; instrucțiuni Windows și edit pentru Gyro-S; warming OpenCode oprit doar pe acel model.
- Corecție locală Strata pentru `completion_tokens_details.reasoning_tokens`; patch și test în `fixes/`. Poate fi suprascrisă la update.
- Protecția implicită `answer_room` activă poate limita thinking-ul la 12288 la output 16384, chiar fără buget explicit. Păstrează protecția până la dovezi de siguranță și calitate.
- Un cache miss după intercalare a fost reprodus sintetic la RAM liber mic, dar intervențiile testate pe titlu nu au dovedit un câștig cauzal în sesiuni reale.
- Experimentul Task 1 incremental: control 245,529 s și incremental 287,155 s, ambele 20/20 extern, 11/11 și 13/13 propriu; n=1 și trasee diferite.
- Ultimul audit shell: comanda cu `unterminated-quote` era invalidă PowerShell: backtick-ul escapează ghilimeaua finală. Parserul a respins originalul și acceptat corecția minimă; corecția a rulat în sandbox cu exit-uri interne 0, 1 și 2, conform scenariilor. Scannerul nu a fost slăbit.

## Constrângeri

1. Nu reduce pragurile RAM/VRAM sau nu opri procesele utilizatorului fără acord. Nu dezactiva `answer_room` pe baza timpului singur.
2. Rulările Gyro-S sunt secvențiale. Verifică starea idle, folosește sesiuni/workspaces și baze OpenCode izolate și nu atinge baza comună.
3. Nu modifica suitele externe între variante. Marchează separat timeouturile, rezultatele parțiale, testele proprii și exit-urile. Nu calcula speedup din timpuri cenzurate.
4. Separă cache-ul Strata, I/O atribuit procesului și citirile fizice ale sistemului. Nu folosi diferențe ale ferestrei de 500 ca delte cumulative.
5. Nu publica loguri brute, baze, chei sau configurații cu credențiale. Raportul original are concluzii istorice nefiabile; vezi README.

## Pasul următor

Mai întâi verifică runtime-ul și configurația efectivă după eventuale update-uri. Alege o ipoteză nouă și o intervenție locală, reversibilă, care păstrează calitatea și protecțiile; nu repeta variantele deja neconcludente din `reports/`. Rulează control și intervenție secvențial, cu limită de timp clară, aceleași suite externe, apoi repetă în ordine inversă dacă primul rezultat justifică asta. O comparație cu suficient RAM liber ar putea ajuta la izolarea parking-ului, dar poate necesita acordul utilizatorului pentru eliberarea memoriei sau hardware suplimentar. Nu promite o accelerare înainte de dovezi.
