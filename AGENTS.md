# Global instructions

## Language and tone

Apply these in every session, for any model. They are suggestions, not hard
rules: follow them unless they conflict with an explicit user request.

- Reply in the language the user writes to you in. Match the language of their
  latest message; do not default to one fixed language.
- Talk plainly, like a person, not like a tool. Short prose answers by default.
- Do not show code, commands, diffs, file dumps, or tool chatter unless the user
  asks for it or the task genuinely requires it. When code is needed, keep it
  minimal and explain it in one or two sentences in the user's language.
- Skip headings, bullet lists and long explanations for simple questions; answer
  the question that was asked.

## Gyro Gyro S via Strata

Apply these when the session model is `strata/gyro-gyro-s`. They are suggestions,
not hard rules: follow them unless they conflict with an explicit user request.

### Prompt cache reuse is the main performance priority
- Keep the conversation and the current task stable; do not jump to unrelated
  topics or new conversations mid-task.
- Complete related operations in one continuous work batch.
- Stay on the current task until it is finished or genuinely blocked.
- Reuse context you already have instead of re-reading the same files.

### Batch work by task
- Group file reading, analysis, editing and verification per task, in one batch.
- Prefer sequential execution over several independent Gyro-S requests.
- Do not launch Gyro-S subagents with independent contexts for work the current
  session can do; if a subagent is truly needed, pass it the full context.
- Optimize total task completion time, not only token generation time.

## Windows test commands and edits (Strata models)

Apply these when the session model is `strata/gyro-gyro-s` or
`strata/coder-iq1_m`. They are suggestions, not hard rules: follow them unless
they conflict with an explicit user request.

- The Windows shell is PowerShell: `ls` is a `Get-ChildItem` alias, so Unix
  flags such as `ls -la` fail. Use `Get-ChildItem -Force` to list hidden files.
- In PowerShell, Python's `unittest` writes normal progress and `OK` to stderr.
  Do not interpret stderr or `NativeCommandError` alone as a failed test. Avoid
  piping `2>&1` through PowerShell: it can turn successful tests into exit code 1.
  Run, for example, `cmd /c "python -m unittest test_module -v 2>&1"; exit $LASTEXITCODE`
  so the shell tool receives the real result. Preserve and inspect actual
  failures before changing tests.
- Before an edit, verify that the old and new text differ and that the target
  exists. For the `edit` tool, include all required fields: `path`, `oldString`,
  and `newString` in every call, even when editing the same file repeatedly.
  Do not issue no-op edit calls.

## ComfyUI local — fără browser popup

- Nu deschide niciodată `http://127.0.0.1:8188/` într-un browser (Firefox/Edge),
  nu folosi unealta `browser` pe interfața ComfyUI și nu rula `start http://...`
  sau `webbrowser.open`. Generarea de imagini se face exclusiv prin API-ul
  ComfyUI (`/system_stats`, `POST /prompt`, `/history`).
- Pornește ComfyUI doar prin
  `C:\Users\x1p\Documents\OpenCode\create game ideea\_tools\comfy\start_comfy.ps1`,
  care include `--disable-auto-launch` și un auto-shutdown la 3 minute idle.
  Nu elimina flagul și nu adăuga `--auto-launch` / `--enable-agent`.

## Reviewer independent — automat, în toate workspace-urile

Agentul `reviewer` e definit global în `~/.config/opencode/opencode.json`, deci există în orice workspace. **Nu e nevoie ca utilizatorul să îl ceară explicit** — declanșează-l singur.

Pentru orice sarcină care modifică fișiere (cod, config, documentație), după implementare și self-verificare:

1. Păstrează cerința originală a utilizatorului verbatim și lista fișierelor modificate.
2. Dispatch automat un `subagent` proaspăt cu `agent: "reviewer"`, cu cerința originală și dovezile reale din fișiere. Cere două etape: conformitate cu specificația și calitate tehnică. Reviewerul nu editează fișiere și nu pornește alți subagenți.
3. Dacă raportează probleme confirmate, repară-le, re-verifică și trimite un reviewer proaspăt pe versiunea corectată. Repetă până nu mai rămân probleme confirmate.
4. Raportează statusul la final: `✓ Verified` doar când reviewerul a revenit complet, valid, fără probleme confirmate; altfel `◐ Local AI Unavailable` / `◐ Partially Verified` / `✗ Verification Failed`, cu motiv scurt.

Dacă endpointul sau modelul reviewerului nu e disponibil, raportează `◐ Local AI Unavailable` și continuă. Nu îl înlocui cu alt model și nu pretinde `✓ Verified` fără un review real.

## Review pentru sarcini vizuale (imagini, sprite-uri, atlase)

Când rezultatul muncii e o imagine, regula de mai sus se completează:

1. **Criterii explicite înainte de review.** Scrie ce anume trebuie să fie adevărat, nu „să arate bine". Exemplu: „cadrul de death e complet căzut, nu în picioare"; „toate cadrele arată același caracter, la fel de înalt". Fără criterii concrete, reviewerul nu are ce bifa greșit.
2. **Pixelul, nu codul.** Reviewerul trebuie să deschidă imaginea cu `read`. Dacă modelul nu poate vedea imaginea, răspunsul e `CANNOT VERIFY VISUALS` + `◐ Partially Verified`. Un prompt, un nume de fișier sau o descriere din cod NU sunt dovadă vizuală. Nu numi un defect „design intenționat" doar pentru că așa scrie în cod.
3. **Cadru cu cadru, la mărime mare.** Nu trimite doar contact sheet-ul mic. Deschide fiecare celulă (sau cropUri) separat, ca diferențele de proporție și de stil să se vadă.
4. **Măsurare deterministă, înainte de verdict.** Rulează `python C:\Users\x1p\.config\opencode\tools\check_atlas_frames.py <imagine> --cols N --rows M`. Dacă programul raportează cadre goale, diferență de înălțime peste prag sau paletă diferită, asta e **problemă confirmată**, nu „diferență cosmetică". Testele JS/build trecute nu validează aspectul.
5. **Verdictul final trebuie să conțină** lista criteriilor vizuale bifate și rezultatul măsurătorii. Fără ele, nu pui `✓ Verified`.

Singura excepție: întrebările pur conversaționale, fără nicio modificare de fișier, nu declanșează review. Orice sarcină cu modificări de fișiere îl declanșează automat.
