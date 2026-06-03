import * as vscode from 'vscode';
import * as path from 'path';
import * as fs from 'fs';

/** One SIMPL+ function / keyword entry parsed from the CHM language reference. */
export interface SimplFunction {
    name: string;
    category: string;
    syntax: string;
    example: string;
    description: string;
    return_value: string;
    file: string;
}

// Real SIMPL+ symbols are single identifiers; many CHM "names" are doc-section
// titles ("Find Next", "Examples", "Arrays") — filter those out.
const IDENTIFIER_RE = /^[A-Za-z_][A-Za-z0-9_]*$/;

let byName: Map<string, SimplFunction> = new Map();
let allFns: SimplFunction[] = [];

/** Load and index the bundled function database. Safe to call once at activation. */
export function loadFunctionDb(extensionPath: string): void {
    const dbPath = path.join(extensionPath, 'scripts', 'function-db.json');
    byName = new Map();
    allFns = [];
    try {
        const raw = JSON.parse(fs.readFileSync(dbPath, 'utf-8')) as SimplFunction[];
        for (const fn of raw) {
            if (!fn.name || !IDENTIFIER_RE.test(fn.name)) { continue; }
            if (!fn.syntax && !fn.description) { continue; }
            // First entry wins on duplicate names (case-insensitive).
            const key = fn.name.toLowerCase();
            if (!byName.has(key)) {
                byName.set(key, fn);
                allFns.push(fn);
            }
        }
    } catch (err) {
        // Leave the maps empty — language features degrade gracefully to nothing.
        console.error(`SIMPL+: failed to load function database from ${dbPath}:`, err);
    }
}

/** Case-insensitive lookup of a single function/keyword by name. */
export function lookup(name: string): SimplFunction | undefined {
    return byName.get(name.toLowerCase());
}

/** All indexed functions (already filtered to real identifiers). */
export function allFunctions(): SimplFunction[] {
    return allFns;
}

/** Build a rich hover/documentation block for a function. */
export function buildDocs(fn: SimplFunction): vscode.MarkdownString {
    const md = new vscode.MarkdownString();
    md.supportHtml = false;

    const heading = fn.category ? `**${fn.name}**  —  *${fn.category}*` : `**${fn.name}**`;
    md.appendMarkdown(heading + '\n\n');

    if (fn.description) {
        md.appendMarkdown(fn.description.trim() + '\n\n');
    }
    if (fn.syntax) {
        md.appendMarkdown('**Syntax**\n');
        md.appendCodeblock(fn.syntax.trim(), 'simplplus');
    }
    if (fn.return_value) {
        md.appendMarkdown(`\n**Returns:** ${fn.return_value.trim()}\n`);
    }
    if (fn.example) {
        md.appendMarkdown('\n**Example**\n');
        md.appendCodeblock(fn.example.trim(), 'simplplus');
    }
    return md;
}
