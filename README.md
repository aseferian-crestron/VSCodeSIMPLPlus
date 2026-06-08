# SIMPL+ for Visual Studio Code

A Visual Studio Code extension providing full language support for **Crestron SIMPL+** — syntax highlighting, code snippets, and integrated compiler support.

---

## Features

### Syntax Highlighting
Complete TextMate grammar covering the entire SIMPL+ language:
- Preprocessor directives (`#SYMBOL_NAME`, `#DEFINE_CONSTANT`, `#IF_DEFINED`, etc.)
- I/O declarations (`DIGITAL_INPUT`, `ANALOG_OUTPUT`, `BUFFER_INPUT`, etc.)
- Data types (`INTEGER`, `STRING`, `LONG_INTEGER`, `REAL`, etc.)
- Event handlers (`PUSH`, `RELEASE`, `CHANGE`, `EVENT`, `THREADSAFE`)
- Control flow (`IF`/`ELSE`, `FOR`, `WHILE`, `DO`/`UNTIL`, `SWITCH`)
- Built-in functions (`Print`, `MakeString`, `Left`, `Gather`, `SocketConnect`, etc.)
- Comments (`//` and `/* */`), strings, numbers, and operators

### Language Intelligence
Editor smarts backed by a database of 305 SIMPL+ functions (parsed from the CHM language reference) plus a scan of the symbols you declare in the current file:

- **Hover** — documentation, syntax, return value, and examples for built-in functions.
- **Auto-completion** (`Ctrl+Space`) — all built-in functions/keywords *plus* your own declared variables, I/O, parameters, constants, functions, and structures. Functions insert a call snippet.
- **Signature help** — parameter hints as you type inside `(` `)`, with one overload per documented syntax line.
- **Go to Definition** (`F12`) — jump to where a user symbol is declared.
- **Go to Symbol / Outline** — press **`Ctrl+Shift+O`** (or type **`@`** in Quick Open) to list every symbol you've declared in the file: functions, I/O, variables, parameters, constants, and structures. Also drives the **Outline** view and breadcrumbs.

When the extension is loaded you'll see a **✓ SIMPL+** badge in the status bar (click it to open the SIMPL+ log). On activation it also shows a brief "extension is active" notification.

### Code Snippets
30+ snippets for common SIMPL+ patterns. Type a prefix and press `Tab`:

| Prefix | Inserts |
|--------|---------|
| `header` | Full module header (`#SYMBOL_NAME`, `#CATEGORY`, etc.) |
| `push` | `PUSH` event handler |
| `change` | `CHANGE` event handler |
| `func` | `FUNCTION` definition |
| `for` | `FOR` loop |
| `while` | `WHILE` loop |
| `din` / `dout` | `DIGITAL_INPUT` / `DIGITAL_OUTPUT` declaration |
| `ain` / `aout` | `ANALOG_INPUT` / `ANALOG_OUTPUT` declaration |
| `sin` / `sout` | `STRING_INPUT` / `STRING_OUTPUT` declaration |
| `wait` | Timed `WAIT` block |
| `const` | `#DEFINE_CONSTANT` |
| `struct` | `STRUCTURE` definition |

### Compiler Integration
Compile `.usp` files directly from VS Code using the Crestron `SPlusCC.exe` command-line compiler.

- **Errors appear inline** as red squiggles in the editor
- **Problems panel** lists all errors and warnings with file + line links
- **Output channel** shows full compiler output in real time

**Keyboard shortcuts:**

| Key | Action |
|-----|--------|
| `F12` | Compile current file |
| `Shift+F12` | Compile all `.usp` files in workspace |

Commands are also available via **right-click → SIMPL+: Compile Current File** and the Command Palette (`Ctrl+Shift+P` → `SIMPL+`).

---

## Requirements

- **Visual Studio Code** 1.75 or later
- **Crestron SIMPL Windows** installed (provides `SPlusCC.exe`)
  - The compiler is **auto-detected** from common install locations and the Windows registry, so it works no matter which directory SIMPL Windows was installed to. If it can't be found, the extension prompts you to locate `SPlusCC.exe` (and remembers your choice). You can also set `simplplus.compilerPath` manually.

---

## Installation

### From VSIX (manual install)
1. Clone or download this repository
2. Run `npm install` then `npm run compile` in the project folder
3. In VS Code: **Extensions** → `...` menu → **Install from VSIX…** → select the built `.vsix`

### Sideload for development
1. Clone this repository
2. Run `npm install`
3. Open the folder in VS Code and press `F5`. This runs the `npm: compile` pre-launch task (`tsc`) and opens a new **Extension Development Host** window with the extension loaded.
4. In that host window, open a `.usp`/`.ush` file. On activation you'll see a **✓ SIMPL+** badge in the status bar and an "extension is active" notification.

