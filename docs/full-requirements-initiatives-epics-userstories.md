# SIMPL+ for VS Code — Full As-Built Requirements

**Document type:** As-built requirements (Initiative → Epics → User Stories)
**Source standard:** Crestron Product Owner agent — Initiative / Epic / User Story format, mandatory Gherkin acceptance criteria
**Snapshot:** `main` @ `e4abaa7`, extension version `0.1.0`
**Last updated:** 2026-06-08
**Authors:** Product Owner (as-built capture)

---

## How to read this document

This document is the formal Initiative → Epic → User Story tree for the **SIMPL+ for Visual Studio Code** extension as it ships today. It is intended for product, engineering, QE, and partner-enablement readers who need to understand what the extension does, why each capability exists, and how to verify it.

- Stories are written as **vertical slices** delivering user-visible value to a SIMPL+ programmer.
- Acceptance criteria are **mandatory Gherkin** and reference concrete keystrokes, files, and observable behavior.
- This is a **retrospective** document — "Current State" describes the shipping behavior at the snapshot above, and the stories serve as a regression / acceptance contract.
- Behavior is verified against the source: `src/providers.ts`, `src/symbols.ts`, `src/functionDb.ts`, `src/extension.ts`, `src/compilerPath.ts`, `syntaxes/simplplus.tmLanguage.json`, `snippets/simplplus.json`, `language-configuration.json`, `scripts/function-db.json`, and `package.json`.

### Identifier scheme

| Prefix           | Meaning                       |
| ---------------- | ----------------------------- |
| `INI-SIMPLP-NNN` | Initiative                    |
| `EP-SIMPLP-NNN`  | Epic                          |
| `US-SIMPLP-NNN`  | User Story (as-built)         |

---

## Assumptions (please confirm or correct)

1. **As-built scope** is `main` @ `e4abaa7`, extension version `0.1.0`. Features that are configured but not implemented (the `simplplus.compileOnSave` setting) are captured as explicitly out of scope on the relevant story.
2. **Single initiative.** The extension is captured as one SIMPL+ tooling initiative; security/distribution concerns are minimal (no network surface beyond invoking the local compiler) and are not split into their own initiative.
3. **Runtime host.** The extension targets VS Code 1.75+. During development it runs in the Extension Development Host (F5); in production it is installed as a VSIX. Where another installed extension also claims `.usp`, language ownership conflicts are addressed in EP-SIMPLP-005.
4. **Compiler dependency.** Compilation requires Crestron SIMPL Windows (which provides `SPlusCC.exe`) installed on Windows. The function database (`scripts/function-db.json`, 305 functions across 28 categories) is bundled and parsed from the Crestron CHM language reference.
5. **Audience naming.** The primary audience is **SIMPL+ programmers** (Crestron integrators and module authors writing `.usp`/`.ush` files). A secondary audience is **extension maintainers** porting this behavior to other hosts (e.g. Crestron Construct via Monaco).
6. **As-built refinement.** Every shipped capability is refined so this document can serve as the acceptance contract for the current release and as the requirements source for the Blazor + Monaco port (`Blazor-Monaco/`).

---

## Crestron value alignment (quick map)

| Epic                                                | Simple to Deploy & Easy to Use | Flexible to Grow & Upgrade | Reliable & Secure by Design | Informed by Partnerships |
| --------------------------------------------------- | :----------------------------: | :------------------------: | :-------------------------: | :----------------------: |
| EP-SIMPLP-001 Syntax highlighting & editing aids    |               ✅               |             ✅             |              —              |            ✅            |
| EP-SIMPLP-002 Language intelligence                 |               ✅               |             ✅             |              —              |            ✅            |
| EP-SIMPLP-003 Code navigation & document symbols    |               ✅               |             ✅             |              —              |            ✅            |
| EP-SIMPLP-004 Compiler integration & diagnostics    |               ✅               |             ✅             |             ✅              |            ✅            |
| EP-SIMPLP-005 Activation, status & host isolation   |               ✅               |             —              |             ✅              |            ✅            |

---

# INI-SIMPLP-001 — SIMPL+ for VS Code: language support and compiler integration for Crestron SIMPL+

```
Title: SIMPL+ for VS Code — language support and compiler integration for Crestron SIMPL+

Audience:
- SIMPL+ programmers authoring `.usp`/`.ush` modules (primary)
- Crestron integrators maintaining existing SIMPL+ modules (primary)
- Extension maintainers porting this behavior into Crestron Construct via Monaco (secondary)

Functionality Enabled:
- Syntax highlighting for the full SIMPL+ language (preprocessor, I/O, data types, function/event keywords, control flow, built-ins, comments, strings, numbers, operators)
- 30+ code snippets for common SIMPL+ patterns
- Language intelligence backed by a 305-function database: hover docs, auto-completion, and signature help — for built-in functions and for the user's own declared symbols/functions
- Code navigation: go-to-definition and a Go to Symbol / Outline view covering functions, I/O, variables, parameters, constants, structures, and event handlers
- One-click compilation via the Crestron command-line compiler with inline error diagnostics, a Problems list, and a live output channel
- Compiler auto-detection (settings → common install dirs → Windows registry) so it works regardless of where SIMPL Windows was installed
- A clear activation indicator and a development workflow that isolates the extension from other tools that claim `.usp`

Rationale:
SIMPL+ has no official VS Code extension. Programmers authoring Crestron control logic in `.usp`/`.ush` files have historically worked without syntax highlighting, IntelliSense, or in-editor compilation, relying on the legacy SIMPL+ editor. This initiative brings a modern editing experience — highlighting, snippets, hover/completion/signature help, navigation, and compile-with-diagnostics — into VS Code, where most integrators already work. It directly supports Crestron's values: it is simple to use (works on any `.usp` the moment it opens; compiler auto-detected), flexible to grow (the function database and symbol scanner extend to new language features; the same behavior is being ported to Construct via Monaco), and informed by partnerships (the backlog is driven by integrator feedback). The work also produces the requirements baseline for the Blazor + Monaco port documented under `Blazor-Monaco/`.

Confluence: N/A — see in-repo `README.md` and `Blazor-Monaco/USER-STORIES.md`

Success Indicators:
- A `.usp`/`.ush` file opens with correct highlighting and an active language indicator with zero configuration
- A SIMPL+ programmer can compile a module and jump to the first error from the Problems list without leaving the editor
- The compiler is resolved automatically on a standard SIMPL Windows install with no manual path entry
- Go to Symbol lists every declaration in a real production module (functions, I/O, variables, constants, structures, event handlers)
- The extension's language features are reused (not rewritten) when ported to Crestron Construct via Monaco
```

