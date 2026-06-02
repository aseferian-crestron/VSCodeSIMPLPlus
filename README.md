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
  - Default path: `C:\Program Files (x86)\Crestron\Simpl\SPlusCC.exe`

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
| `simplplus.compilerPath` | `C:\Program Files (x86)\Crestron\Simpl\SPlusCC.exe` | Path to SPlusCC.exe |
| `simplplus.compileTarget` | `series3` | Target series: `series2`, `series3`, or `series2 series3` |
| `simplplus.compileOnSave` | `false` | Auto-compile on save |

---

## File Support

| Extension | Description |
|-----------|-------------|
| `.usp` | SIMPL+ source module |
| `.ush` | SIMPL+ header / include file |

---

## Test Suite

The `test-suite/` folder contains **253 `.usp` files** — one per SIMPL+ built-in function and language construct — automatically generated from the `Simpl+lr.chm` language reference and verified to compile without errors against a Series 3 target.

Tests are organized by category:

```
test-suite/
├── Array_Operations/
├── Bit_and_Byte_Functions/
├── Branching_and_Decision_Constructs/
├── Compiler_Directives/
├── Data_Conversion_Functions/
├── Declarations/
├── Direct_Socket_Access/
├── Encoding/
├── Events/
├── Exception_Handling/
├── File_Functions/
├── Looping_Constructs/
├── Mathematical_Functions/
├── Ramping_Functions/
├── Random_Number_Functions/
├── String_Formatting_and_Printing_Functions/
├── String_Parsing_and_Manipulation_Functions/
├── System_Control/
├── System_Interfacing/
├── Time_and_Date_Functions/
└── Wait_Events/
```

### Running the test suite

**From VS Code:** Command Palette → `SIMPL+: Run Test Suite`

**From PowerShell:**
```powershell
.\scripts\test-compile.ps1 -Path test-suite -Target series3
```

### Regenerating the test suite
If you have a newer version of SIMPL Windows installed:
```powershell
# 1. Extract the CHM language reference
& "C:\Program Files\7-Zip\7z.exe" x "C:\Program Files (x86)\Crestron\Simpl\Simpl+lr.chm" -o"help-extracted" -y

# 2. Parse all function definitions
python scripts\parse-help.py

# 3. Generate test files
python scripts\generate-tests.py
```

---

## Project Structure

```
VSCodeSIMPLPlus/
├── src/
│   └── extension.ts          TypeScript extension entry point
├── syntaxes/
│   └── simplplus.tmLanguage.json   TextMate grammar
├── snippets/
│   └── simplplus.json        Code snippets
├── scripts/
│   ├── parse-help.py         Parses Simpl+lr.chm HTML → function-db.json
│   ├── generate-tests.py     Generates test .usp files from function-db.json
│   ├── test-compile.ps1      Batch test runner using SPlusCC.exe
│   └── function-db.json      Parsed database of 305 SIMPL+ functions
├── test-suite/               253 verified-compiling .usp test files
├── sample/
│   └── sample.usp            Example SIMPL+ module
├── language-configuration.json
├── package.json
└── tsconfig.json
```

---

## Known Limitations

- **Line numbers in errors** may be relative to the compiled function body rather than the absolute file line. Error messages and file links are always accurate.
- The following categories are not included in the test suite as they require specific hardware or installed libraries: CIP/Cresnet signal routing functions, `#CRESTRON_LIBRARY` / `#USER_SIMPLSHARP_LIBRARY` directives, OEM join directives (Series-2 only), and GatherAsync callback patterns.

---

## License

Copyright © Crestron Electronics, Inc. All rights reserved.
