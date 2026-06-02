#!/usr/bin/env python3
"""
generate-tests.py  —  Generate one .usp test file per SIMPL+ function/keyword
from function-db.json, using help-file example code where available.

Usage:
    python generate-tests.py [--db <path>] [--out-dir <path>]
"""

import os, re, json, argparse, sys
from collections import defaultdict

DB_FILE  = os.path.join(os.path.dirname(__file__), 'function-db.json')
OUT_DIR  = os.path.join(os.path.dirname(__file__), '..', 'test-suite')

# ── regex helpers ─────────────────────────────────────────────────────────────

# Actual event/function DEFINITION keywords at start of a line
# (NOT control-flow constructs like IF/WHILE/FOR which are statements)
HANDLER_RE = re.compile(
    r'^\s*(PUSH|RELEASE|CHANGE|EVENT|FUNCTION|THREADSAFE|EVENTHANDLER'
    r'|SOCKETRECEIVE|SOCKETSTATUS)\b',
    re.MULTILINE | re.IGNORECASE
)

# I/O declarations that MUST stay at module (top) level
IO_DECL_RE = re.compile(
    r'^\s*(DIGITAL_INPUT|ANALOG_INPUT|STRING_INPUT|BUFFER_INPUT'
    r'|DIGITAL_OUTPUT|ANALOG_OUTPUT|STRING_OUTPUT'
    r'|TCP_CLIENT|TCP_SERVER|UDP_SOCKET)\b',
    re.IGNORECASE
)

# Variable declarations that can live inside a function (but must be first)
VAR_DECL_RE = re.compile(
    r'^\s*(INTEGER|SIGNED_INTEGER|LONG_INTEGER|SIGNED_LONG_INTEGER|REAL'
    r'|STRING)\s+[\w$\[\]]+',
    re.IGNORECASE
)

# Preprocessor directives
DIRECTIVE_RE = re.compile(r'^\s*#\w+', re.IGNORECASE)

# ── type helpers ──────────────────────────────────────────────────────────────

TYPE_DECL = {
    'INTEGER': 'INTEGER', 'SIGNED_INTEGER': 'SIGNED_INTEGER',
    'LONG_INTEGER': 'LONG_INTEGER', 'SIGNED_LONG_INTEGER': 'SIGNED_LONG_INTEGER',
    'REAL': 'REAL', 'STRING': 'STRING',
}
TYPE_ARG = {
    'INTEGER': '1', 'SIGNED_INTEGER': '0', 'LONG_INTEGER': '0',
    'SIGNED_LONG_INTEGER': '0', 'REAL': '1.0', 'STRING': '"test"',
}

# Socket functions that need a typed socket variable as first arg
SOCKET_FIRST_ARG = {
    'socketconnectclient':    'TCP_CLIENT',
    'socketdisconnectclient': 'TCP_CLIENT',
    'socketserverstart':      'TCP_SERVER',
    'socketserverstoplisten': 'TCP_SERVER',
    'socketserverastart':     'TCP_SERVER',
    'socketgetportnumber':    'TCP_CLIENT',
    'socketgetremoteipaddress': 'TCP_CLIENT',
    'socketgetaddressasrequested': 'TCP_CLIENT',
    'socketisbroadcast':      'UDP_SOCKET',
    'socketismulticast':      'UDP_SOCKET',
    'socketudp_enable':       'UDP_SOCKET',
    'socketudp_disable':      'UDP_SOCKET',
    'socketgetsenderipaddress': 'UDP_SOCKET',
    'socketgetstatus':        None,  # requires SOCKETSTATUS event — skip
}

# Functions that can only be used in specific events — skip auto-generation
SKIP_SYNTAX_GEN = {
    'socketgetstatus',   # can only be in SOCKETSTATUS event
    'getexceptioncode',  # can only be in TRY/CATCH
    'getexceptionmessage',
}

