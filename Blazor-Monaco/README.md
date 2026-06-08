# SIMPL+ Syntax Editor — Blazor + Monaco

How to bring the **SIMPL+ language editing experience** (the behavior proven out in the
VS Code POC in the **parent folder** — this `VSCodeSIMPL+Plugin` repo) into **Crestron
Construct**, which is a **Blazor** application, using the **Monaco** editor.

This folder lives inside the VS Code plugin repo and holds the reusable assets pulled from
the POC plus this design document. It is **not** a running project yet — it's the plan and
the carry-over files.

---

## Why this is the maximum-reuse path

Monaco *is* the editor engine inside VS Code, and its language API is nearly identical to
the VS Code extension API. That means the POC is a **light port, not a rewrite**:

- `vscode.languages.register*Provider(...)` → `monaco.languages.register*Provider(...)` — same method names, same shapes (with small differences noted below).
- The function database and the symbol-scanner regex logic carry over unchanged.
- The TextMate grammar can be reused as-is, or ported to Monaco's native tokenizer.

Construct stays Blazor/C# for what C# is good at (hosting, the compiler process, files); the
language intelligence lives in a small JavaScript/TypeScript module loaded next to Monaco.

---

## Architecture (3 layers)

```
┌─ Blazor (C#) ───────────────────────────────────────┐
│  • BlazorMonaco component hosts the Monaco editor    │
│  • Compiler bridge: spawn SPlusCC.exe, parse output, │
│    push results back as Monaco markers               │
│  • File I/O, project model, theming                  │
└──────────────┬───────────────────────────────────────┘
               │ JS interop (BlazorMonaco / IJSRuntime)
┌──────────────▼─ JS/TS language module (reused POC) ──┐
│  • Registers the 'simplplus' language                │
│  • Grammar (syntax highlighting)                     │
│  • Providers: hover, completion, signature help,     │
│    definition, documentSymbol  (the `@` outline)     │
│  • Symbol scanner  (ported from symbols.ts)          │
│  • function-db.json  (verbatim)                      │
└───────────────────────────────────────────────────────┘
```

**Key principle:** keep the language support as a **JS/TS module**, *not* rewritten in C#.
That's what preserves the POC investment. Blazor only hosts and bridges.

---

## Reusable assets (in `reusable-assets/`)

These were copied directly from the POC. Each is described below with how it maps into
Blazor + Monaco.

### `function-db.json` — ✅ reuse **verbatim**
- **305 entries**, one per built-in SIMPL+ function / keyword, across **28 categories**
  (Array Operations, Bit & Byte Functions, Data Conversion, Declarations, Direct Socket
  Access, Email Functions, …). Parsed from the Crestron CHM language reference.
- **Fields per entry:** `name`, `category`, `syntax`, `example`, `description`,
  `return_value`, `file`.
- **Use in Monaco:** ship as a static web asset and `fetch()` it from the JS module at
  startup. It powers:
  - **Hover** — render `description` + `syntax` + `return_value` + `example` as markdown.
  - **Completion** — one `CompletionItem` per entry; when `syntax` shows a call (`Name(...)`),
    insert a `Name($0)` snippet.
  - **Signature help** — split `syntax` into overloads, parse params between `(` `)`.
- **Filtering note (from the POC):** keep only entries whose `name` is a single identifier
  (`/^[A-Za-z_]\w*$/`) and that have a `syntax` or `description` — this drops CHM
  doc-section titles like "Find Next" / "Examples".

### `simplplus.tmLanguage.json` — 🟡 reuse, with a decision (see below)
- TextMate grammar covering preprocessor directives, I/O declarations, data types, event
  handlers, control flow, built-in functions, comments, strings, numbers, operators.
