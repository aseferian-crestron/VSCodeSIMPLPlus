import * as vscode from 'vscode';

/** A symbol declared by the user within a SIMPL+ document. */
export interface UserSymbol {
    name: string;
    detail: string;                  // the declaring keyword, e.g. "DIGITAL_INPUT"
    kind: vscode.SymbolKind;
    nameRange: vscode.Range;         // range of the identifier itself (jump target)
    fullRange: vscode.Range;         // range of the whole declaration line
}

// Declaration keywords grouped by purpose. Longest-first within each group so the
// big alternation never matches a prefix of a longer keyword.
const IO_TYPES = [
    'DIGITAL_INPUT', 'DIGITAL_OUTPUT', 'ANALOG_INPUT', 'ANALOG_OUTPUT',
    'STRING_INPUT', 'STRING_OUTPUT', 'BUFFER_INPUT',
];
const PARAM_TYPES = [
    'SIGNED_LONG_INTEGER_PARAMETER', 'LONG_INTEGER_PARAMETER',
    'SIGNED_INTEGER_PARAMETER', 'INTEGER_PARAMETER', 'STRING_PARAMETER',
];
const VAR_TYPES = [
    'SIGNED_LONG_INTEGER', 'LONG_INTEGER', 'SIGNED_INTEGER', 'INTEGER', 'STRING', 'REAL',
];

const KIND_BY_TYPE = new Map<string, vscode.SymbolKind>();
for (const t of IO_TYPES)    { KIND_BY_TYPE.set(t, vscode.SymbolKind.Field); }
for (const t of PARAM_TYPES) { KIND_BY_TYPE.set(t, vscode.SymbolKind.Property); }
for (const t of VAR_TYPES)   { KIND_BY_TYPE.set(t, vscode.SymbolKind.Variable); }

// Order matters: parameters/IO before plain var types (they share the INTEGER/STRING roots).
const ALL_DECL_TYPES = [...IO_TYPES, ...PARAM_TYPES, ...VAR_TYPES];

const DECL_RE   = new RegExp(`^(\\s*(${ALL_DECL_TYPES.join('|')})\\b\\s+)([^;{]+);`, 'i');
const FUNC_RE   = /^(\s*(?:CALLBACK\s+)?\w*FUNCTION\s+)([A-Za-z_]\w*)\s*\(/i;
const STRUCT_RE = /^(\s*STRUCTURE\s+)([A-Za-z_]\w*)/i;
const CONST_RE  = /^(\s*#DEFINE_CONSTANT\s+)([A-Za-z_]\w*)/i;
const IDENT_RE  = /[A-Za-z_]\w*/g;

// Generic `Type names;` line — only treated as a declaration when the leading
// token is a user-declared structure type (see knownStructs).
const USER_DECL_RE = /^(\s*([A-Za-z_]\w*)\b\s+)([^;{]+);/;

/** Scan a document and return every user-declared symbol. */
export function scanSymbols(doc: vscode.TextDocument): UserSymbol[] {
    const symbols: UserSymbol[] = [];
    const knownStructs = new Set<string>();   // lowercased structure names, for struct-typed vars
    let inBlockComment = false;

    for (let lineNo = 0; lineNo < doc.lineCount; lineNo++) {
        const raw = doc.lineAt(lineNo).text;
        const { masked, inBlock } = maskComments(raw, inBlockComment);
        inBlockComment = inBlock;
        if (!masked.trim()) { continue; }

        const fullRange = doc.lineAt(lineNo).range;

        // Function definitions.
        const fm = masked.match(FUNC_RE);
        if (fm) {
            push(symbols, fm[2], 'FUNCTION', vscode.SymbolKind.Function, lineNo, fm[1].length, fullRange);
            continue;
        }
        // Structure definitions.
        const sm = masked.match(STRUCT_RE);
        if (sm) {
            knownStructs.add(sm[2].toLowerCase());
            push(symbols, sm[2], 'STRUCTURE', vscode.SymbolKind.Struct, lineNo, sm[1].length, fullRange);
            continue;
        }
        // #DEFINE_CONSTANT.
        const cm = masked.match(CONST_RE);
        if (cm) {
            push(symbols, cm[2], '#DEFINE_CONSTANT', vscode.SymbolKind.Constant, lineNo, cm[1].length, fullRange);
            continue;
        }
        // I/O, parameter and variable declarations (possibly comma-separated).
        const dm = masked.match(DECL_RE);
        if (dm) {
            collectNames(symbols, dm[3], dm[2].toUpperCase(),
                         KIND_BY_TYPE.get(dm[2].toUpperCase()) ?? vscode.SymbolKind.Variable,
                         lineNo, dm[1].length, fullRange);
            continue;
        }
        // Variables declared with a user structure type, e.g. `DeviceState gDevice;`.
        const um = masked.match(USER_DECL_RE);
        if (um && knownStructs.has(um[2].toLowerCase())) {
            collectNames(symbols, um[3], um[2], vscode.SymbolKind.Variable,
                         lineNo, um[1].length, fullRange);
        }
    }
    return symbols;
}

/** Capture each comma-separated identifier in a declaration's names list. */
function collectNames(
    out: UserSymbol[], namesList: string, detail: string, kind: vscode.SymbolKind,
    lineNo: number, namesCol: number, fullRange: vscode.Range,
) {
    // Blank out array sizes / initializers so bracketed identifiers aren't captured.
    const namesPart = namesList.replace(/\[[^\]]*\]/g, m => ' '.repeat(m.length))
                               .replace(/=[^,]*/g, m => ' '.repeat(m.length));
    IDENT_RE.lastIndex = 0;
    let m: RegExpExecArray | null;
    while ((m = IDENT_RE.exec(namesPart)) !== null) {
        push(out, m[0], detail, kind, lineNo, namesCol + m.index, fullRange);
    }
}

function push(
    out: UserSymbol[], name: string, detail: string, kind: vscode.SymbolKind,
    line: number, col: number, fullRange: vscode.Range,
) {
    const nameRange = new vscode.Range(line, col, line, col + name.length);
    out.push({ name, detail, kind, nameRange, fullRange });
}

/**
 * Replace comment and string content with spaces (preserving column positions) so
 * declaration regexes never match inside comments or string literals.
 */
function maskComments(line: string, inBlock: boolean): { masked: string; inBlock: boolean } {
    let out = '';
    let i = 0;
    let block = inBlock;
    let inString = false;

    while (i < line.length) {
        if (block) {
            const end = line.indexOf('*/', i);
            if (end === -1) { out += ' '.repeat(line.length - i); i = line.length; }
            else            { out += ' '.repeat(end + 2 - i); i = end + 2; block = false; }
            continue;
        }
        if (inString) {
            out += ' ';
            if (line[i] === '"') { inString = false; }
            i++;
            continue;
        }
        if (line[i] === '/' && line[i + 1] === '/') {           // line comment
            out += ' '.repeat(line.length - i);
            break;
        }
        if (line[i] === '/' && line[i + 1] === '*') {           // block comment start
            block = true;
            out += '  ';
            i += 2;
            continue;
        }
        if (line[i] === '"') {                                  // string start
            inString = true;
            out += ' ';
            i++;
            continue;
        }
        out += line[i];
        i++;
    }
    return { masked: out, inBlock: block };
}