# Library directive functions — skip because no real library to load
SKIP_LIBRARY_NAMES = {
    'CRESTRON_LIBRARY', 'CRESTRON_SIMPLSHARP_LIBRARY',
    'USER_SIMPLSHARP_LIBRARY', 'USER_LIBRARY',
}

# CEN-OEM type qualifiers that are only valid in OEM serial port modules
CEN_OEM_QUALIFIERS = {
    '_OEM_CD', '_OEM_CTS', '_OEM_RTS', '_OEM_DTR',
    '_OEM_LONG_BREAK', '_OEM_STR_IN', '_OEM_STR_OUT', '_OEM_PACING',
}

# Common I/O block injected into modules that have no I/O of their own
COMMON_IO = '''\
DIGITAL_INPUT  _SKIP_,Test_DIn;
ANALOG_INPUT   _SKIP_,Test_AIn;
STRING_INPUT   _SKIP_,Test_SIn[256];
BUFFER_INPUT   _SKIP_,Test_BufIn[256];
DIGITAL_OUTPUT _SKIP_,Test_DOut;
ANALOG_OUTPUT  _SKIP_,Test_AOut;
STRING_OUTPUT  _SKIP_,Test_SOut;'''

# ── name helpers ──────────────────────────────────────────────────────────────

def sanitize_name(name):
    s = re.sub(r'[^A-Za-z0-9_]', '_', name)
    return re.sub(r'_+', '_', s).strip('_') or 'Unknown'

def sanitize_cat(cat):
    cat = cat.replace('&amp;', '&').replace('&', 'and')
    return re.sub(r'[^\w\s-]', '', cat).strip().replace(' ', '_') or 'Uncategorized'

# ── example analysis ──────────────────────────────────────────────────────────

def example_has_handlers(example):
    """True only when example has real event/function DEFINITIONS (PUSH, FUNCTION, etc.)
    NOT control-flow keywords like IF/WHILE/FOR which are statements."""
    return bool(HANDLER_RE.search(example))

def example_has_own_io(example):
    return bool(IO_DECL_RE.search(example))

def example_has_cen_oem(example):
    return any(q.upper() in example.upper() for q in CEN_OEM_QUALIFIERS)

# ── generation strategies ─────────────────────────────────────────────────────

def make_header(name):
    return f'#SYMBOL_NAME "Test_{sanitize_name(name)}"\n#DEFAULT_VOLATILE\n\n'


def generate_from_example(name, example, _category):
    """Return .usp content wrapping the help-file example code."""
    header = make_header(name)
    lines  = example.split('\n')

    if example_has_handlers(example):
        # Example already has PUSH/RELEASE/CHANGE/FUNCTION blocks — use as module body.
        # Only add COMMON_IO if the example has no I/O declarations of its own.
        if example_has_own_io(example):
            return header + example.rstrip() + '\n'
        else:
            return header + COMMON_IO + '\n\n' + example.rstrip() + '\n'

    # No handlers — every statement must go inside FUNCTION Main().
    # Separate IO declarations (module-level) from variable declarations and statements.
    io_lines   = []
    var_lines  = []
    stmt_lines = []
    has_stmts  = False  # once we see a non-decl line, all remaining lines are stmts

    for line in lines:
        stripped = line.strip()
        if not stripped:
            # Keep blank lines in whichever section we're building
            (stmt_lines if has_stmts else var_lines).append(line)
            continue
        if stripped.startswith('//'):
            (stmt_lines if has_stmts else var_lines).append(line)
            continue
        if DIRECTIVE_RE.match(line):
            # Preprocessor directives belong at module level but outside functions
            io_lines.append(line)
            continue
        if IO_DECL_RE.match(line):
            io_lines.append(line)
            continue
        if VAR_DECL_RE.match(line) and not has_stmts:
            var_lines.append(line)
            continue
        # Everything else is a statement
        has_stmts = True
        stmt_lines.append(line)

    # Module-level I/O block
    if io_lines:
        io_block = '\n'.join(io_lines)
    else:
        io_block = COMMON_IO

    # Function body: var declarations FIRST, then statements (SIMPL+ is C89-style)
    # Strip trailing blank lines
    while var_lines and not var_lines[-1].strip():
        var_lines.pop()
    while stmt_lines and not stmt_lines[-1].strip():
        stmt_lines.pop()

    separator = [''] if var_lines and stmt_lines else []
    body_lines = var_lines + separator + stmt_lines
    body_indented = '\n'.join('    ' + l for l in body_lines)

    return (
        header
        + io_block + '\n\n'
        + f'FUNCTION Main()\n{{\n{body_indented}\n}}\n'
    )


