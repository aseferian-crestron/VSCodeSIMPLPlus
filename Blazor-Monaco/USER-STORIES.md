# SIMPL+ Editor — User Stories & Acceptance Criteria

These stories describe the **observed behavior of the SIMPL+ VS Code POC** (`../`, this
plugin repo) and serve as the requirements for replicating that behavior in **Crestron
Construct** (Blazor + Monaco). Each acceptance criterion reflects how the plugin *actually*
works today, verified against the source.

Conventions: stories use the *As a / I want / so that* form; acceptance criteria are
testable Given/When/Then statements. "Editor" = the SIMPL+ editing surface (VS Code today,
Monaco-in-Construct as the target).

---

## Epic 1 — Syntax Highlighting

### US-1.1 — Highlight SIMPL+ language elements
**As a** SIMPL+ programmer
**I want** my code colorized by token type
**so that** I can read structure at a glance and spot typos in keywords.

**Acceptance Criteria**
- Given a `.usp` or `.ush` file, when it opens, then it is recognized as the SIMPL+ language.
- Preprocessor directives (`#SYMBOL_NAME`, `#DEFINE_CONSTANT`, `#ENABLE_STACK_CHECKING`, `#IF_DEFINED`/`#ENDIF`, `#HELP_BEGIN`/`#HELP_END`, etc.) are highlighted as preprocessor tokens; an unknown `#XXX` directive still highlights generically.
- I/O declaration keywords are highlighted: `DIGITAL_INPUT`, `ANALOG_INPUT`, `STRING_INPUT`, `BUFFER_INPUT`, `DIGITAL_OUTPUT`, `ANALOG_OUTPUT`, `STRING_OUTPUT`.
- Data types are highlighted: `INTEGER`, `STRING`, `LONG_INTEGER`, `SIGNED_INTEGER`, `SIGNED_LONG_INTEGER`, `REAL`, `STRUCTURE`, and array variants.
- Function/handler keywords are highlighted: `FUNCTION`, `INTEGER_FUNCTION`, `STRING_FUNCTION`, `LONG_INTEGER_FUNCTION`, `SIGNED_INTEGER_FUNCTION`, `SIGNED_LONG_INTEGER_FUNCTION`, `CALLBACK`, `PUSH`, `RELEASE`, `CHANGE`, `EVENT`, `THREADSAFE`, `EVENTHANDLER`.
- Control-flow keywords (`IF`/`ELSE`, `FOR`, `WHILE`, `DO`/`UNTIL`, `SWITCH`/`CASE`, `RETURN`, `BREAK`, `TO`, `STEP`) and word operators (`AND`, `OR`, `NOT`, `MOD`, `BAND`, …) are highlighted.
- Built-in functions (e.g. `Print`, `MakeString`, `Left`, `Find`, `GetLastModifiedArrayIndex`) and language constants (`TRUE`, `FALSE`, `ON`, `OFF`) are highlighted.
- Line comments (`//…`), block comments (`/* … */`), double-quoted strings with escape sequences, and numeric literals (hex `0x…`, float, integer) are highlighted.
- All keyword matching is **case-insensitive** (`Function`, `function`, `FUNCTION` all highlight).

---

## Epic 2 — Code Snippets

### US-2.1 — Insert common SIMPL+ patterns via snippets
**As a** SIMPL+ programmer
**I want** prefix-triggered snippets with tab stops
**so that** I can scaffold boilerplate quickly and consistently.

**Acceptance Criteria**
- Given I type a snippet prefix and trigger completion, when I accept it, then the snippet body is inserted with editable tab stops.
- At least the following prefixes exist: module header, `DIGITAL_INPUT`/`ANALOG_INPUT`/`STRING_INPUT`/`BUFFER_INPUT`, `DIGITAL_OUTPUT`/`ANALOG_OUTPUT`/`STRING_OUTPUT`, `PUSH`, `CHANGE`, `FUNCTION`, `FOR`, `WHILE`, `WAIT`, `#DEFINE_CONSTANT`, `STRUCTURE` (≈31 snippets total).
- Tab stops let me cycle through placeholder fields after insertion.

---

## Epic 3 — Hover Documentation

### US-3.1 — See documentation when hovering a built-in function
**As a** SIMPL+ programmer
**I want** to hover over a built-in function and see its docs
**so that** I don't have to leave the editor to consult the language reference.

**Acceptance Criteria**
- Given the cursor hovers over a known built-in function name, when the hover appears, then it shows the function name, category, description, syntax, return value, and an example (whichever fields are present).
- Hover content is sourced from the bundled function database (~305 functions across 28 categories).
- Hover lookup is case-insensitive.
- Given the hovered word is not a known function, when I hover, then no SIMPL+ hover is shown.

