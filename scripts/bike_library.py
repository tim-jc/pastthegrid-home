"""Narrow, text-only reader for the existing Standert Markdown and CSV."""
import csv
import json
import posixpath
from datetime import date
from html import escape
from pathlib import Path
import re
from urllib.parse import urlsplit

BIKE = Path('bikes/standert/kreissage_rs.md')
LOG = Path('workshop/maintenance_log.csv')
PAGE = BIKE.with_suffix('') / 'index.html'


def safe_text(text):
    # A source change must not accidentally publish an absolute workstation path.
    if re.search(r'(?:file:|(?<![\w:/<])/[\w.-]+(?:/[\w.-]+)*|[A-Za-z]:[\\/]|~/)', text):
        raise ValueError('Local filesystem path in source text; review before rendering')
    return escape(text)


def slug(text):
    return re.sub(r'[^\w-]+', '-', text.lower()).strip('-')


def inline(text, anchors, warnings):
    """Only links, strong/emphasis and code spans; all raw HTML is escaped."""
    pattern = r'(!?\[([^\]]+)\]\(([^\s)]+)\)|\*\*([^*]+)\*\*|\*([^*]+)\*|`([^`]+)`)'
    parts, pos = [], 0
    for match in re.finditer(pattern, text):
        plain = text[pos:match.start()]
        if any(mark in plain for mark in ('[', ']', '*', '`')):
            raise ValueError('Unsupported inline Markdown')
        parts.append(safe_text(plain))
        whole, label, target, strong, emphasis, code = match.groups()
        if label is not None:
            label = safe_text(label)
            url = urlsplit(target)
            if whole.startswith('!'):
                warnings.append('Image reference retained as text; no image copied')
                parts.append(label + ' <span class="unavailable">(image not included)</span>')
            elif target.startswith('#') and target[1:] in anchors:
                parts.append('<a href="' + escape(target, quote=True) + '">' + label + '</a>')
            elif url.scheme in ('https', 'http') and url.netloc and not url.username and not url.password and url.hostname not in ('localhost', '127.0.0.1', '::1') and not re.match(r'^(?:10\.|192\.168\.|172\.(?:1[6-9]|2\d|3[01])\.)', url.hostname or ''):
                parts.append('<a href="' + escape(target, quote=True) + '">' + label + '</a>')
            else:
                warnings.append('Local, unsafe or unresolved link rendered without a destination')
                parts.append(label + ' <span class="unavailable">(reference not included)</span>')
        else:
            tag, value = ('strong', strong) if strong is not None else (('em', emphasis) if emphasis is not None else ('code', code))
            parts.append('<' + tag + '>' + safe_text(value) + '</' + tag + '>')
        pos = match.end()
    tail = text[pos:]
    if any(mark in tail for mark in ('[', ']', '*', '`')):
        raise ValueError('Unsupported inline Markdown')
    parts.append(safe_text(tail))
    return ''.join(parts)