def generate_from_syntax(name, syntax, _category):
    """Generate a minimal valid call from the first syntax line."""
    safe    = sanitize_name(name)
    name_lc = name.lower()

    # Skip functions that require special event contexts
    if name_lc in SKIP_SYNTAX_GEN:
        return None

    first_line = syntax.split('\n')[0].strip()

    # Check if first arg needs a socket type
    socket_type = SOCKET_FIRST_ARG.get(name_lc)

    # Match: [RETURN_TYPE] FuncName ( params )
    m = re.match(
        r'^(?:(INTEGER|SIGNED_INTEGER|LONG_INTEGER|SIGNED_LONG_INTEGER|REAL|STRING)\s+)?'
        r'(\w+)\s*\(([^)]*)\)',
        first_line, re.IGNORECASE
    )
    if not m:
        body = [f'// Syntax: {first_line}', '// (auto-generation not supported for this syntax)']
        return make_header(name) + COMMON_IO + '\n\nFUNCTION Main()\n{\n' + \
               '\n'.join('    ' + l for l in body) + '\n}\n'

    ret_type   = (m.group(1) or '').upper()
    func_name  = m.group(2)
    params_str = m.group(3).strip()

    # Socket module-level declaration — socket types require a buffer size
    socket_decl = ''
    socket_var  = None
    if socket_type:
        socket_var  = '_mySocket'
        socket_decl = f'{socket_type} {socket_var}[1024];\n'

    # Parse parameters into (var_name, decl, init, arg) tuples
    param_items = []
    param_index = 0
    if params_str and params_str.lower() not in ('', 'void'):
        for i, param in enumerate(re.split(r',', params_str)):
            param = param.strip()
            # Handle socket first-arg override
            if i == 0 and socket_var:
                param_items.append((socket_var, None, None, socket_var))
                continue
            pm = re.match(
                r'^(INTEGER|SIGNED_INTEGER|LONG_INTEGER|SIGNED_LONG_INTEGER|REAL|STRING)\b',
                param, re.IGNORECASE
            )
            if pm:
                ptype = pm.group(1).upper()
                var   = f'_p{param_index}'
                param_index += 1
                if ptype == 'STRING':
                    decl = f'STRING {var}[256];'
                    init = f'{var} = "test";'
                else:
                    decl = f'{ptype} {var};'
                    init = f'{var} = {TYPE_ARG.get(ptype, "0")};'
                param_items.append((var, decl, init, var))
            else:
                param_items.append((f'0 /*{param}*/', None, None, f'0 /*{param}*/'))

    args = [t[3] for t in param_items]
    call = f'{func_name}({", ".join(args)});'

    # Return-value variable
    ret_decl = ''
    if ret_type and ret_type in TYPE_DECL:
        ret_var  = '_result'
        ret_decl = (f'STRING {ret_var}[256];' if ret_type == 'STRING'
                    else f'{TYPE_DECL[ret_type]} {ret_var};')
        call     = f'{ret_var} = {func_name}({", ".join(args)});'

    # Build function body: ALL declarations first, then initializations, then call
    decl_lines = ([ret_decl] if ret_decl else []) + \
                 [t[1] for t in param_items if t[1]]
    init_lines = [t[2] for t in param_items if t[2]]
    stmt_lines = init_lines + [call]

    separator  = [''] if decl_lines and stmt_lines else []
    body_lines = decl_lines + separator + stmt_lines
    body_indented = '\n'.join('    ' + l for l in body_lines)

    io_block = (socket_decl + '\n' + COMMON_IO) if socket_decl else COMMON_IO

    return (
        make_header(name)
        + io_block + '\n\n'
        + f'FUNCTION Main()\n{{\n{body_indented}\n}}\n'
    )


