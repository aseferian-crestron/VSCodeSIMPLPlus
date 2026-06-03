import * as vscode from 'vscode';
import * as cp from 'child_process';
import * as fs from 'fs';
import * as path from 'path';

const EXE = 'SPlusCC.exe';
let cached: string | undefined;

/** Forget any auto-detected path (call after the user changes the setting). */
export function clearCachedCompilerPath(): void {
    cached = undefined;
}

/**
 * Resolve the SIMPL+ compiler (SPlusCC.exe). SIMPL Windows can be installed to any
 * directory, so we try, in order: the user setting, common install roots, then the
 * Windows registry (install-location-agnostic). Returns undefined if not found.
 */
export async function resolveCompilerPath(): Promise<string | undefined> {
    // 1. Explicit user setting always wins (existence is validated by the caller).
    const configured = (vscode.workspace.getConfiguration('simplplus').get<string>('compilerPath') || '').trim();
    if (configured) { return configured; }

    if (cached && fs.existsSync(cached)) { return cached; }

    // 2. Common install roots.
    for (const base of candidateBases()) {
        const p = path.join(base, 'Crestron', 'Simpl', EXE);
        if (fs.existsSync(p)) { cached = p; return p; }
    }

    // 3. Registry — wherever the user installed SIMPL Windows.
    const fromReg = findInRegistry();
    if (fromReg) { cached = fromReg; return fromReg; }

    return undefined;
}

function candidateBases(): string[] {
    const bases = [
        process.env['ProgramFiles(x86)'],
        process.env['ProgramW6432'],
        process.env['ProgramFiles'],
        'C:\\',
    ].filter(Boolean) as string[];
    return [...new Set(bases)];
}

/** Look up the SIMPL Windows install location from the uninstall registry. */
function findInRegistry(): string | undefined {
    if (process.platform !== 'win32') { return undefined; }
    const roots = [
        'HKLM\\SOFTWARE\\WOW6432Node\\Microsoft\\Windows\\CurrentVersion\\Uninstall',
        'HKLM\\SOFTWARE\\Microsoft\\Windows\\CurrentVersion\\Uninstall',
        'HKCU\\SOFTWARE\\Microsoft\\Windows\\CurrentVersion\\Uninstall',
    ];
    for (const root of roots) {
        for (const subkey of regSearchSubkeys(root, 'SIMPL Window')) {
            const loc = regReadValue(subkey, 'InstallLocation') ?? regReadValue(subkey, 'Inno Setup: App Path');
            if (loc) {
                const exe = path.join(loc.trim(), EXE);
                if (fs.existsSync(exe)) { return exe; }
            }
        }
    }
    return undefined;
}

/** Subkey paths under `root` whose value data matches `needle` (e.g. a DisplayName). */
function regSearchSubkeys(root: string, needle: string): string[] {
    try {
        const out = cp.execFileSync('reg', ['query', root, '/s', '/f', needle, '/d'],
            { encoding: 'utf-8', windowsHide: true, timeout: 8000 });
        return out.split(/\r?\n/).map(l => l.trim()).filter(l => /^HKEY_/.test(l));
    } catch {
        return [];
    }
}

/** Read a single REG_SZ value from a registry key. */
function regReadValue(key: string, value: string): string | undefined {
    try {
        const out = cp.execFileSync('reg', ['query', key, '/v', value],
            { encoding: 'utf-8', windowsHide: true, timeout: 8000 });
        const esc = value.replace(/[.*+?^${}()|[\]\\]/g, '\\$&');
        const re  = new RegExp(`${esc}\\s+REG_\\w+\\s+(.+)$`);
        for (const line of out.split(/\r?\n/)) {
            const m = line.match(re);
            if (m) { return m[1].trim(); }
        }
    } catch {
        // value missing — fall through
    }
    return undefined;
}

/**
 * Show the "compiler not found" error and let the user locate SPlusCC.exe. On success
 * the chosen path is saved to settings and returned; otherwise undefined.
 */
export async function promptForCompiler(triedPath: string | undefined): Promise<string | undefined> {
    const detail = triedPath
        ? `SIMPL+ compiler not found at:\n${triedPath}`
        : 'Could not locate the SIMPL+ compiler (SPlusCC.exe). Is SIMPL Windows installed?';

    const pick = await vscode.window.showErrorMessage(detail, 'Locate SPlusCC.exe…', 'Open Settings');
    if (pick === 'Open Settings') {
        vscode.commands.executeCommand('workbench.action.openSettings', 'simplplus.compilerPath');
        return undefined;
    }
    if (pick !== 'Locate SPlusCC.exe…') { return undefined; }

    const uris = await vscode.window.showOpenDialog({
        canSelectMany: false,
        title: 'Select the SIMPL+ compiler (SPlusCC.exe)',
        filters: process.platform === 'win32' ? { 'SIMPL+ Compiler': ['exe'] } : undefined,
    });
    if (!uris || uris.length === 0) { return undefined; }

    const chosen = uris[0].fsPath;
    await vscode.workspace.getConfiguration('simplplus')
        .update('compilerPath', chosen, vscode.ConfigurationTarget.Global);
    clearCachedCompilerPath();
    return chosen;
}
