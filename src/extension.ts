import * as vscode from 'vscode';
import * as cp from 'child_process';
import * as path from 'path';
import * as fs from 'fs';

const DIAG_SOURCE = 'SIMPL+';
// Matches: [filepath] Error 1001 (Line 9) - message
const ERROR_RE = /^\[(.+?)\]\s+(Error|Warning)\s+\d+\s+\(Line\s+(\d+)\)\s+-\s+(.+)$/;

let diagnostics: vscode.DiagnosticCollection;
let outputChannel: vscode.OutputChannel;

export function activate(context: vscode.ExtensionContext) {
    diagnostics    = vscode.languages.createDiagnosticCollection(DIAG_SOURCE);
    outputChannel  = vscode.window.createOutputChannel('SIMPL+');

    context.subscriptions.push(
        diagnostics,
        outputChannel,
        vscode.commands.registerCommand('simplplus.compile',    compileCurrentFile),
        vscode.commands.registerCommand('simplplus.compileAll', compileAllFiles),
        vscode.commands.registerCommand('simplplus.runTests',   runTestSuite),
    );
}

export function deactivate() {
    diagnostics.dispose();
    outputChannel.dispose();
}

// ---- command handlers -------------------------------------------------------

async function compileCurrentFile() {
    const editor = vscode.window.activeTextEditor;
    if (!editor || editor.document.languageId !== 'simplplus') {
        vscode.window.showWarningMessage('No SIMPL+ (.usp) file is active.');
        return;
    }
    await editor.document.save();
    await runCompiler([editor.document.fileName]);
}

async function compileAllFiles() {
    const uris = await vscode.workspace.findFiles('**/*.usp', '**/node_modules/**');
    if (uris.length === 0) {
        vscode.window.showInformationMessage('No .usp files found in the workspace.');
        return;
    }
    await runCompiler(uris.map(u => u.fsPath));
}

async function runTestSuite() {
    const wsFolder = vscode.workspace.workspaceFolders?.[0]?.uri.fsPath;
    if (!wsFolder) {
        vscode.window.showWarningMessage('Open a workspace folder first.');
        return;
    }
    const testDir = path.join(wsFolder, 'test-suite');
    if (!fs.existsSync(testDir)) {
        vscode.window.showWarningMessage(`test-suite folder not found: ${testDir}`);
        return;
    }
    const files: string[] = [];
    collectUsp(testDir, files);
    if (files.length === 0) {
        vscode.window.showWarningMessage('No .usp files found in test-suite/.');
        return;
    }
    vscode.window.showInformationMessage(`Running SIMPL+ test suite: ${files.length} files…`);
    await runCompiler(files, true);
}

// ---- core compiler invocation -----------------------------------------------

async function runCompiler(files: string[], isBatch = false) {
    const config      = vscode.workspace.getConfiguration('simplplus');
    const compilerPath: string = config.get('compilerPath', defaultCompilerPath());
    const target: string       = config.get('compileTarget', 'series3');

    if (!fs.existsSync(compilerPath)) {
        const pick = await vscode.window.showErrorMessage(
            `SIMPL+ compiler not found at:\n${compilerPath}`,
            'Open Settings'
        );
        if (pick) { vscode.commands.executeCommand('workbench.action.openSettings', 'simplplus.compilerPath'); }
        return;
    }

    diagnostics.clear();
    outputChannel.clear();
    outputChannel.show(true);

    const label = isBatch
        ? `SIMPL+ test suite (${files.length} files)`
        : `Compiling ${path.basename(files[0])}`;

    await vscode.window.withProgress(
        { location: vscode.ProgressLocation.Notification, title: label, cancellable: false },
        async () => runBatch(compilerPath, files, target)
    );
}

async function runBatch(compilerPath: string, allFiles: string[], target: string) {
    // SPlusCC supports multiple files in one call; batch to avoid command-line limits
    const BATCH = 50;
    const diagMap = new Map<string, vscode.Diagnostic[]>();
    let totalErrors = 0;
    let totalWarnings = 0;

    for (let i = 0; i < allFiles.length; i += BATCH) {
        const chunk = allFiles.slice(i, i + BATCH);
        const { errors, warnings } = await spawnCompiler(compilerPath, chunk, target, diagMap);
        totalErrors   += errors;
        totalWarnings += warnings;
    }

    // Push all diagnostics at once
    for (const [filePath, diags] of diagMap) {
        diagnostics.set(vscode.Uri.file(filePath), diags);
    }

    const msg = totalErrors === 0
        ? `SIMPL+ compilation successful — ${allFiles.length} file(s)${totalWarnings ? `, ${totalWarnings} warning(s)` : ''}`
        : `SIMPL+ failed — ${totalErrors} error(s) in ${allFiles.length} file(s)`;

    if (totalErrors === 0) {
        vscode.window.showInformationMessage(msg);
    } else {
        vscode.window.showErrorMessage(msg, 'Show Problems').then(pick => {
            if (pick) { vscode.commands.executeCommand('workbench.actions.view.problems'); }
        });
    }
}

function spawnCompiler(
    compilerPath: string,
    files: string[],
    target: string,
    diagMap: Map<string, vscode.Diagnostic[]>
): Promise<{ errors: number; warnings: number }> {
    return new Promise(resolve => {
        const args = ['\\build', ...files, '\\target', target];
        let errors = 0;
        let warnings = 0;
        let buffer = '';

        outputChannel.appendLine(`> ${path.basename(compilerPath)} ${args.slice(0, 3).join(' ')} … (${files.length} file(s))`);

        const proc = cp.spawn(compilerPath, args, { windowsHide: true });

        const processLine = (line: string) => {
            outputChannel.appendLine(line);
            const m = line.match(ERROR_RE);
            if (!m) { return; }

            const [, filePath, severity, lineStr, message] = m;
            const lineNo  = Math.max(0, parseInt(lineStr, 10) - 1);
            const range   = new vscode.Range(lineNo, 0, lineNo, Number.MAX_SAFE_INTEGER);
            const sev     = severity === 'Error'
                ? vscode.DiagnosticSeverity.Error
                : vscode.DiagnosticSeverity.Warning;
            const diag    = new vscode.Diagnostic(range, message.trim(), sev);
            diag.source   = DIAG_SOURCE;

            const key  = filePath.trim();
            const list = diagMap.get(key) ?? [];
            list.push(diag);
            diagMap.set(key, list);

            if (sev === vscode.DiagnosticSeverity.Error)   { errors++; }
            else                                           { warnings++; }
        };

        const feedData = (data: Buffer) => {
            buffer += data.toString();
            const lines = buffer.split('\n');
            buffer = lines.pop() ?? '';
            lines.forEach(processLine);
        };

        proc.stdout?.on('data', feedData);
        proc.stderr?.on('data', feedData);

        proc.on('close', () => {
            if (buffer.trim()) { processLine(buffer); }
            resolve({ errors, warnings });
        });

        proc.on('error', err => {
            outputChannel.appendLine(`ERROR spawning compiler: ${err.message}`);
            resolve({ errors: 1, warnings: 0 });
        });
    });
}

// ---- helpers ----------------------------------------------------------------

function defaultCompilerPath(): string {
    return 'C:\\Program Files (x86)\\Crestron\\Simpl\\SPlusCC.exe';
}

function collectUsp(dir: string, results: string[]) {
    for (const entry of fs.readdirSync(dir, { withFileTypes: true })) {
        const full = path.join(dir, entry.name);
        if (entry.isDirectory()) {
            collectUsp(full, results);
        } else if (entry.name.toLowerCase().endsWith('.usp')) {
            results.push(full);
        }
    }
}