# Directive-specific overrides: maps directive name → exact line to emit
DIRECTIVE_OVERRIDES = {
    'DEFINE_CONSTANT':          '#DEFINE_CONSTANT MY_CONST 100',
    'CATEGORY':                 '#CATEGORY "0"',
    'ANALOG_SERIAL_EXPAND':     '#ANALOG_SERIAL_EXPAND 4',
    'DIGITAL_EXPAND':           '#DIGITAL_EXPAND 4',
    'MAX_INTERNAL_BUFFER_SIZE': '#MAX_INTERNAL_BUFFER_SIZE 256',
    'OUTPUT_SHIFT':             '#OUTPUT_SHIFT 0',
    'INCLUDEPATH':              '// #INCLUDEPATH skipped — requires installed include path',
    'IF_DEFINED_ENDIF':         '#DEFINE_CONSTANT MY_CONST 1\n#IF_DEFINED MY_CONST\n// compiled when MY_CONST is defined\n#ENDIF',
    'IF_NOT_DEFINED_ENDIF':     '#IF_NOT_DEFINED UNDEFINED_CONST\n// compiled when constant is not defined\n#ENDIF',
    'HELP_BEGIN_HELP_END':      '#HELP_BEGIN\nThis module does something useful.\n#HELP_END',
    'DEFAULT_NONVOLATILE':      '#DEFAULT_NONVOLATILE',
    'ANALOG_INPUT_JOIN':        '// _ANALOG_INPUT_JOIN — OEM join directive, series-2 only',
    'ANALOG_OUTPUT_JOIN':       '// _ANALOG_OUTPUT_JOIN — OEM join directive, series-2 only',
    'DIGITAL_INPUT_JOIN':       '// _DIGITAL_INPUT_JOIN — OEM join directive, series-2 only',
    'DIGITAL_OUTPUT_JOIN':      '// _DIGITAL_OUTPUT_JOIN — OEM join directive, series-2 only',
    'STRING_INPUT_JOIN':        '// _STRING_INPUT_JOIN — OEM join directive, series-2 only',
    'STRING_OUTPUT_JOIN':       '// _STRING_OUTPUT_JOIN — OEM join directive, series-2 only',
}


def generate_directive(name, syntax, _category):
    """Generate a minimal module that includes the directive/declaration."""
    safe = sanitize_name(name)

    # Use a known-good override if we have one
    override = DIRECTIVE_OVERRIDES.get(name) or DIRECTIVE_OVERRIDES.get(safe)
    if override:
        directive_line = override
    elif not syntax.strip():
        directive_line = f'// {name} — no syntax'
    else:
        first = syntax.split('\n')[0].strip()
        if first.startswith('#'):
            # Replace <PLACEHOLDER> with sensible defaults
            first = re.sub(r'<\w*[Nn]ame\w*>', safe, first)
            first = re.sub(r'<[Ss]tring[^>]*>', f'"{safe}"', first)
            first = re.sub(r'"<[^>]*>"', f'"{safe}"', first)
            first = re.sub(r'<[Nn]umber[^>]*>|<[Vv]alue[^>]*>|<[Ii]nteger[^>]*>', '0', first)
            first = re.sub(r'<[^>]*>', safe, first)
            directive_line = first
        else:
            directive_line = f'// {name}: {first}'

    return (
        f'#SYMBOL_NAME "Test_{safe}"\n'
        f'#DEFAULT_VOLATILE\n'
        f'{directive_line}\n\n'
        f'DIGITAL_INPUT _SKIP_,Test_DIn;\n\n'
        f'PUSH Test_DIn\n{{\n'
        f'    Print("directive test\\n");\n'
        f'}}\n'
    )