- **Use in Monaco:** Monaco's *native* tokenizer is **Monarch**, not TextMate. Two options:
  1. **Reuse as-is** via `vscode-textmate` + `vscode-oniguruma` (WASM) wired into Monaco's
     token provider. Identical coloring to the POC; adds a WASM dependency + setup.
  2. **Port to Monarch** (a one-time rewrite into Monaco's state-machine DSL). Lighter
     runtime, no WASM, but you maintain a second grammar format.
  - Recommendation: reuse via vscode-textmate **if** exact parity matters; otherwise port to
    Monarch for a cleaner runtime. This is the *only* asset facing a possible rewrite.

### `language-configuration.json` — 🟡 reuse the **data**
- Brackets, auto-closing pairs, and comment tokens (`//`, `/* */`).
- **Use in Monaco:** map onto `monaco.languages.setLanguageConfiguration('simplplus', { ... })`
  — same concepts (`comments`, `brackets`, `autoClosingPairs`, `surroundingPairs`).

### `simplplus.snippets.json` — 🟡 reuse the **data**
- **31 snippets** (module header, I/O declarations, `PUSH`/`CHANGE`/`EVENT` handlers,
  `FUNCTION`, loops, `WAIT`, `#DEFINE_CONSTANT`, `STRUCTURE`, …) in VS Code snippet format
  (`prefix`, `body`, `description`).
- **Use in Monaco:** fold these into the completion provider as snippet `CompletionItem`s
  (`insertTextRules = InsertAsSnippet`). The `${1:...}` tab-stop syntax is shared between
  VS Code and Monaco, so the `body` strings transfer directly.

> **Source logic to port (kept in the POC, not copied here as data):**
> `../src/symbols.ts` (regex symbol scanner) and `../src/providers.ts` (the five
> providers). These are TypeScript and port ~1:1 to a Monaco module — see below.

---

## Porting the language intelligence (`symbols.ts` + `providers.ts`)

The logic is portable; only the editor bindings change. Provider mapping:

| POC (VS Code API) | Monaco API | Powers |
|---|---|---|
| `registerHoverProvider` | `monaco.languages.registerHoverProvider` | Hover docs |
| `registerCompletionItemProvider` | `monaco.languages.registerCompletionItemProvider` | IntelliSense |
| `registerSignatureHelpProvider` | `monaco.languages.registerSignatureHelpProvider` | Param hints |
| `registerDefinitionProvider` | `monaco.languages.registerDefinitionProvider` | Go to Definition (F12) |
| `registerDocumentSymbolProvider` | `monaco.languages.registerDocumentSymbolProvider` | **`@` Go to Symbol + Outline** |

### Porting gotchas (small but real)
- **0-based → 1-based (the #1 thing to get right).** VS Code `Position`/`Range` are
  **0-based**; Monaco `IRange` is **1-based** (`startLineNumber`, `startColumn`,
  `endLineNumber`, `endColumn`). The POC's `symbols.ts` builds 0-based ranges — **add 1**
  when constructing Monaco ranges, or the outline and jump-to-definition targets land on the
  wrong line/column.
- **Completion items** need an explicit **`range`** (the text span to replace) and a `kind`
  from `monaco.languages.CompletionItemKind`. Snippets require
  `insertTextRules: monaco.languages.CompletionItemInsertTextRule.InsertAsSnippet`.
- **Markdown:** VS Code `MarkdownString` → plain `{ value: string, isTrusted?: boolean }`.
- **Enums** are Monaco's own: `CompletionItemKind`, `SymbolKind`, etc.
- The regex logic itself (declaration/function/struct/const matching, comment masking) is
  identical — JS regex transfers unchanged.

### Known scanner gaps to carry over / fix
From the POC, the symbol scanner currently misses:
- **Wrapped multi-line declarations** — an I/O/var declaration whose terminating `;` is on a
  later line than the type keyword is skipped (the decl regex expects `;` on the same line).
- **Event handlers** (`PUSH`, `RELEASE`, `CHANGE`, `EVENT`, `THREADSAFE`) are not listed in
  the `@` outline.
Worth fixing during the port if Construct wants them in the outline.

---

## Compiler integration — depends on Blazor hosting model

The POC shells out to `SPlusCC.exe` and parses its output. In Construct:

- **Blazor Server:** C# runs server-side → spawn `SPlusCC.exe` directly with
  `System.Diagnostics.Process` (closest to the POC's `extension.ts`).
- **Blazor WebAssembly:** the browser can't launch processes → the compile call must go to a
  **backend API endpoint** that runs `SPlusCC.exe` server-side and returns the parsed result.

Reusable **logic** regardless of model:
- **Argument construction:** `\build <files...> \target <series2|series3|series2 series3>`.
- **Output parsing regex:** `^\[(.+?)\]\s+(Error|Warning)\s+\d+\s+\(Line\s+(\d+)\)\s+-\s+(.+)$`
  → `[file] Error 1001 (Line 9) - message`.
- **Surface results in Monaco** via `monaco.editor.setModelMarkers(model, owner, markers)` —
  the equivalent of the POC's VS Code `DiagnosticCollection` (red squiggles + problem list).
- **Caveat from the POC:** compiler line numbers may be relative to the function body, not
  the absolute file line.

---

## Open-source libraries

| Library | Role | License |
|---|---|---|
| **monaco-editor** | The editor engine | MIT |
| **BlazorMonaco** (NuGet) | Blazor wrapper + JS interop to mount Monaco | MIT |
| **vscode-textmate** | Load `.tmLanguage.json` grammars (only if reusing the TextMate grammar) | MIT |
| **vscode-oniguruma** | WASM regex engine that vscode-textmate needs | MIT |

> If you port the grammar to **Monarch** instead, you drop the `vscode-textmate` +
> `vscode-oniguruma` dependencies entirely.

---

## Two decisions still open

1. **Grammar:** reuse `simplplus.tmLanguage.json` via vscode-textmate (parity, +WASM), or
   port it to **Monarch** (cleaner runtime, one-time rewrite)?
2. **Compiler wiring:** is Construct **Blazor Server** (spawn `SPlusCC.exe` directly) or
   **Blazor WebAssembly** (compile via a backend API)?

Answering these pins down the final module shape and the compiler bridge.

---

## Suggested next steps

1. Decide grammar approach (Monarch vs vscode-textmate) and hosting model (Server vs WASM).
2. Stand up a minimal BlazorMonaco host page that mounts Monaco for the `simplplus` language.
3. Port `symbols.ts` → a Monaco `DocumentSymbolProvider` (mind the 0-based→1-based ranges).
4. Port `providers.ts` (hover/completion/signature/definition), feeding from
   `function-db.json` + the snippet set.
5. Wire `setLanguageConfiguration` from `language-configuration.json`.
6. Implement the compiler bridge (C#) and map output to `setModelMarkers`.

---

## Provenance

All `reusable-assets/` files were copied from the VS Code POC at
`C:\ClaudeProjects\VSCodeSIMPL+Plugin`:

| Asset here | Source in POC |
|---|---|
| `function-db.json` | `scripts/function-db.json` |
| `simplplus.tmLanguage.json` | `syntaxes/simplplus.tmLanguage.json` |
| `language-configuration.json` | `language-configuration.json` |
| `simplplus.snippets.json` | `snippets/simplplus.json` |

The provider/scanner **logic** to port lives in the POC's `src/providers.ts` and
`src/symbols.ts`.
