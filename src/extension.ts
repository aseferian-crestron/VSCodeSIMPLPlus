import * as vscode from 'vscode';
import * as cp from 'child_process';
import * as path from 'path';
import * as fs from 'fs';
import { loadFunctionDb } from './functionDb';
import { registerLanguageFeatures } from './providers';
import { resolveCompilerPath, promptForCompiler } from './compilerPath';

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
    );

    // Language intelligence backed by the CHM-derived function database.
    loadFunctionDb(context.extensionPath);
    registerLanguageFeatures(context);
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

// ---- core compiler invocation -----------------------------------------------

async function runCompiler(files: string[]) {
    const config            = vscode.workspace.getConfiguration('simplplus');
    const target: string    = config.get('compileTarget', 'series3');

    let compilerPath = await resolveCompilerPath();
    if (!compilerPath || !fs.existsSync(compilerPath)) {
        compilerPath = await promptForCompiler(compilerPath);
        if (!compilerPath || !fs.existsSync(compilerPath)) { return; }
    }

    diagnostics.clear();
    outputChannel.clear();
    outputChannel.show(true);

    const label = files.length === 1
        ? `Compiling ${path.basename(files[0])}`
        : `Compiling ${files.length} SIMPL+ files`;

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