# ── category sets ─────────────────────────────────────────────────────────────

DIRECTIVE_CATS = {
    'Compiler Directives', 'Declarations',
    'User Defined Functions',
    'CEN-OEM Specific Definitions',
}

# ── main ──────────────────────────────────────────────────────────────────────

def main():
    parser = argparse.ArgumentParser(description='Generate SIMPL+ test files')
    parser.add_argument('--db',      default=DB_FILE)
    parser.add_argument('--out-dir', default=OUT_DIR)
    args = parser.parse_args()

    db_path  = os.path.abspath(args.db)
    out_root = os.path.abspath(args.out_dir)

    if not os.path.isfile(db_path):
        print(f'ERROR: DB not found: {db_path}'); sys.exit(1)

    with open(db_path, encoding='utf-8') as f:
        db = json.load(f)

    # Clean out old .usp files (overwrite-safe — just let new writes replace them)
    import shutil
    if os.path.isdir(out_root):
        for entry in os.listdir(out_root):
            full = os.path.join(out_root, entry)
            if entry == '.build':
                continue
            if os.path.isdir(full):
                try:
                    shutil.rmtree(full)
                except PermissionError:
                    pass  # file locked by running compiler — will be overwritten

    os.makedirs(out_root, exist_ok=True)

    stats    = defaultdict(int)
    generated = []

    for entry in db:
        name     = entry['name']
        syntax   = entry.get('syntax', '').strip()
        example  = entry.get('example', '').strip()
        category = entry.get('category', '').replace('&amp;', '&')

        # Skip entries with nothing useful
        if not name or not (syntax or example):
            stats['skipped_no_content'] += 1
            continue

        # Skip library-loading directives (no library to load in test context)
        if name in SKIP_LIBRARY_NAMES:
            stats['skipped_library'] += 1
            continue

        # Skip CEN-OEM entries with OEM type qualifiers (series2-only hardware feature)
        if example_has_cen_oem(example) or name.upper() in {q.lstrip('_') for q in CEN_OEM_QUALIFIERS}:
            stats['skipped_cen_oem'] += 1
            continue

        safe_name = sanitize_name(name)
        safe_cat  = sanitize_cat(category)
        cat_dir   = os.path.join(out_root, safe_cat)
        os.makedirs(cat_dir, exist_ok=True)
        out_path  = os.path.join(cat_dir, f'{safe_name}.usp')

        # Choose strategy
        content = None
        if category in DIRECTIVE_CATS and (not example or not example_has_handlers(example)):
            content = generate_directive(name, syntax, category)
            stats['directive'] += 1
        elif example and len(example.strip()) > 10:
            content = generate_from_example(name, example, category)
            stats['from_example'] += 1
        elif syntax:
            content = generate_from_syntax(name, syntax, category)
            if content is None:
                stats['skipped_special'] += 1
                continue
            stats['from_syntax'] += 1
        else:
            stats['skipped_no_content'] += 1
            continue

        with open(out_path, 'w', encoding='utf-8') as f:
            f.write(content)

        generated.append({'name': name, 'category': category, 'file': out_path})
        stats['total'] += 1

    print(f'Generated {stats["total"]} test files:')
    print(f'  From examples: {stats["from_example"]}')
    print(f'  From syntax:   {stats["from_syntax"]}')
    print(f'  Directives:    {stats["directive"]}')
    print(f'  Skipped (library/CEN-OEM/special): '
          f'{stats["skipped_library"]+stats["skipped_cen_oem"]+stats["skipped_special"]}')
    print(f'  Skipped (no content): {stats["skipped_no_content"]}')
    print(f'\nOutput: {out_root}')

    with open(os.path.join(out_root, 'manifest.json'), 'w', encoding='utf-8') as f:
        json.dump(generated, f, indent=2, ensure_ascii=False)


if __name__ == '__main__':
    main()