---

# Epics

| Epic ID       | Title                                            | Stories        |
| ------------- | ------------------------------------------------ | -------------- |
| EP-SIMPLP-001 | Syntax highlighting & editing aids               | 3              |
| EP-SIMPLP-002 | Language intelligence (hover, completion, sig)   | 4              |
| EP-SIMPLP-003 | Code navigation & document symbols               | 3              |
| EP-SIMPLP-004 | Compiler integration & diagnostics               | 5              |
| EP-SIMPLP-005 | Activation, status & host isolation              | 2              |
| **Total**     |                                                  | **17 stories** |

---

## EP-SIMPLP-001 — Syntax highlighting & editing aids

```
Title: Syntax highlighting & editing aids

Parent Initiative: INI-SIMPLP-001 — SIMPL+ for VS Code: language support and compiler integration for Crestron SIMPL+

Audience:
- SIMPL+ programmers reading and writing `.usp`/`.ush` files
- Integrators reviewing an unfamiliar module

Functionality Enabled:
- A TextMate grammar that colorizes the full SIMPL+ language
- 30+ tab-stop snippets for declarations, handlers, functions, and control flow
- Bracket matching, auto-closing pairs, and comment toggling tuned for SIMPL+

In Scope:
- Highlighting: preprocessor directives, I/O declaration keywords, data types, function/event keywords (including typed `*_FUNCTION` variants and `CALLBACK`), control flow, word operators, built-in functions, language constants, line/block comments, strings with escapes, numbers (hex/float/int), operators
- Case-insensitive keyword matching (SIMPL+ is case-insensitive)
- Snippets covering module header, I/O declarations, `PUSH`/`CHANGE` handlers, `FUNCTION`, loops, `WAIT`, `#DEFINE_CONSTANT`, `STRUCTURE`
- Language configuration: brackets, auto-closing pairs, and `//` / `/* */` comment toggling

Out of Scope:
- Semantic (token-server) highlighting — grammar-based only
- Auto-formatting / pretty-printing of SIMPL+ code (not implemented)

Dependencies:
- `syntaxes/simplplus.tmLanguage.json` (TextMate grammar)
- `snippets/simplplus.json` (snippets)
- `language-configuration.json` (brackets, comments, auto-close)
- `package.json` (language contribution for `.usp`/`.ush` → `simplplus`)

Confluence: N/A — see `README.md` § "Features"

Related QE stories: N/A (no separate QE doc)
```

### US-SIMPLP-001 — Able to read SIMPL+ code with full syntax highlighting

```
Summary: Able to read SIMPL+ code with full syntax highlighting, including typed function keywords

Description:
As a SIMPL+ programmer, I want my `.usp`/`.ush` code colorized by token type,
so that I can read a module's structure at a glance and immediately spot a
mistyped keyword.

Current State:
Opening a `.usp` or `.ush` file activates the `simplplus` language (contributed
in `package.json`) and applies the TextMate grammar in
`syntaxes/simplplus.tmLanguage.json`. The grammar colorizes preprocessor
directives, I/O types, data types, function/event keywords, control flow, word
operators, built-in functions, constants, comments, strings, numbers, and
operators. The `function-types` rule matches `FUNCTION` plus the typed variants
`INTEGER_FUNCTION`, `STRING_FUNCTION`, `LONG_INTEGER_FUNCTION`,
`SIGNED_INTEGER_FUNCTION`, `SIGNED_LONG_INTEGER_FUNCTION`, and `CALLBACK`. All
keyword matching is case-insensitive.

Designs:
Reference grammar: `syntaxes/simplplus.tmLanguage.json`. Sample module:
`sample/sample.usp`.

Technical Notes:
- Typed function keywords are ordered longest-first in the grammar alternation so
  a specific variant (e.g. `INTEGER_FUNCTION`) wins over bare `FUNCTION`.
- Word boundaries matter: bare `FUNCTION` does not match inside `INTEGER_FUNCTION`,
  which is why the typed variants are enumerated explicitly.

Scope Clarification:
In Scope:
- Highlighting of all SIMPL+ token classes listed in the epic
- Case-insensitive keywords
Out of Scope:
- Semantic highlighting via a language server (grammar-based only)

Acceptance Criteria:

Scenario: A .usp file is recognized as SIMPL+ on open
  Given a file named `module.usp`
  When the user opens it in VS Code
  Then the editor language mode is "SIMPL+"
    And the file's content is colorized by the SIMPL+ grammar

Scenario: Typed function declaration keywords are highlighted as function keywords
  Given a file containing `Integer_Function GetValue(integer x)` and `String_Function Name()`
  When the file is open as SIMPL+
  Then `Integer_Function` and `String_Function` are colored as function keywords
    And bare `FUNCTION` declarations are colored the same way

Scenario: Keyword highlighting is case-insensitive
  Given a file containing `integer gVol;`, `INTEGER gCount;`, and `Integer gIdx;`
  When the file is open as SIMPL+
  Then the `integer`, `INTEGER`, and `Integer` keywords are all highlighted as data types

