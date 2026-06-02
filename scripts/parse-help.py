#!/usr/bin/env python3
"""
parse-help.py  --  Extract all SIMPL+ function/keyword definitions from the
extracted Simpl+lr.chm HTML files and write function-db.json.

Usage:
    python parse-help.py [--help-dir <path>] [--out <path>]
"""

import os
import re
import json
import argparse
import sys

HELP_DIR = os.path.join(os.path.dirname(__file__), '..', 'help-extracted')
OUT_FILE = os.path.join(os.path.dirname(__file__), 'function-db.json')

# HTM files that are NOT function references (skip these)
SKIP_PATTERNS = [
    r'^Compiler_(Error|Warning)_',
    r'^Allowable_', r'^Array_out_', r'^Bad_printf', r'^BookMarks',
    r'^ByRef', r'^Calling_a', r'^Clock_Driver', r'^Comments',
    r'^Compile_Output', r'^Compiler_Options', r'^Conventions', r'^Cursor_',
    r'^Datatype_', r'^Declarations_',
    r'^Direct_Socket_(Error|Example|Functions_Overview)',
    r'^Dynamic', r'^Edit_', r'^EditMenu', r'^EditSelect',
    r'^Email_Function_Return', r'^EndOfFile', r'^Examples?\.htm',
    r'^Exception_Handling', r'^Expressions_',
    r'^File_(Function_Return|INFO|Time)', r'^For_Whom', r'^Full_Stack',
    r'^Function_(Definition|Libraries|Parameters)', r'^Functions_Overview',
    r'^Important_', r'^Index', r'^Inherit', r'^Insert_Category', r'^Legal',
    r'^Library_not', r'^Making_it', r'^New_Additions', r'^Numeric_Formats',
    r'^Obsolete', r'^Operator_', r'^Overview', r'^PARAMETER_PROPERTIES',
    r'^Program_Structure', r'^RAMP_INFO', r'^Ramping_(Function|Functions)',
    r'^Read_Structure', r'^Reading_and_Writing', r'^Relative_', r'^Release\.',
    r'^rlt1D', r'^Rstack_', r'^Runtime_', r'^Scheduler_',
    r'^SIMPL.Plus.Revisions', r'^SIMPL_Plus_Revisions', r'^Signed_vs',
    r'^Software_', r'^Stacked_', r'^StartFile', r'^Status_Values',
    r'^String_array', r'^STRING_CONCAT', r'^String_Operators',
    r'^STRUCTURES\.', r'^Tabs\.', r'^Target_Selection', r'^Task_',
    r'^Too_much', r'^TP_', r'^Unimplemented', r'^User_Defined',
    r'^Using_SIMPL', r'^UTF16_Unicode', r'^Variable_Names', r'^What_is',
    r'^Where_Can', r'^Windows_', r'^Writing_Your', r'^X.Generation',
    r'^Arithmetic_', r'^ASCII\.', r'^Bitwise_', r'^Relational_',
    r'^_Temp\.', r'^\$', r'^#', r'^BTree', r'^Example_\d',
    r'^Direct_Socket_Access_Example', r'^GatherEvent', r'^File_First',
    r'^FindClose',
]

SKIP_RE = [re.compile(p, re.IGNORECASE) for p in SKIP_PATTERNS]


def should_skip(filename):
    name = os.path.splitext(filename)[0]
    return any(p.match(name) for p in SKIP_RE)


def strip_tags(text):
    """Remove HTML tags, inserting spaces around inline tags to prevent concatenation."""
    text = re.sub(r'<(?:span|a|b|i|em|strong|code|font)[^>]*>', ' ', text, flags=re.IGNORECASE)
    text = re.sub(r'</(?:span|a|b|i|em|strong|code|font)>', ' ', text, flags=re.IGNORECASE)
    text = re.sub(r'<br\s*/?>', ' ', text, flags=re.IGNORECASE)
    text = re.sub(r'<[^>]+>', '', text)
    text = re.sub(r'  +', ' ', text)
    return text


def decode_entities(text):
    """Decode HTML entities and normalize quotation characters to ASCII."""
    text = text.replace('&#160;', ' ').replace('&nbsp;', ' ')
    text = text.replace('&lt;', '<').replace('&gt;', '>').replace('&amp;', '&')
    text = text.replace('&quot;', '"').replace('&#39;', "'")
    text = text.replace('&apos;', "'")
    # Windows-1252 smart quotes as numeric HTML entities -> ASCII straight quotes
    text = text.replace('&#147;', '"').replace('&#148;', '"')
    text = text.replace('&#145;', "'").replace('&#146;', "'")
    text = text.replace('&#150;', '-').replace('&#151;', '-')
    # Unicode smart quotes (U+2018-U+201D, common in Windows-1252 files) -> ASCII
    text = text.replace('“', '"').replace('”', '"')
    text = text.replace('‘', "'").replace('’', "'")
    text = text.replace('–', '-').replace('—', '-')
    # Non-breaking space (U+00A0) -> regular space
    text = text.replace(' ', ' ')
    return text


def clean(text):
    return decode_entities(strip_tags(text)).strip()


