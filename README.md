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
3. Open the folder in VS Code and press `F5` — a new Extension Development Host window opens with the extension active

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

## Known Limitations

- **Line numbers in errors** may be relative to the compiled function body rather than the absolute file line. Error messages and file links are always accurate.

---

## License

Copyright © Crestron Electronics, Inc. All rights reserved.