def markdown(text, extra_anchors=()):
    lines = text.splitlines()
    headings = [re.match(r'^(#{1,5}) (.+)$', line) for line in lines]
    ids, anchors = {}, set(extra_anchors) | {'main', 'completed-maintenance', 'planned-maintenance'}
    for i, heading in enumerate(headings):
        if heading:
            base = slug(heading[2])
            identifier, suffix = base, 1
            while identifier in anchors:
                identifier = base + '-' + str(suffix)
                suffix += 1
            ids[i] = identifier
            anchors.add(identifier)
    if not lines or not re.fullmatch(r'# [^#].*', lines[0]):
        raise ValueError('Expected bike title as first Markdown line')
    out, warnings, toc = [], [], []
    render = lambda value: inline(value, anchors, warnings)
    i = 0
    section_started = False
    while i < len(lines):
        line = lines[i]
        if not line.strip():
            i += 1
            continue
        heading = headings[i]
        if heading:
            # Source uses multiple level-one sections. Keep one page h1 and
            # shift subsequent source headings together beneath it.
            if i > 0 and len(heading[1]) == 1:
                section_started = True
            level = len(heading[1]) + (1 if section_started else 0)
            out.append(f'<h{level} id="{ids[i]}">{render(heading[2])}</h{level}>')
            if i > 0 and len(heading[1]) == 1:
                toc.append((ids[i], heading[2]))
            i += 1
        elif line.startswith('> '):
            quoted = []
            while i < len(lines) and lines[i].startswith('> '):
                if lines[i][2:].startswith(('>', '-', '#', '```')):
                    raise ValueError('Unsupported nested quote construct')
                quoted.append(lines[i][2:])
                i += 1
            out.append('<blockquote><p>' + render(' '.join(quoted)) + '</p></blockquote>')
        elif line == '---':
            out.append('<hr>')
            i += 1
        elif line.startswith('|'):
            rows = []
            while i < len(lines) and lines[i].startswith('|'):
                if not lines[i].endswith('|'):
                    raise ValueError('Unterminated Markdown table row')
                rows.append([v.strip() for v in lines[i].strip('|').split('|')])
                i += 1
            if len(rows) < 2 or not all(re.fullmatch(r':?-+:?', v) for v in rows[1]):
                raise ValueError('Missing Markdown table separator')
            if any(len(row) != len(rows[0]) for row in rows):
                raise ValueError('Inconsistent Markdown table columns')
            table = '<div class="table-scroll" role="region" aria-label="Technical table" tabindex="0"><table><thead><tr>'
            table += ''.join('<th scope="col">' + render(v) + '</th>' for v in rows[0]) + '</tr></thead><tbody>'
            for row in rows[2:]:
                table += '<tr>' + ''.join('<td>' + render(v) + '</td>' for v in row) + '</tr>'
            out.append(table + '</tbody></table></div>')
        elif line.startswith('- '):
            items = []
            while i < len(lines) and lines[i].startswith('- '):
                value = lines[i][2:]
                i += 1
                while i < len(lines) and lines[i].startswith('  ') and not lines[i].lstrip().startswith(('-', '*', '|')):
                    value += ' ' + lines[i].strip()
                    i += 1
                if value.startswith(('[ ] ', '[x] ', '[X] ')):
                    label = 'Unchecked' if value[1] == ' ' else 'Checked'
                    items.append('<li><span class="unavailable">' + label + ':</span> ' + render(value[4:]) + '</li>')
                else:
                    items.append('<li>' + render(value) + '</li>')
            out.append('<ul>' + ''.join(items) + '</ul>')
        else:
            if re.match(r'^\s*(?:#{1,}|>|```|~~~|\d+[.)] |\* |\+ |\[[^]]+\]:)', line) or line.startswith('  '):
                raise ValueError('Unsupported Markdown block at line ' + str(i + 1))
            paragraph = [line]
            i += 1
            while i < len(lines) and lines[i].strip() and not re.match(r'^(?:#|\||- |---|\s{2}|>|```|~~~|\d+[.)] |\* |\+ )', lines[i]):
                paragraph.append(lines[i])
                i += 1
            out.append('<p>' + render(' '.join(paragraph)) + '</p>')
    return '\n'.join(out), toc, warnings


def source_text(root, relative):
    root = Path(root).expanduser().resolve()
    if not root.is_dir():
        raise ValueError('BIKE_LIBRARY_ROOT must point to an existing directory')
    path = root / relative
    if Path(relative).is_absolute() or '..' in Path(relative).parts or not path.resolve().is_relative_to(root):
        raise ValueError('Bike Library source must remain within configured root')
    if not path.is_file():
        raise ValueError('Missing required Bike Library file: ' + str(relative))
    return path.read_text(encoding='utf-8')