Scenario: Comments and strings are highlighted and do not bleed into code
  Given a file containing a `// line comment`, a `/* block comment */`, and a `"string with \n escape"`
  When the file is open as SIMPL+
  Then the comment and string spans are colored as comment/string
    And code following a closed block comment or string is colored normally
```

---

### US-SIMPLP-002 — Able to scaffold common SIMPL+ patterns with snippets

```
Summary: Able to scaffold common SIMPL+ patterns with prefix-triggered snippets

Description:
As a SIMPL+ programmer, I want prefix-triggered snippets with editable tab
stops for the boilerplate I write constantly, so that I can scaffold a module
header, an I/O declaration, an event handler, or a function without retyping
the structure each time.

Current State:
`snippets/simplplus.json` contributes 31 snippets in the standard VS Code
snippet format (`prefix`, `body`, `description`). Prefixes cover the module
header, `DIGITAL_INPUT`/`ANALOG_INPUT`/`STRING_INPUT`/`BUFFER_INPUT`,
`DIGITAL_OUTPUT`/`ANALOG_OUTPUT`/`STRING_OUTPUT`, `PUSH`, `CHANGE`, `FUNCTION`,
`FOR`, `WHILE`, `WAIT`, `#DEFINE_CONSTANT`, and `STRUCTURE`. Snippet bodies use
`${1:...}` tab stops.

Designs:
Reference snippets: `snippets/simplplus.json`.

Technical Notes:
- Snippet `body` tab-stop syntax (`${1:...}`, `$0`) is shared with Monaco, so the
  snippet set transfers directly to the Construct port.

