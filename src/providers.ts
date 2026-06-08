import * as vscode from 'vscode';
import { allFunctions, lookup, buildDocs, SimplFunction } from './functionDb';
import { scanSymbols, UserSymbol } from './symbols';

const SELECTOR: vscode.DocumentSelector = { language: 'simplplus' };

let log: vscode.OutputChannel | undefined;

/** Register all language-feature providers. */
export function registerLanguageFeatures(context: vscode.ExtensionContext, channel?: vscode.OutputChannel) {
    log = channel;
    context.subscriptions.push(
        vscode.languages.registerHoverProvider(SELECTOR, new SimplHoverProvider()),
        vscode.languages.registerCompletionItemProvider(SELECTOR, new SimplCompletionProvider()),
        vscode.languages.registerSignatureHelpProvider(SELECTOR, new SimplSignatureProvider(), '(', ','),
        vscode.languages.registerDefinitionProvider(SELECTOR, new SimplDefinitionProvider()),
        vscode.languages.registerDocumentSymbolProvider(SELECTOR, new SimplDocumentSymbolProvider()),
    );
}

// ---- hover ------------------------------------------------------------------

class SimplHoverProvider implements vscode.HoverProvider {
    provideHover(doc: vscode.TextDocument, pos: vscode.Position): vscode.ProviderResult<vscode.Hover> {
        const range = doc.getWordRangeAtPosition(pos);
        if (!range) { return; }
        const fn = lookup(doc.getText(range));
        if (!fn) { return; }
        return new vscode.Hover(buildDocs(fn), range);
    }
}

// ---- completion -------------------------------------------------------------