### US-3.2 — See the signature when hovering a function I declared
**As a** SIMPL+ programmer
**I want** to hover over one of my own functions and see its signature
**so that** I can recall its return type and parameters without scrolling to the definition.

**Acceptance Criteria**
- Given the cursor hovers over a user-declared function name, when no built-in match exists, then the hover shows the function's reconstructed signature (return type + name + parameter list), e.g. `INTEGER_FUNCTION GetSource(INTEGER iInput)`.
- Built-in database functions take precedence over user functions of the same name.
- Functions whose parameter list wraps across multiple lines are not parsed (single-line declarations only).

---

## Epic 4 — Auto-Completion (IntelliSense)

### US-4.1 — Complete built-in functions and keywords
**As a** SIMPL+ programmer
**I want** completion suggestions for built-in functions
**so that** I can discover and insert them with correct names.

**Acceptance Criteria**
- Given I trigger completion, when the list appears, then it includes the built-in functions/keywords from the function database, each with its category as detail and full documentation.
- Given a chosen function whose documented syntax shows a call with parentheses, when I accept it, then it inserts `Name($0)` with the cursor positioned inside the parentheses.

### US-4.2 — Complete symbols I declared in the current file
**As a** SIMPL+ programmer
**I want** my own variables, I/O, parameters, constants, functions, and structures to appear in completion
**so that** I can reference them without retyping or misspelling.

**Acceptance Criteria**
- Given I have declared symbols in the open file, when I trigger completion, then those symbols appear alongside the built-ins.
- Each user symbol shows a kind appropriate to its declaration (variable, field/IO, property/parameter, function, struct, constant).
- Duplicate names (e.g. comma-separated declarations) appear only once.
- Symbol detection is case-insensitive with respect to the declaring keyword (e.g. `integer gVol;` is detected the same as `INTEGER gVol;`).

---

## Epic 5 — Signature Help

### US-5.1 — See parameter hints while calling a function
**As a** SIMPL+ programmer
**I want** parameter hints as I type a function call
**so that** I know which argument I'm on and what it expects.

**Acceptance Criteria**
- Given I type `(` after a known function name, when signature help opens, then it shows the function's signature(s) and description.
- Given a function documented with multiple syntax lines, when signature help opens, then each line is presented as a separate overload.
- Given I type commas within the argument list, when I advance, then the active-parameter highlight moves to the corresponding parameter (accounting for nested parentheses).

### US-5.2 — Parameter hints for functions I declared
**As a** SIMPL+ programmer
**I want** signature help for my own functions
**so that** I get the same call-time guidance as for built-ins.

**Acceptance Criteria**
- Given I type `(` after a user-declared function name with no built-in match, when signature help opens, then it shows that function's reconstructed signature with each parameter as a separate hint.
- Given I type commas, when I advance, then the active-parameter highlight tracks my position.
- Built-in database functions take precedence over user functions of the same name.

---

## Epic 6 — Go to Definition

### US-6.1 — Jump to where a symbol is declared
**As a** SIMPL+ programmer
**I want** to jump from a symbol usage to its declaration
**so that** I can navigate large modules quickly.

**Acceptance Criteria**
- Given the cursor is on a user-declared symbol, when I invoke Go to Definition, then the editor navigates to the identifier at its declaration site.
- Lookup is case-insensitive.
- Given the symbol has multiple matching declarations, when I invoke Go to Definition, then all candidate locations are offered.
- Given the word is not a user-declared symbol, when I invoke Go to Definition, then nothing is navigated.

---

## Epic 7 — Go to Symbol / Outline

### US-7.1 — List all symbols in the current file
**As a** SIMPL+ programmer
**I want** a symbol list / outline for the open file
**so that** I can see its structure and jump to any declaration.

**Acceptance Criteria**
- Given an open SIMPL+ file, when I invoke Go to Symbol (`@` / Ctrl+Shift+O), then it lists the file's declared functions, I/O, variables, parameters, constants, and structures with their kinds.
- Selecting an entry navigates to that declaration.
- The same symbols populate the Outline view and breadcrumbs.
- Declarations inside comments or string literals are **not** listed.

### US-7.2 — List event handlers in the outline
**As a** SIMPL+ programmer
**I want** my event handlers to appear in the symbol list
**so that** I can jump straight to the `PUSH`/`RELEASE`/`CHANGE` block for a given signal.

**Acceptance Criteria**
- Given the file contains event handlers, when I open Go to Symbol / Outline, then each `PUSH`, `RELEASE`, and `CHANGE` handler is listed, keyed by its signal name with the event type shown as detail and an "event" kind.
- `THREADSAFE`-prefixed handlers (e.g. `THREADSAFE CHANGE x`) are listed the same way.
- Selecting an entry navigates to the handler's signal.
- Handler keywords appearing inside comments are **not** listed.