Scope Clarification:
In Scope:
- The 31 contributed snippets and their tab stops
Out of Scope:
- User-defined / workspace snippets (use VS Code's native snippet authoring)

Acceptance Criteria:

Scenario: Insert a function snippet
  Given an open SIMPL+ file
  When the user types the function snippet prefix and accepts the suggestion
  Then a `FUNCTION` definition body is inserted
    And the cursor lands on the first editable tab stop

Scenario: Cycle through tab stops
  Given a snippet has just been inserted with two or more tab stops
  When the user presses Tab
  Then the selection advances to the next placeholder

Scenario: Module header snippet inserts the standard directives
  Given an empty SIMPL+ file
  When the user inserts the module-header snippet
  Then the standard `#SYMBOL_NAME` / `#CATEGORY` / directive scaffold is inserted
```

---

### US-SIMPLP-003 — Able to rely on bracket matching, auto-close, and comment toggling

```
Summary: Able to rely on bracket matching, auto-closing pairs, and comment toggling

Description:
As a SIMPL+ programmer, I want the editor's brackets, auto-close, and
comment-toggle behavior tuned for SIMPL+, so that editing feels native rather
than like editing plain text.

Current State:
`language-configuration.json` defines the bracket pairs, auto-closing pairs,
surrounding pairs, and comment tokens (`//` for line comments, `/* */` for block
comments) for the `simplplus` language.

Designs:
Reference: `language-configuration.json`.

Technical Notes:
- These map directly onto Monaco's `setLanguageConfiguration` in the Construct port.

Scope Clarification:
In Scope:
- Bracket matching/auto-close and `//` // `/* */` comment toggle
Out of Scope:
- Indentation rules / on-type formatting (not configured)

Acceptance Criteria:

Scenario: Toggle line comment
  Given a line of SIMPL+ code is selected
  When the user invokes Toggle Line Comment (Ctrl+/)
  Then the line is prefixed with `//`
    And invoking it again removes the `//`

Scenario: Auto-close a bracket
  Given the cursor is in an open SIMPL+ file
  When the user types `(`
  Then a matching `)` is inserted and the cursor is placed between them

Scenario: Block comment toggle wraps a selection
  Given a multi-line selection of SIMPL+ code
  When the user invokes Toggle Block Comment
  Then the selection is wrapped in `/*` and `*/`
```

---

## EP-SIMPLP-002 — Language intelligence (hover, completion, signature help)

```
Title: Language intelligence (hover, completion, signature help)

Parent Initiative: INI-SIMPLP-001 — SIMPL+ for VS Code: language support and compiler integration for Crestron SIMPL+

Audience:
- SIMPL+ programmers who need to recall function syntax, parameters, and their own declarations

Functionality Enabled:
- Hover documentation for built-in functions (description, syntax, return value, example)
- Hover signature for the user's own declared functions
- Auto-completion of built-in functions/keywords and the user's declared symbols
- Signature help for built-in functions and the user's own functions

In Scope:
- Function database load + filtering (`src/functionDb.ts`, `scripts/function-db.json`): 305 functions across 28 categories, filtered to real identifiers
- Hover, completion, and signature-help providers (`src/providers.ts`)
- User-symbol scan for completion (`scanSymbols`) and user-function signature parse (`scanUserFunctions`) in `src/symbols.ts`

Out of Scope:
- Cross-file / project-wide symbol resolution (current scope is the open document)
- Type checking / semantic diagnostics in the editor (compilation handles correctness — see EP-SIMPLP-004)

Dependencies:
- `src/providers.ts`, `src/functionDb.ts`, `src/symbols.ts`, `scripts/function-db.json`

Confluence: N/A — see `README.md` § "Language Intelligence"

Related QE stories: N/A
```

### US-SIMPLP-004 — Able to hover a built-in function to see its documentation

```
Summary: Able to hover a built-in function to see its documentation

Description:
As a SIMPL+ programmer, I want to hover over a built-in function and see its
documentation, so that I can recall its syntax and behavior without leaving the
editor or opening the CHM reference.

Current State:
The hover provider (`SimplHoverProvider` in `src/providers.ts`) looks up the
hovered word in the function database (`src/functionDb.ts`, case-insensitive)
and renders a markdown block with the function name, category, description,
syntax, return value, and example (whichever fields are present). The database
holds 305 functions across 28 categories, filtered to entries whose name is a
single identifier and that have syntax or a description.

Designs:
Reference: `src/providers.ts` (`SimplHoverProvider`, `buildDocs`),
`src/functionDb.ts`.

Technical Notes:
- The database is loaded once at activation from `scripts/function-db.json`;
  a failure to load degrades gracefully (no hover) rather than crashing activation.

Scope Clarification:
In Scope:
- Hover for built-in database functions
Out of Scope:
- Hover for language keywords without a database entry

Acceptance Criteria:

Scenario: Hover a known built-in function
  Given an open SIMPL+ file containing a call to a known built-in (e.g. `MakeString(...)`)
  When the user hovers over the function name
  Then a hover appears showing the function name and its documentation (description/syntax/return/example as available)

Scenario: Hover lookup is case-insensitive
  Given the file contains the built-in written as `makestring(...)`
  When the user hovers over it
  Then the same documentation is shown as for `MakeString`

Scenario: Hovering a non-function word shows no SIMPL+ hover
  Given the cursor hovers over an ordinary local variable that is not a known function
  When the hover would appear
  Then no SIMPL+ built-in hover is shown
```

---

### US-SIMPLP-005 — Able to hover a function I declared to see its signature

```
Summary: Able to hover a user-declared function to see its parsed signature

Description:
As a SIMPL+ programmer, I want to hover over one of my own functions and see
its signature, so that I can recall its return type and parameters without
scrolling back to its definition.

Current State:
When the hovered word is not a built-in, the hover provider falls back to
`scanUserFunctions(doc)` (`src/symbols.ts`), which parses each function
declaration's return-type keyword and single-line parameter list. The hover
shows a "user function" block with the reconstructed signature, e.g.
`INTEGER_FUNCTION GetSource(integer iInput)`.

Designs:
Reference: `src/providers.ts` (`SimplHoverProvider`, `buildUserFunctionDocs`),
`src/symbols.ts` (`scanUserFunctions`).

Technical Notes:
- Built-in database functions take precedence over a user function of the same name.
- Function declarations whose parameter list wraps across multiple lines are not
  parsed (single-line declarations only).

Scope Clarification:
In Scope:
- Hover signature for user-declared functions (return type + parameters)
Out of Scope:
- User functions whose parameter list spans multiple lines
- Rendering the function's body or doc-comment

Acceptance Criteria:

Scenario: Hover a user-declared function shows its signature
  Given a file declaring `Integer_Function GetSourceFromSwitcherInput(integer iSwitcherInput)`
  When the user hovers over `GetSourceFromSwitcherInput` anywhere it appears
  Then a hover shows `INTEGER_FUNCTION GetSourceFromSwitcherInput(integer iSwitcherInput)` labeled as a user function

Scenario: A user function with no parameters shows empty parentheses
  Given a file declaring `Function SetDestActiveAudioSourceIcon()`
  When the user hovers over `SetDestActiveAudioSourceIcon`
  Then the hover shows `FUNCTION SetDestActiveAudioSourceIcon()`

Scenario: A commented-out function is not offered
  Given a function declaration that is inside a `/* ... */` block comment
  When the user hovers over its name elsewhere
  Then it is not surfaced as a user function from the commented declaration
```

---

### US-SIMPLP-006 — Able to complete built-in functions and my own declarations

```
Summary: Able to auto-complete built-in functions and the symbols I declared in the file

Description:
As a SIMPL+ programmer, I want completion suggestions for built-in functions
and for the variables, I/O, parameters, constants, functions, and structures I
have declared, so that I can insert correct names without retyping or
misspelling them.

Current State:
The completion provider (`SimplCompletionProvider` in `src/providers.ts`) offers
every built-in from the function database — each with its category as detail and
full documentation; when a function's syntax shows a call, it inserts a
`Name($0)` snippet. It then appends the user's declared symbols from
`scanSymbols(doc)` (variables, I/O, parameters, constants, functions,
structures, and event handlers), de-duplicated by lowercased name, each mapped
to an appropriate completion kind.

Designs:
Reference: `src/providers.ts` (`SimplCompletionProvider`, `completionKindFor`),
`src/symbols.ts` (`scanSymbols`).

Technical Notes:
- Symbol detection is case-insensitive with respect to the declaring keyword
  (`integer gVol;` is detected like `INTEGER gVol;`).
- Duplicate identifiers (e.g. comma-separated declarations) appear once.

Scope Clarification:
In Scope:
- Built-in functions/keywords and current-file user declarations
Out of Scope:
- Symbols declared in other files / `#INCLUDE`d headers (open-document scope only)
- Scope-aware completion (whole-file, not block-scoped)

Acceptance Criteria:

Scenario: Built-in functions appear in completion
  Given an open SIMPL+ file
  When the user triggers completion
  Then built-in functions from the database are listed with their category as detail

Scenario: Accepting a call-style built-in inserts a call snippet
  Given completion is open and the user selects a built-in whose syntax shows a call
  When the user accepts it
  Then `Name()` is inserted with the cursor positioned inside the parentheses

Scenario: User-declared symbols appear alongside built-ins
  Given the file declares `INTEGER gVolume;` and `FUNCTION SetVolume(...)`
  When the user triggers completion
  Then `gVolume` and `SetVolume` appear in the list with appropriate kinds

Scenario: Duplicate declarations are listed once
  Given the file declares `DIGITAL_INPUT a, b, a;` (a repeated)
  When the user triggers completion
  Then `a` appears only once
```

---

### US-SIMPLP-007 — Able to see parameter hints while calling a function

```
Summary: Able to see parameter hints (signature help) while calling built-in or user functions

Description:
As a SIMPL+ programmer, I want parameter hints as I type a function call, so
that I know which argument I am on and what it expects — for built-in functions
and for my own.

Current State:
The signature-help provider (`SimplSignatureProvider` in `src/providers.ts`)
triggers on `(` and `,`. It walks back from the cursor to find the called
function name. For a built-in, each line of the database `syntax` becomes a
separate overload with parameters parsed from the parentheses. If the name is
not a built-in, it falls back to a user function from `scanUserFunctions(doc)`,
presenting the reconstructed signature with each parameter as a hint. The active
parameter is tracked by counting argument-separating commas at the current call
depth.

Designs:
Reference: `src/providers.ts` (`SimplSignatureProvider`, `functionCallName`,
`commaDepth`, `parseParams`), `src/symbols.ts` (`scanUserFunctions`).

Technical Notes:
- Built-ins take precedence over user functions of the same name.
- The active-parameter index accounts for nested parentheses in arguments.

Scope Clarification:
In Scope:
- Signature help for built-ins (one overload per syntax line) and user functions
- Active-parameter tracking via comma depth
Out of Scope:
- User functions whose parameter list wraps across lines

Acceptance Criteria:

Scenario: Signature help opens for a built-in call
  Given the user types a known built-in function name followed by `(`
  When the call is being typed
  Then a signature popup shows the function's syntax/overload(s) and description

Scenario: Active parameter advances with commas
  Given signature help is showing for a multi-parameter function
  When the user types an argument and a comma
  Then the highlighted parameter advances to the next one

Scenario: Signature help for a user-declared function
  Given a file declaring `Function RouteSource(integer iSource, integer iDestination)`
  When the user types `RouteSource(`
  Then signature help shows `FUNCTION RouteSource(integer iSource, integer iDestination)` with two parameter hints
```

---

## EP-SIMPLP-003 — Code navigation & document symbols

```
Title: Code navigation & document symbols

Parent Initiative: INI-SIMPLP-001 — SIMPL+ for VS Code: language support and compiler integration for Crestron SIMPL+

Audience:
- SIMPL+ programmers navigating large modules

Functionality Enabled:
- Go to Definition for user-declared symbols
- Go to Symbol / Outline listing all declarations in the file
- Event handlers (PUSH/RELEASE/CHANGE) included in the outline

In Scope:
- Definition provider and document-symbol provider (`src/providers.ts`)
- Symbol scanner (`src/symbols.ts`) covering functions, I/O, variables, parameters, constants, structures, struct-typed variables, and event handlers
- Comment/string masking so declarations inside comments are not surfaced

Out of Scope:
- Cross-file navigation / find-all-references across files
- Wrapped multi-line declarations (terminating `;` on a later line) — not captured

Dependencies:
- `src/providers.ts` (`SimplDefinitionProvider`, `SimplDocumentSymbolProvider`)
- `src/symbols.ts` (`scanSymbols`, `maskComments`)

Confluence: N/A — see `README.md` § "Language Intelligence"

Related QE stories: N/A
```

### US-SIMPLP-008 — Able to jump to where a symbol is declared

```
Summary: Able to jump from a symbol usage to its declaration (Go to Definition)

Description:
As a SIMPL+ programmer, I want to jump from a symbol usage to its declaration,
so that I can navigate a large module quickly.

Current State:
The definition provider (`SimplDefinitionProvider` in `src/providers.ts`) scans
the document for declarations matching the word under the cursor
(case-insensitive) and returns their identifier locations. If multiple
declarations match, all candidate locations are offered.

Designs:
Reference: `src/providers.ts` (`SimplDefinitionProvider`), `src/symbols.ts`.

Technical Notes:
- Lookup is case-insensitive.
- See EP-SIMPLP-005 / known issues for the `F12` keybinding interaction with the
  compile command.

Scope Clarification:
In Scope:
- Go to Definition for current-file user declarations
Out of Scope:
- Definitions in other files / included headers

Acceptance Criteria:

Scenario: Jump to a variable declaration
  Given a file where `gVolume` is declared and later used
  When the cursor is on a usage of `gVolume` and the user invokes Go to Definition
  Then the editor navigates to the `gVolume` identifier at its declaration

Scenario: Lookup is case-insensitive
  Given `gVolume` is declared and used as `GVOLUME`
  When the user invokes Go to Definition on `GVOLUME`
  Then it navigates to the `gVolume` declaration

Scenario: A non-declared word navigates nowhere
  Given the cursor is on a built-in function name with no user declaration
  When the user invokes Go to Definition
  Then no navigation occurs
```

---

### US-SIMPLP-009 — Able to list and jump to every declaration via Go to Symbol / Outline

```
Summary: Able to list and jump to every declaration in the file (Go to Symbol / Outline)

Description:
As a SIMPL+ programmer, I want a symbol list / outline for the open file, so
that I can see its structure and jump to any declaration.

Current State:
The document-symbol provider (`SimplDocumentSymbolProvider` in
`src/providers.ts`) returns the results of `scanSymbols(doc)`
(`src/symbols.ts`): functions, I/O (`DIGITAL_INPUT`…), variables, parameters,
constants (`#DEFINE_CONSTANT`), structures, and struct-typed variables — each
with an appropriate kind, a jump target on the identifier, and the full
declaration line as its range. The scanner masks comments and string literals
first, so declarations inside them are not listed. This populates Go to Symbol
(`@` / Ctrl+Shift+O), the Outline view, and breadcrumbs.

Designs:
Reference: `src/providers.ts` (`SimplDocumentSymbolProvider`), `src/symbols.ts`
(`scanSymbols`, `maskComments`).

Technical Notes:
- Ranges are 0-based in VS Code; the Construct/Monaco port must convert to 1-based.
- Wrapped multi-line declarations (terminating `;` on a later line) are not
  captured — see Out of Scope.

Scope Clarification:
In Scope:
- Functions, I/O, variables, parameters, constants, structures, struct-typed vars
- Outline view + breadcrumbs fed by the same provider
Out of Scope:
- Wrapped multi-line I/O/variable declarations (not captured)
- Nested symbols (struct members / function locals surface flat, not nested)

Acceptance Criteria:

Scenario: Go to Symbol lists declarations
  Given a module declaring functions, I/O, variables, constants, and a structure
  When the user invokes Go to Symbol (`@` / Ctrl+Shift+O)
  Then each declaration is listed with a kind, and selecting one navigates to it

Scenario: Declarations inside comments are not listed
  Given a function declaration that appears inside a `/* ... */` block comment
  When the user invokes Go to Symbol
  Then that commented declaration is not listed

Scenario: The Outline view shows the same symbols
  Given an open SIMPL+ module
  When the user opens the Outline view
  Then it shows the same declarations as Go to Symbol
```

---

### US-SIMPLP-010 — Able to find event handlers in the outline

```
Summary: Able to find PUSH/RELEASE/CHANGE event handlers in the outline

Description:
As a SIMPL+ programmer, I want my event handlers to appear in the symbol list,
so that I can jump straight to the `PUSH`/`RELEASE`/`CHANGE` block for a given
signal.

Current State:
`scanSymbols` (`src/symbols.ts`) detects event-handler declarations matching
`(THREADSAFE) PUSH | RELEASE | CHANGE <signal>` and emits each as a symbol keyed
by its signal name, with the event type as detail and the `Event` kind. The
detection runs on comment-masked text, so handler keywords inside comments are
ignored. (`EVENT` is intentionally excluded to avoid false positives on the
English word "Event".)

Designs:
Reference: `src/symbols.ts` (`EVENT_RE`, `scanSymbols`).

Technical Notes:
- Handlers are keyed by signal name, so Go to Symbol filtering by the signal name
  finds the handler.
- `THREADSAFE`-prefixed handlers are detected the same way.

Scope Clarification:
In Scope:
- `PUSH`, `RELEASE`, `CHANGE` handlers, optionally `THREADSAFE`-prefixed
Out of Scope:
- Bare `EVENT { }` blocks and socket event handlers (not listed)

Acceptance Criteria:

Scenario: PUSH and CHANGE handlers appear in the outline
  Given a module with `PUSH Volume_Up { ... }` and `CHANGE Volume_Set { ... }`
  When the user invokes Go to Symbol
  Then `Volume_Up` (PUSH handler) and `Volume_Set` (CHANGE handler) are listed
    And selecting one navigates to its signal

Scenario: THREADSAFE-prefixed handler is listed
  Given a module with `THREADSAFE CHANGE Command_In { ... }`
  When the user invokes Go to Symbol
  Then `Command_In` is listed as a CHANGE handler

Scenario: An event keyword inside a comment is not listed
  Given a comment line `// Event Handlers` inside a `/* ... */` block
  When the user invokes Go to Symbol
  Then no spurious handler entry is produced from that comment
```

---

## EP-SIMPLP-004 — Compiler integration & diagnostics

```
Title: Compiler integration & diagnostics

Parent Initiative: INI-SIMPLP-001 — SIMPL+ for VS Code: language support and compiler integration for Crestron SIMPL+

Audience:
- SIMPL+ programmers compiling modules during development
- Integrators validating a whole project of `.usp` files

Functionality Enabled:
- Compile the current `.usp` from the editor
- Compile all `.usp` files in the workspace
- Inline error/warning diagnostics, a Problems list, and a live output channel
- Automatic discovery of `SPlusCC.exe` regardless of install location
- Target control-system series selection

In Scope:
- `simplplus.compile` and `simplplus.compileAll` commands, context menus, and keybindings (`package.json`)
- Compiler invocation and output parsing (`src/extension.ts`): args `\build <files> \target <series>`, error regex `[file] Error N (Line X) - message`, diagnostics collection, output channel, batching
- Compiler auto-detection (`src/compilerPath.ts`): setting → install dirs → Windows registry → prompt-to-locate
- `simplplus.compileTarget` setting (series2 / series3 / series2 series3)

Out of Scope:
- `simplplus.compileOnSave` — the setting is declared in `package.json` but is NOT wired to any save handler (no auto-compile on save)
- Non-Windows compilation (depends on the Windows-only `SPlusCC.exe`)

Dependencies:
- `src/extension.ts` (commands, compile orchestration, diagnostics, output channel)
- `src/compilerPath.ts` (auto-detection + prompt)
- `package.json` (commands, keybindings, menus, settings)

Confluence: N/A — see `README.md` §§ "Compiler Integration", "Configuration"

Related QE stories: N/A
```

### US-SIMPLP-011 — Able to compile the current file from the editor

```
Summary: Able to compile the current `.usp` file from the editor

Description:
As a SIMPL+ programmer, I want to compile the active `.usp` without leaving the
editor, so that I get fast feedback on errors.

Current State:
The `simplplus.compile` command (bound to `F12` for SIMPL+ files, also on the
editor context menu and the Command Palette) saves the active document and
invokes `SPlusCC.exe` for the configured target series, streaming output to the
"SIMPL+" output channel. On success a notification is shown; on failure an error
notification offers to open the Problems view. (`src/extension.ts`.)

Designs:
Reference: `src/extension.ts` (`compileCurrentFile`, `runCompiler`).

Technical Notes:
- The active document is saved before compiling.
- `F12` is also the default Go-to-Definition gesture; see known issues in
  EP-SIMPLP-005.

Scope Clarification:
In Scope:
- Compile-current via command, context menu, and keybinding
Out of Scope:
- Compile-on-save (declared setting not wired)

Acceptance Criteria:

Scenario: Compile the active file
  Given an active `.usp` file and a resolvable compiler
  When the user runs "Compile Current File"
  Then the file is saved
    And `SPlusCC.exe` is invoked for the configured target
    And compiler output is streamed to the SIMPL+ output channel

Scenario: Compile is unavailable without a SIMPL+ file
  Given no `.usp` file is active
  When the user runs "Compile Current File"
  Then a warning indicates no SIMPL+ file is active
    And no compiler process is started

Scenario: Success notification on clean compile
  Given a `.usp` that compiles without errors
  When the user compiles it
  Then a success notification is shown
```

---

### US-SIMPLP-012 — Able to compile all files in the workspace

```
Summary: Able to compile every `.usp` file in the workspace at once

Description:
As an integrator, I want to compile every `.usp` in the workspace in one action,
so that I can validate a whole project.

Current State:
The `simplplus.compileAll` command (bound to `Shift+F12` for SIMPL+ files) finds
all `**/*.usp` in the workspace (excluding `node_modules`), compiles them in
batches of 50 to avoid command-line length limits, and shows a combined result
summary. If no `.usp` files exist, an informational message is shown.
(`src/extension.ts`.)

Designs:
Reference: `src/extension.ts` (`compileAllFiles`, `runBatch`, `spawnCompiler`).

Technical Notes:
- Batching keeps the spawned command line within OS limits for large projects.

Scope Clarification:
In Scope:
- Workspace-wide compile with batching and a combined summary
Out of Scope:
- Selective/changed-files-only compilation

Acceptance Criteria:

Scenario: Compile all files in a workspace
  Given a workspace containing multiple `.usp` files
  When the user runs "Compile All Files in Workspace"
  Then every `.usp` (outside node_modules) is compiled
    And a combined summary of created/error counts is shown

Scenario: No files to compile
  Given a workspace with no `.usp` files
  When the user runs "Compile All Files in Workspace"
  Then an informational message states that none were found
```

---

### US-SIMPLP-013 — Able to see compiler errors inline and in the Problems list

```
Summary: Able to see compiler errors and warnings inline and in the Problems list

Description:
As a SIMPL+ programmer, I want errors and warnings surfaced in the editor, so
that I can find and fix them by clicking instead of reading raw output.

Current State:
Compiler output lines matching `[file] Error|Warning N (Line X) - message` are
parsed into diagnostics on the reported line, with Error/Warning severity and
source "SIMPL+". Diagnostics appear as inline squiggles and in the Problems list,
each linking to the file and line. The diagnostics collection is cleared at the
start of each compile run. (`src/extension.ts`.)

Designs:
Reference: `src/extension.ts` (`ERROR_RE`, `spawnCompiler`, diagnostics
collection).

Technical Notes:
- Reported line numbers may be relative to the compiled function body rather than
  the absolute file line (compiler behavior; documented limitation).

Scope Clarification:
In Scope:
- Inline diagnostics + Problems list with file/line links
- Clearing diagnostics at the start of each run
Out of Scope:
- Quick-fixes / code actions on diagnostics (not implemented)

Acceptance Criteria:

Scenario: An error becomes an inline diagnostic
  Given a `.usp` that produces a compiler error on a line
  When the user compiles it
  Then a red squiggle appears on the reported line
    And a matching entry appears in the Problems list linking to the file and line

Scenario: Warnings are distinguished from errors
  Given a `.usp` that produces a warning
  When the user compiles it
  Then the diagnostic is rendered with Warning severity

Scenario: Diagnostics are cleared on the next run
  Given a previous compile produced diagnostics
  When the user compiles again and the issues are resolved
  Then the stale diagnostics are cleared
```

---

### US-SIMPLP-014 — Able to compile without configuring the compiler path

```
Summary: Able to compile without configuring the compiler path (auto-detection)

Description:
As a SIMPL+ programmer, I want the extension to find `SPlusCC.exe`
automatically, so that I don't have to know or configure where SIMPL Windows
was installed.

Current State:
`resolveCompilerPath()` (`src/compilerPath.ts`) resolves the compiler in order:
(1) the `simplplus.compilerPath` setting if set; (2) `Crestron\Simpl\SPlusCC.exe`
under common Program Files locations; (3) the Windows registry uninstall hives
(searched via `reg.exe` for the SIMPL Windows install location). If it cannot be
found, `promptForCompiler()` shows an error with a "Locate SPlusCC.exe…" file
picker and saves the choice to global settings. The default `compilerPath` is
blank (auto-detect).

Designs:
Reference: `src/compilerPath.ts`. End-user docs: `README.md` § "Requirements".

Technical Notes:
- Registry lookup is dependency-free (`reg.exe`).
- A user-set `compilerPath` always wins over auto-detection.

Scope Clarification:
In Scope:
- Setting → install-dir → registry resolution, with a locate prompt fallback
Out of Scope:
- Non-Windows compiler discovery

Acceptance Criteria:

Scenario: Auto-detect on a standard install
  Given `simplplus.compilerPath` is blank and SIMPL Windows is installed
  When the user compiles
  Then the compiler is resolved automatically from install dirs or the registry

Scenario: Explicit setting takes precedence
  Given `simplplus.compilerPath` is set to a valid path
  When the user compiles
  Then that path is used regardless of auto-detection

Scenario: Prompt to locate when not found
  Given the compiler cannot be resolved
  When the user compiles
  Then an error offers a "Locate SPlusCC.exe…" file picker
    And the chosen path is saved to settings for future compiles
```

---

### US-SIMPLP-015 — Able to choose the target control-system series

```
Summary: Able to choose the target control-system series for compilation

Description:
As a SIMPL+ programmer, I want to choose the control-system target, so that
compilation matches my hardware.

Current State:
The `simplplus.compileTarget` setting (`series2`, `series3`, or
`series2 series3`; default `series3`) is passed to the compiler as the `\target`
argument on every compile. (`src/extension.ts`, `package.json`.)

Designs:
Reference: `package.json` (configuration), `src/extension.ts` (`runCompiler`).

Technical Notes:
- The target is read fresh on each compile, so changing the setting takes effect
  on the next compile without reload.

Scope Clarification:
In Scope:
- series2 / series3 / series2 series3 target selection
Out of Scope:
- Per-file or per-project target overrides

Acceptance Criteria:

Scenario: Default target is series3
  Given the user has not changed `simplplus.compileTarget`
  When the user compiles
  Then the compiler is invoked with target `series3`

Scenario: Changing the target affects the next compile
  Given the user sets `simplplus.compileTarget` to `series2`
  When the user compiles
  Then the compiler is invoked with target `series2`
```

---

## EP-SIMPLP-005 — Activation, status & host isolation

```
Title: Activation, status & host isolation

Parent Initiative: INI-SIMPLP-001 — SIMPL+ for VS Code: language support and compiler integration for Crestron SIMPL+

Audience:
- SIMPL+ programmers relying on the tooling being active
- Extension maintainers developing or debugging the extension

Functionality Enabled:
- A clear, always-visible indication that the extension is loaded and which language owns the file
- A development workflow that isolates the extension from other tools that also claim `.usp`

In Scope:
- Activation indicator: status-bar badge, activation notification, and a SIMPL+ output channel that logs each `@` symbol scan with the document's language id (`src/extension.ts`, `src/providers.ts`)
- `simplplus.showLog` command to open the log
- Dev-host isolation via `--disable-extensions` in `.vscode/launch.json`, and guidance for resolving `.usp` ownership conflicts with other installed extensions

Out of Scope:
- Telemetry / usage reporting (none)
- A settings UI beyond the contributed configuration

Dependencies:
- `src/extension.ts` (status item, output channel, `simplplus.showLog`)
- `src/providers.ts` (per-scan logging)
- `.vscode/launch.json` (`--disable-extensions`)

Confluence: N/A — see `README.md` §§ "Language Intelligence", "Troubleshooting", "Installation → Sideload for development"

Related QE stories: N/A
```

### US-SIMPLP-016 — Able to tell at a glance that the SIMPL+ tooling is active

```
Summary: Able to tell at a glance that the SIMPL+ tooling is active

Description:
As a SIMPL+ programmer, I want a clear indication that the language tooling is
loaded, so that I can trust that highlighting, IntelliSense, and compile are
available — and diagnose it quickly when they are not.

Current State:
On activation the extension shows a status-bar badge ("✓ SIMPL+"), a one-time
activation notification, and opens a "SIMPL+" output channel. The badge's click
command (`simplplus.showLog`) opens the log. The document-symbol provider logs
each `@` scan with the document's `languageId` and the number of symbols found,
which makes language-ownership conflicts visible. (`src/extension.ts`,
`src/providers.ts`.)

Designs:
Reference: `src/extension.ts` (status item, output channel), `src/providers.ts`
(per-scan logging).

Technical Notes:
- The per-scan log line reports the actual `languageId`, which is the decisive
  signal when another extension has claimed `.usp` (see US-SIMPLP-017).

Scope Clarification:
In Scope:
- Status badge, activation notification, output channel, `simplplus.showLog`
Out of Scope:
- Telemetry

Acceptance Criteria:

Scenario: Activation shows the status badge and notification
  Given a `.usp` file is opened
  When the extension activates
  Then a "✓ SIMPL+" badge appears in the status bar
    And a one-time activation notification is shown

Scenario: The badge opens the log
  Given the extension is active
  When the user clicks the "✓ SIMPL+" status-bar badge
  Then the SIMPL+ output channel is shown

Scenario: A symbol scan logs the active language
  Given an open `.usp` recognized as `simplplus`
  When the user invokes Go to Symbol
  Then the SIMPL+ output logs a line reporting `lang=simplplus` and the symbol count
```

---

### US-SIMPLP-017 — Able to develop the extension without `.usp` conflicts from other tools

```
Summary: Able to develop/run the extension without another extension hijacking `.usp`

Description:
As an extension maintainer (and as a user diagnosing why features are missing),
I want the SIMPL+ extension to own `.usp` reliably, so that the `@` outline,
hover, and completion actually run instead of being silently disabled by another
installed extension that also claims `.usp`.

Current State:
The Extension Development Host loads all installed extensions plus the one under
development. When another installed extension also registers `.usp`, VS Code may
assign the file to that extension's language (the status bar can still display
"SIMPL+" because the alias collides), and this extension's providers — scoped to
`{ language: 'simplplus' }` — never fire. The included `.vscode/launch.json`
passes `--disable-extensions`, so the dev host runs only this extension. The
README documents how to confirm the active language via the SIMPL+ output and how
to resolve the conflict for a packaged install.