def registry(path=None):
    path = path or Path(__file__).resolve().parents[1] / 'config/bikes.json'
    data = json.loads(Path(path).read_text())
    if not isinstance(data, dict) or not data:
        raise ValueError('Empty or invalid bike registry')
    routes, keys = set(), set()
    for source, key in data.items():
        if not re.fullmatch(r'bikes/[a-z0-9_-]+/[a-z0-9_-]+\.md', source):
            raise ValueError('Unsafe bike source path')
        route = str(Path(source).with_suffix('') / 'index.html')
        if route.casefold() in routes:
            raise ValueError('Bike output path collision')
        routes.add(route.casefold())
        if key is not None:
            if not isinstance(key, str) or not key.strip() or key in keys:
                raise ValueError('Ambiguous maintenance mapping')
            keys.add(key)
    return data


def maintenance_rows(root, mappings=None):
    mappings = mappings or registry()
    keys = {value for value in mappings.values() if value is not None}
    reader = csv.DictReader(source_text(root, LOG).splitlines(keepends=True), strict=True)
    if reader.fieldnames != ['work_date', 'bike', 'work_done', 'notes']:
        raise ValueError('Unexpected maintenance CSV schema')
    rows = []
    for number, row in enumerate(reader, 2):
        if None in row or any(value is None for value in row.values()):
            raise ValueError('Malformed maintenance row ' + str(number))
        if row['bike'] not in keys:
            raise ValueError('Ambiguous or unmapped maintenance bike at row ' + str(number))
        if not row['work_done'].strip():
            raise ValueError('Missing work description at maintenance row ' + str(number))
        work_date = row['work_date']
        if work_date:
            try:
                if not re.fullmatch(r'\d{4}-\d{2}-\d{2}', work_date):
                    raise ValueError()
                date.fromisoformat(work_date)
            except ValueError:
                raise ValueError('Invalid maintenance date at row ' + str(number)) from None
        rows.append(row)
    return rows


def summary(record):
    # Read only the existing Summary table, not later component tables.
    match = re.search(r'^## Summary\s*\n(.*?)(?=^#{1,5} |\Z)', record, re.M | re.S)
    result = {}
    if match:
        for line in match[1].splitlines():
            cells = [value.strip() for value in line.strip('|').split('|')]
            if len(cells) == 2 and cells[0] in ('Status', 'Material', 'Year', 'Size'):
                result[cells[0]] = cells[1]
    return result


def discover(root, mappings=None):
    mappings = mappings or registry()
    bikes = []
    for source in sorted(mappings):
        record = source_text(root, source)
        first = record.splitlines()[0] if record.splitlines() else ''
        if not re.fullmatch(r'# [^#].*', first):
            raise ValueError('Expected bike title in ' + source)
        bikes.append({'source': Path(source), 'title': first[2:], 'summary': summary(record),
                      'page': Path(source).with_suffix('') / 'index.html'})
    return bikes


def load(root, approved_image=False, bike=BIKE, rows=None, mappings=None):
    mappings = mappings or registry()
    record = source_text(root, bike)
    if approved_image:
        record = re.sub(r'!\[([^\]]+)\]\(../../photos/standert/standert\.jpg\)', r'[\1](#standert-photograph)', record)
    body, toc, warnings = markdown(record, ('standert-photograph',) if approved_image else ())
    rows = maintenance_rows(root, mappings) if rows is None else rows
    key = mappings.get(str(bike))
    completed = [row for row in rows if key is not None and row['bike'] == key and row['work_date']]
    planned = [row for row in rows if key is not None and row['bike'] == key and not row['work_date']]
    completed.sort(key=lambda row: row['work_date'], reverse=True)
    return body, toc, warnings, completed, planned


def maintenance(rows, dated):
    if not rows:
        return '<p>No ' + ('completed maintenance' if dated else 'planned or undated work') + ' recorded.</p>'
    items = []
    for row in rows:
        when = '<time datetime="{0}">{0}</time>'.format(row['work_date']) if dated else '<span class="eyebrow">Planned or undated</span>'
        items.append('<li>' + when + '<p>' + safe_text(row['work_done']) + '</p>' + ('<p class="maintenance-note">' + safe_text(row['notes']) + '</p>' if row['notes'] else '') + '</li>')
    return '<ul class="maintenance-list">' + ''.join(items) + '</ul>'