class SimplCompletionProvider implements vscode.CompletionItemProvider {
    provideCompletionItems(doc: vscode.TextDocument): vscode.ProviderResult<vscode.CompletionItem[]> {
        const items = allFunctions().map(fn => {
            const item = new vscode.CompletionItem(fn.name, kindFor(fn));
            item.detail = fn.category || 'SIMPL+';
            item.documentation = buildDocs(fn);
            // If the syntax shows a call with parentheses, insert a call snippet.
            if (/^\s*\w+\s*\(/.test(fn.syntax)) {
                item.insertText = new vscode.SnippetString(`${fn.name}($0)`);
            }
            return item;
        });

        // Add the user's own declarations (variables, constants, I/O, params, functions,
        // structures) found in the current file. Dedupe by name — scanSymbols may report
        // the same identifier more than once (e.g. comma-separated declarations).
        const seen = new Set<string>();
        for (const s of scanSymbols(doc)) {
            const key = s.name.toLowerCase();
            if (seen.has(key)) { continue; }
            seen.add(key);
            const item = new vscode.CompletionItem(s.name, completionKindFor(s.kind));
            item.detail = s.detail;
            items.push(item);
        }
        return items;
    }
}

/** Map an outline SymbolKind to the matching CompletionItemKind. */
function completionKindFor(kind: vscode.SymbolKind): vscode.CompletionItemKind {
    switch (kind) {
        case vscode.SymbolKind.Field:    return vscode.CompletionItemKind.Field;
        case vscode.SymbolKind.Property: return vscode.CompletionItemKind.Property;
        case vscode.SymbolKind.Function: return vscode.CompletionItemKind.Function;
        case vscode.SymbolKind.Struct:   return vscode.CompletionItemKind.Struct;
        case vscode.SymbolKind.Constant: return vscode.CompletionItemKind.Constant;
        default:                         return vscode.CompletionItemKind.Variable;
    }
}

function kindFor(fn: SimplFunction): vscode.CompletionItemKind {
    const cat = fn.category.toLowerCase();
    if (cat.includes('declaration')) { return vscode.CompletionItemKind.Keyword; }
    if (cat.includes('directive') || cat.includes('compiler')) { return vscode.CompletionItemKind.Keyword; }
    if (cat.includes('event')) { return vscode.CompletionItemKind.Event; }
    if (cat.includes('looping') || cat.includes('branching') || cat.includes('decision')) {
        return vscode.CompletionItemKind.Keyword;
    }
    return vscode.CompletionItemKind.Function;
}

// ---- signature help ---------------------------------------------------------

class SimplSignatureProvider implements vscode.SignatureHelpProvider {
    provideSignatureHelp(
        doc: vscode.TextDocument,
        pos: vscode.Position,
    ): vscode.ProviderResult<vscode.SignatureHelp> {
        const fnName = functionCallName(doc, pos);
        if (!fnName) { return; }
        const fn = lookup(fnName);
        if (!fn || !fn.syntax) { return; }

        const help = new vscode.SignatureHelp();
        // Each line of the syntax block is a separate overload.
        help.signatures = fn.syntax.split('\n')
            .map(s => s.trim())
            .filter(Boolean)
            .map(line => {
                const sig = new vscode.SignatureInformation(line);
                if (fn.description) {
                    sig.documentation = new vscode.MarkdownString(fn.description.trim());
                }
                sig.parameters = parseParams(line).map(p => new vscode.ParameterInformation(p));
                return sig;
            });
        help.activeSignature = 0;
        help.activeParameter = Math.min(commaDepth(doc, pos), Math.max(0, signatureParamCount(help) - 1));
        return help;
    }
}

/** Walk back from the cursor to find the function name owning the open `(`. */
function functionCallName(doc: vscode.TextDocument, pos: vscode.Position): string | undefined {
    const text = doc.getText(new vscode.Range(new vscode.Position(0, 0), pos));
    let depth = 0;
    for (let i = text.length - 1; i >= 0; i--) {
        const ch = text[i];
        if (ch === ')') { depth++; }
        else if (ch === '(') {
            if (depth === 0) {
                const before = text.slice(0, i);
                const m = before.match(/([A-Za-z_]\w*)\s*$/);
                return m ? m[1] : undefined;
            }
            depth--;
        }
    }
    return undefined;
}

/** Count argument-separating commas at the current call depth (the active parameter index). */
function commaDepth(doc: vscode.TextDocument, pos: vscode.Position): number {
    const text = doc.getText(new vscode.Range(new vscode.Position(0, 0), pos));
    let depth = 0;
    let commas = 0;
    for (let i = text.length - 1; i >= 0; i--) {
        const ch = text[i];
        if (ch === ')') { depth++; }
        else if (ch === '(') {
            if (depth === 0) { break; }
            depth--;
        } else if (ch === ',' && depth === 0) {
            commas++;
        }
    }
    return commas;
}

function signatureParamCount(help: vscode.SignatureHelp): number {
    return help.signatures[0]?.parameters.length ?? 0;
}

/** Extract parameter names from a `Func(a, b, c)` syntax line. */
function parseParams(syntaxLine: string): string[] {
    const m = syntaxLine.match(/\(([^)]*)\)/);
    if (!m || !m[1].trim()) { return []; }
    return m[1].split(',').map(s => s.trim()).filter(Boolean);
}

// ---- go-to-definition (user-declared symbols) -------------------------------

class SimplDefinitionProvider implements vscode.DefinitionProvider {
    provideDefinition(
        doc: vscode.TextDocument,
        pos: vscode.Position,
    ): vscode.ProviderResult<vscode.Definition> {
        const range = doc.getWordRangeAtPosition(pos);
        if (!range) { return; }
        const word = doc.getText(range).toLowerCase();

        const matches = scanSymbols(doc).filter(s => s.name.toLowerCase() === word);
        if (matches.length === 0) { return; }
        return matches.map(s => new vscode.Location(doc.uri, s.nameRange));
    }
}

// ---- document symbols (outline / breadcrumbs) -------------------------------

class SimplDocumentSymbolProvider implements vscode.DocumentSymbolProvider {
    provideDocumentSymbols(doc: vscode.TextDocument): vscode.ProviderResult<vscode.DocumentSymbol[]> {
        try {
            const found = scanSymbols(doc);
            log?.appendLine(`[SIMPL+] @ symbol scan: lang=${doc.languageId}, file=${doc.uri.fsPath}, found ${found.length} symbols${found.length ? ': ' + found.map(s => s.name).join(', ') : ''}`);
            return found.map((s: UserSymbol) =>
                new vscode.DocumentSymbol(s.name, s.detail, s.kind, s.fullRange, s.nameRange));
        } catch (err) {
            log?.appendLine(`[SIMPL+] @ symbol scan FAILED: ${err}`);
            return [];
        }
    }
}