---

## Epic 8 — Compiler Integration

### US-8.1 — Compile the current file from the editor
**As a** SIMPL+ programmer
**I want** to compile the active `.usp` without leaving the editor
**so that** I get fast feedback on errors.

**Acceptance Criteria**
- Given an active `.usp`, when I run "Compile Current File" (command, context menu, or keybinding), then the file is saved and passed to the Crestron command-line compiler (`SPlusCC.exe`) for the configured target series.
- Compiler output is streamed to a dedicated output channel in real time.
- On success, a success notification is shown; on failure, an error notification offers to open the Problems view.

### US-8.2 — Compile all files in the workspace
**As a** SIMPL+ programmer
**I want** to compile every `.usp` in the workspace at once
**so that** I can validate a whole project.

**Acceptance Criteria**
- Given a workspace with `.usp` files, when I run "Compile All", then all are compiled (batched to avoid command-line limits) and a combined result summary is shown.
- Given no `.usp` files exist, when I run "Compile All", then an informational message says none were found.

### US-8.3 — See compiler errors inline and in a problem list
**As a** SIMPL+ programmer
**I want** errors and warnings surfaced in the editor
**so that** I can find and fix them by clicking.

**Acceptance Criteria**
- Given the compiler reports `[file] Error N (Line X) - message`, when compilation finishes, then a diagnostic is created on the reported line with the message and severity (Error/Warning).
- Diagnostics appear as inline squiggles and in the Problems list, each linking to the file + line.
- Diagnostics are cleared at the start of each compile run.
- (Known caveat) Reported line numbers may be relative to the function body rather than the absolute file line.

---

## Epic 9 — Compiler Discovery & Configuration

### US-9.1 — Auto-detect the compiler regardless of install location
**As a** SIMPL+ programmer
**I want** the editor to find `SPlusCC.exe` automatically
**so that** I don't have to configure paths manually.

**Acceptance Criteria**
- Given `compilerPath` is blank, when I compile, then the editor resolves the compiler from common install directories and the Windows registry (SIMPL Windows install location).
- Given `compilerPath` is set, when I compile, then that path takes precedence.
- Given the compiler cannot be found, when I compile, then the editor prompts me to locate `SPlusCC.exe` and remembers my selection.

### US-9.2 — Configure target series
**As a** SIMPL+ programmer
**I want** to choose the control-system target
**so that** compilation matches my hardware.

**Acceptance Criteria**
- Given the `compileTarget` setting, when I compile, then the chosen target (`series2`, `series3`, or `series2 series3`) is passed to the compiler; default is `series3`.

---

## Epic 10 — Extension Activation & Status

### US-10.1 — Know the SIMPL+ tooling is active
**As a** SIMPL+ programmer
**I want** a clear indication the language tooling is loaded
**so that** I can trust that highlighting/IntelliSense/compile are available.

**Acceptance Criteria**
- Given a SIMPL+ file is opened, when the extension activates, then a status-bar badge ("✓ SIMPL+") is shown and a one-time activation notification appears.
- Clicking the badge opens the SIMPL+ log/output.
- Given another tool also claims `.usp`, when there is a conflict, then the user can determine which language owns the file (the log reports the active language ID on symbol scans).

---

## Known gaps / not-yet-implemented (track separately, do not write passing AC)

These are **not** working behaviors today; capture them as backlog items, not acceptance criteria:

- **Compile-on-save** — `compileOnSave` setting exists in configuration but is **not wired** to any save handler. No automatic compile occurs on save.
- **Wrapped multi-line declarations** — I/O/variable declarations whose terminating `;` is on a later line than the type keyword are **not** captured by completion / outline / go-to-definition. Function declarations whose *parameter list* wraps across lines are likewise not parsed for hover/signature help.
- **`F12` keybinding conflict** — `F12` is bound to "Compile Current File" for SIMPL+ files, which shadows the standard `F12` "Go to Definition" gesture; Go to Definition must be reached another way (context menu / Ctrl+click). Worth resolving when replicating in Construct.

---

## Source of truth

Behavior verified against the POC at `../` (repo `aseferian-crestron/VSCodeSIMPLPlus`):
`src/providers.ts` (hover/completion/signature/definition/outline), `src/symbols.ts`
(symbol scanner), `src/extension.ts` + `src/compilerPath.ts` (compile + discovery),
`syntaxes/simplplus.tmLanguage.json` (highlighting), `snippets/simplplus.json`,
`scripts/function-db.json`, and `package.json` (commands, keybindings, settings).