def render(root, template, hero=None, bike=BIKE, rows=None, mappings=None):
    if hero is not None and bike != BIKE:
        raise ValueError('Photograph is approved only for Standert')
    title = source_text(root, bike).splitlines()[0][2:]
    body, toc, warnings, completed, planned = load(root, approved_image=hero is not None, bike=bike, rows=rows, mappings=mappings)
    if hero is not None:
        item, encoded, (width, height) = hero
        figure = ('<figure class="bike-hero" id="standert-photograph"><img src="' + escape(item['output'], quote=True)
                  + '" width="' + str(width) + '" height="' + str(height) + '" alt="' + safe_text(item['alt'])
                  + '" decoding="async"><figcaption>' + safe_text(item['caption']) + '</figcaption></figure>')
        body = body.replace('</h1>', '</h1>' + figure, 1)
    toc_html = '<nav class="contents" aria-label="Record sections">' + ''.join('<a href="#' + key + '">' + escape(label) + '</a>' for key, label in toc) + '<a href="#completed-maintenance">Completed maintenance</a><a href="#planned-maintenance">Planned or undated work</a></nav>'
    content = toc_html + '<article class="bike-record">' + body + '</article>'
    content += '<section class="maintenance" aria-labelledby="completed-maintenance"><h2 id="completed-maintenance">Completed maintenance</h2>' + maintenance(completed, True) + '</section>'
    content += '<section class="maintenance" aria-labelledby="planned-maintenance"><h2 id="planned-maintenance">Planned or undated work</h2><p>Undated CSV entries; completion is not implied. Inline checklists remain in the source notes above.</p>' + maintenance(planned, False) + '</section>'
    content = '<p class="record-context">Bike Library · Read-only record</p><p class="reference-notice">One approved photograph is included. Other linked local documents, photographs and records are labelled but not included.</p>' + content
    if hero is None:
        content = content.replace('One approved photograph is included. Other linked', 'Linked')
    start = template.index('    <main ')
    end = template.index('    </main>', start) + len('    </main>')
    page = template[:start] + '    <main id="main" tabindex="-1">' + content + '</main>' + template[end:]
    page = page.replace('href="assets/', 'href="../../../assets/').replace('src="assets/', 'src="../../../assets/')
    page = page.replace('href="./"', 'href="../../../"').replace('Home — Past the Grid', escape(title) + ' — Past the Grid Home')
    page = page.replace('<span class="portal-label">Home <span aria-hidden="true">/</span> Private portal</span>', '<a class="back-home" href="../../">← Bike Library</a>')
    page = page.replace('content="Past the Grid Home — a private portal for personal cycling information."', 'content="' + escape(title, quote=True) + ' — a read-only Bike Library record."')
    return page, warnings, len(completed), len(planned)


def index(template, bikes):
    entries = []
    for bike in bikes:
        fields = bike['summary']
        descriptor = ' · '.join(key + ': ' + value for key, value in fields.items())
        if not descriptor:
            descriptor = 'Status not recorded'
        elif 'Status' not in fields:
            descriptor += ' · Status not recorded'
        href = posixpath.relpath(bike['page'].as_posix(), 'bikes')
        entries.append('<li><h2><a href="' + href + '">' + safe_text(bike['title']) + '</a></h2><p>' + safe_text(descriptor) + '</p></li>')
    content = '<section class="library-index"><p class="eyebrow">Private records</p><h1>Bike Library</h1><ul class="bike-list">' + ''.join(entries) + '</ul></section>'
    start = template.index('    <main ')
    end = template.index('    </main>', start) + len('    </main>')
    page = template[:start] + '<main id="main" tabindex="-1">' + content + '</main>' + template[end:]
    page = page.replace('href="assets/', 'href="../assets/').replace('src="assets/', 'src="../assets/')
    page = page.replace('href="./"', 'href="../"').replace('Home — Past the Grid', 'Bike Library — Past the Grid')
    return page