Designs:
Reference: `.vscode/launch.json`, `README.md` §§ "Troubleshooting", "Installation
→ Sideload for development".

Technical Notes:
- The `@` symbol-scan log line (US-SIMPLP-016) reports the real `languageId`,
  which is how the conflict is confirmed.
- For a packaged VSIX installed alongside a conflicting extension, the user must
  choose which extension owns `.usp` (disable the other, or change the file
  association).

Scope Clarification:
In Scope:
- Dev-host isolation via `--disable-extensions`
- Documented diagnosis and resolution of `.usp` ownership conflicts
Out of Scope:
- Programmatic takeover of `.usp` from another installed extension (VS Code does
  not permit this; it is a user/association decision)

Acceptance Criteria:

Scenario: The dev host runs only this extension
  Given the developer launches the extension with the included launch config (F5)
  When the Extension Development Host opens
  Then other installed extensions are disabled in that host
    And opening a `.usp` exercises this extension's `simplplus` providers

Scenario: The active language is verifiable when features seem missing
  Given a `.usp` is open but Go to Symbol shows nothing
  When the user checks the SIMPL+ output channel after pressing `@`
  Then the logged `languageId` reveals whether the file is owned by `simplplus` or another language

Scenario: Resolving a packaged-install conflict
  Given the extension is installed as a VSIX alongside another extension that claims `.usp`
  When the user sets the `.usp` file association to "SIMPL+" (or disables the other extension)
  Then this extension's language features run for `.usp` files
```