def clean_code_line(text):
    """Clean a code chunk line: strip HTML and collapse all internal whitespace to single spaces."""
    text = clean(text)
    # Collapse internal newlines and multiple spaces to a single space
    text = ' '.join(text.split())
    return text


def extract_codechunks(html_fragment):
    """Return list of code lines from <p class="CodeChunk"> elements."""
    lines = []
    for m in re.finditer(r'<p[^>]*class="CodeChunk"[^>]*>(.*?)</p>',
                         html_fragment, re.DOTALL | re.IGNORECASE):
        line = clean_code_line(m.group(1))
        lines.append(line)
    return lines


def extract_plain_paragraphs(html_fragment):
    """Return plain text from paragraphs that are NOT Function/CodeChunk class."""
    text_parts = []
    for m in re.finditer(r'<p([^>]*)>(.*?)</p>', html_fragment, re.DOTALL | re.IGNORECASE):
        attrs = m.group(1)
        if re.search(r'class="(Function|CodeChunk|Note)', attrs, re.IGNORECASE):
            continue
        t = clean(m.group(2))
        if t and t.strip():
            text_parts.append(t)
    return text_parts


def parse_htm(filepath):
    try:
        with open(filepath, 'r', encoding='windows-1252', errors='replace') as f:
            content = f.read()
    except Exception:
        return None

    # Function name from <h1>
    h1 = re.search(r'<h1[^>]*>(.*?)</h1>', content, re.DOTALL | re.IGNORECASE)
    name = clean(h1.group(1)) if h1 else os.path.splitext(os.path.basename(filepath))[0]

    # Category from MadCap:tocPath
    toc = re.search(r'MadCap:tocPath="([^"]*)"', content)
    category = toc.group(1) if toc else ''
    category_parts = [p.strip() for p in category.split('|')]
    category = category_parts[-1] if category_parts else ''

    # Split by <p class="Function"> section headers
    section_map = {}
    current_label = None
    current_html = []

    for chunk in re.split(r'(<p[^>]*class="[Ff]unction"[^>]*>)', content, flags=re.IGNORECASE):
        if re.match(r'<p[^>]*class="[Ff]unction"[^>]*>', chunk, re.IGNORECASE):
            if current_label is not None:
                section_map[current_label] = ''.join(current_html)
            current_html = []
            current_label = '__pending__'
        elif current_label == '__pending__':
            end = chunk.find('</p>')
            label_text = clean(chunk[:end]) if end != -1 else clean(chunk)
            label_text = label_text.lower().strip().rstrip(':').strip()
            current_label = label_text
            current_html = [chunk[end + 4:] if end != -1 else '']
        else:
            current_html.append(chunk)

    if current_label and current_label != '__pending__':
        section_map[current_label] = ''.join(current_html)

    syntax_html  = section_map.get('syntax', '')
    example_html = section_map.get('example', section_map.get('examples', ''))
    desc_html    = section_map.get('description', '')
    return_html  = section_map.get('return value', '')

    syntax_lines  = extract_codechunks(syntax_html)
    example_lines = extract_codechunks(example_html)
    description   = ' '.join(extract_plain_paragraphs(desc_html))
    return_value  = ' '.join(extract_plain_paragraphs(return_html))

    syntax  = '\n'.join(l for l in syntax_lines if l.strip())
    example = '\n'.join(example_lines)

    return {
        'name':         name,
        'category':     category,
        'syntax':       syntax,
        'example':      example,
        'description':  description[:500],
        'return_value': return_value[:200],
        'file':         os.path.basename(filepath),
    }


def main():
    parser = argparse.ArgumentParser(description='Parse SIMPL+ help HTM files')
    parser.add_argument('--help-dir', default=HELP_DIR)
    parser.add_argument('--out',      default=OUT_FILE)
    args = parser.parse_args()

    help_dir = os.path.abspath(args.help_dir)
    if not os.path.isdir(help_dir):
        print(f'ERROR: help-dir not found: {help_dir}'); sys.exit(1)

    htm_files = []
    for root, _dirs, files in os.walk(help_dir):
        for f in files:
            if f.lower().endswith('.htm'):
                htm_files.append(os.path.join(root, f))

    print(f'Found {len(htm_files)} HTM files in {help_dir}')

    results, skipped = [], 0
    for filepath in sorted(htm_files):
        if should_skip(os.path.basename(filepath)):
            skipped += 1
            continue
        entry = parse_htm(filepath)
        if entry and entry['name']:
            results.append(entry)

    print(f'Skipped {skipped} non-function files')
    print(f'Parsed {len(results)} function/keyword entries')

    results.sort(key=lambda x: (x['category'], x['name'].lower()))

    out_path = os.path.abspath(args.out)
    with open(out_path, 'w', encoding='utf-8') as f:
        json.dump(results, f, indent=2, ensure_ascii=False)
    print(f'Written to {out_path}')

    from collections import Counter
    cats = Counter(r['category'] for r in results)
    print('\nCategories:')
    for cat, count in sorted(cats.items()):
        print(f'  {count:3d}  {cat}')


if __name__ == '__main__':
    main()