**Notes:**
- The included `.vscode/launch.json` passes `--disable-extensions`, so the dev host runs **only** this extension. This is intentional: another installed extension that also claims `.usp` (e.g. a "Crestron Components" extension) would otherwise own the file's language and disable this extension's `@` outline, hover, and completion. See [Troubleshooting](#troubleshooting) if those features don't appear.
- After editing files in `src/`, re-run the compile (`npm run compile`, or rely on the F5 pre-launch task) and reload the dev host (**Developer: Reload Window**) to pick up changes.

### Copy to extensions folder
```powershell
Copy-Item -Recurse "VSCodeSIMPLPlus" "$env:USERPROFILE\.vscode\extensions\vscode-simplplus-0.1.0"
```
Then restart VS Code.

---

## Configuration

Open VS Code settings (`Ctrl+,`) and search for **SIMPL+**:

| Setting | Default | Description |
|---------|---------|-------------|
| `simplplus.compilerPath` | _(blank — auto-detect)_ | Path to SPlusCC.exe. Leave blank to auto-detect from common install locations and the registry. |
| `simplplus.compileTarget` | `series3` | Target series: `series2`, `series3`, or `series2 series3` |
| `simplplus.compileOnSave` | `false` | Auto-compile on save |

---

## File Support

| Extension | Description |
|-----------|-------------|
| `.usp` | SIMPL+ source module |
| `.ush` | SIMPL+ header / include file |

---

## Compiler Test Suite (separate)

The SIMPL+ compiler test suite (253 generated `.usp` files plus the generator and
batch runner) is **not part of this extension** — it's a standalone testing effort kept
in a sibling folder: **`../SIMPLPlusTests`** (`C:\ClaudeProjects\SIMPLPlusTests`).

It consumes this plugin's `scripts/function-db.json` to generate per-function tests.
See that folder's own README for how to run/regenerate it.

---

## Project Structure

```
VSCodeSIMPLPlus/
├── src/
│   ├── extension.ts          Extension entry point + compiler integration
│   ├── functionDb.ts         Loads function-db.json; hover/doc rendering
│   ├── providers.ts          Hover, completion, signature help, go-to-definition, outline
│   ├── symbols.ts            Scans user-declared symbols (I/O, vars, functions, …)
│   └── compilerPath.ts       Auto-detects SPlusCC.exe (settings → install dirs → registry)
├── syntaxes/
│   └── simplplus.tmLanguage.json   TextMate grammar
├── snippets/
│   └── simplplus.json        Code snippets
├── scripts/
│   ├── parse-help.py         Parses Simpl+lr.chm HTML → function-db.json
│   └── function-db.json      Parsed database of 305 SIMPL+ functions (runtime asset)
├── sample/
│   └── sample.usp            Example SIMPL+ module
├── language-configuration.json
├── package.json
└── tsconfig.json
```

---

## Troubleshooting

### `@` (Go to Symbol) / Outline shows nothing, hover & completion don't fire
The language features only run when VS Code identifies the file as the `simplplus` language. The usual cause is **another installed extension claiming `.usp`** (e.g. a separate "Crestron Components" extension). When two extensions register `.usp`, VS Code assigns the file to only one language ID — and the status bar may still *display* "SIMPL+" even though it's the other extension's language.

- **While developing:** the included launch config (`.vscode/launch.json`) passes `--disable-extensions`, so the Extension Development Host runs **only** this extension and owns `.usp`. Press `F5` and the `@` outline, hover, etc. will work.
- **When installed normally:** disable or uninstall the conflicting extension so this one owns `.usp`, or change the file association (`Ctrl+Shift+P` → **Change Language Mode** → **Configure File Association for '.usp'**).
- **To verify which language owns the file:** open the **SIMPL+** Output panel (click the **✓ SIMPL+** status-bar badge). Pressing `@` logs a line showing the file's actual `languageId` and the symbols found.

---

## Known Limitations

- **Line numbers in errors** may be relative to the compiled function body rather than the absolute file line. Error messages and file links are always accurate.
- **Wrapped multi-line declarations** aren't picked up by the outline / go-to-definition. An I/O or variable declaration whose terminating `;` is on a later line than the type keyword (e.g. `DIGITAL_INPUT a,` then more names below, `;` several lines down) is skipped by the symbol scanner. Functions, constants, and single-line declarations are unaffected.
- **Event handlers** (`PUSH`, `RELEASE`, `CHANGE`, `EVENT`, `THREADSAFE`) are not listed in the `@` outline.

---

## License

Copyright © Crestron Electronics, Inc. All rights reserved.
