#!/usr/bin/env python3
"""Build static pages from the shared shell and their authoritative sources.

Markdown, when present, owns body_<slug>.html. Otherwise the hand-authored body
is used. DIAGRAM markers inline canonical SVG exports; INCLUDE markers only
read trusted HTML snippets beneath tools/. This module is importable without
writing files so transformations can be checked independently of a site build.
"""
import html
from html.parser import HTMLParser
import json
from pathlib import Path
import re
import sys
import unicodedata
import xml.etree.ElementTree as ET

from md2body import render_page

ROOT = Path(__file__).resolve().parent.parent
SVG_NS = 'http://www.w3.org/2000/svg'
ET.register_namespace('', SVG_NS)
ET.register_namespace('xlink', 'http://www.w3.org/1999/xlink')


class BodyScanner(HTMLParser):
    """Locate original tags without reserializing user-authored HTML."""
    def __init__(self, source):
        super().__init__(convert_charrefs=True)
        self.lines = [0]
        for line in source.splitlines(keepends=True):
            self.lines.append(self.lines[-1] + len(line))
        self.ids, self.headings, self.pagers = set(), [], []
        self.divs, self.heading = [], None
        self.feed(source)

    def source_offset(self):
        line, col = self.getpos()
        return self.lines[line - 1] + col

    def handle_starttag(self, tag, attrs):
        attrs = dict(attrs)
        if attrs.get('id'):
            self.ids.add(attrs['id'])
        if tag == 'h2':
            self.heading = {'start': self.source_offset(), 'tag': self.get_starttag_text(),
                            'id': attrs.get('id'), 'text': ''}
        if tag == 'div':
            self.divs.append((self.source_offset(), 'pager' in attrs.get('class', '').split()))

    def handle_endtag(self, tag):
        if tag == 'h2' and self.heading:
            self.headings.append(self.heading)
            self.heading = None
        if tag == 'div' and self.divs:
            start, pager = self.divs.pop()
            if pager:
                self.pagers.append((start, self.source_offset() + len('</div>')))

    def handle_data(self, data):
        if self.heading is not None:
            self.heading['text'] += data


def add_heading_ids(source):
    scan = BodyScanner(source)
    changes, headings = [], []
    for heading in scan.headings:
        text = ' '.join(heading['text'].split())
        anchor = heading['id']
        if not anchor:
            label = re.sub(r'^\d+(?:\.\d+)*[.、．\s]+', '', text)
            slug = re.sub(r'[^\w-]+', '-', unicodedata.normalize('NFKC', label).lower()).strip('-')
            base = 'section-' + (slug or 'heading')
            anchor, index = base, 2
            while anchor in scan.ids:
                anchor = f'{base}-{index}'; index += 1
            scan.ids.add(anchor)
            position = heading['start'] + len(heading['tag']) - 1
            changes.append((position, f' id="{html.escape(anchor, quote=True)}"'))
        headings.append((anchor, text))
    for position, inserted in reversed(changes):
        source = source[:position] + inserted + source[position:]
    return source, headings


def remove_legacy_pagers(source):
    for start, end in reversed(BodyScanner(source).pagers):
        source = source[:start] + source[end:]
    return source


def scope_svg_css(css, root_id):
    """Scope exported SVG rules, including nested media/supports blocks.

    This is an embedding transform, not an Archify export implementation.
    The input must already be the canonical SVG downloaded from the viewer.
    """
    css = re.sub(r'/\*.*?\*/', '', css, flags=re.S)
    output, cursor = [], 0
    while cursor < len(css):
        imported = re.match(r'\s*@import\s+[^;]+;', css[cursor:])
        if imported:
            output.append(imported[0].strip())
            cursor += imported.end()
            continue
        opening = css.find('{', cursor)
        if opening < 0:
            if css[cursor:].strip():
                raise ValueError('SVG stylesheet contains an unsupported standalone rule')
            break
        header = css[cursor:opening].strip()
        depth, quote, escape, end = 1, None, False, opening + 1
        while end < len(css) and depth:
            char = css[end]
            if escape:
                escape = False
            elif char == '\\':
                escape = True
            elif quote:
                if char == quote:
                    quote = None
            elif char in ('"', "'"):
                quote = char
            elif char == '{':
                depth += 1
            elif char == '}':
                depth -= 1
            end += 1
        if depth:
            raise ValueError('SVG stylesheet has unbalanced braces')
        content = css[opening + 1:end - 1]
        if header.startswith(('@media', '@supports', '@layer', '@container')):
            content = scope_svg_css(content, root_id)
        elif header.startswith(('@font-face', '@keyframes', '@-webkit-keyframes')):
            pass
        elif header.startswith('@'):
            raise ValueError(f'Unsupported SVG stylesheet rule: {header}')
        else:
            selectors = []
            # Split selector lists only outside attribute/function arguments.
            pieces, start, level = [], 0, 0
            for pos, char in enumerate(header):
                if char in '([':
                    level += 1
                elif char in ')]':
                    level -= 1
                elif char == ',' and level == 0:
                    pieces.append(header[start:pos]); start = pos + 1
            pieces.append(header[start:])
            for selector in pieces:
                selector = re.sub(r':root\b|(?<![\w.#-])(?:svg|html|body)(?![\w-])',
                                  '#' + root_id, selector.strip())
                if selector.startswith(('[data-theme', '[data-preset', '[data-quality-profile')):
                    selector = '#' + root_id + selector
                if not selector.startswith('#' + root_id):
                    selector = '#' + root_id + ' ' + selector
                selectors.append(selector)
            header = ', '.join(selectors)
        output.append(f'{header}{{{content}}}')
        cursor = end
    return '\n'.join(output)


def diagram_figure(path, slug, instance):
    tree = ET.fromstring(path.read_text(encoding='utf-8'))
    if tree.tag != '{' + SVG_NS + '}svg':
        raise ValueError(f'DIAGRAM asset is not an SVG: {path}')
    prefix = f'diagram-{slug}-{instance}'
    root_id = prefix + '-svg'
    styles = '\n'.join(node.text or '' for node in tree.iter()
                       if node.tag == '{' + SVG_NS + '}style')
    animation_names = set(re.findall(r'@(?:-webkit-)?keyframes\s+([\w-]+)', styles))
    face_names = set(re.findall(r'@font-face\s*\{[^}]*?font-family:\s*[\"\']([^\"\']+)', styles))
    id_map = {node.attrib['id']: prefix + '-' + node.attrib['id']
              for node in tree.iter() if 'id' in node.attrib}
    if tree.get('id'):
        id_map[tree.get('id')] = root_id

    def references(value):
        value = re.sub(r'url\(\s*([\"\']?)#([^\s)\"\']+)\1\s*\)',
                       lambda m: 'url(#' + id_map.get(m[2], m[2]) + ')', value)
        return value

    for node in tree.iter():
        if node.tag == '{' + SVG_NS + '}script':
            raise ValueError(f'DIAGRAM must be a static canonical SVG, not a script: {path}')
        for key, value in list(node.attrib.items()):
            if key.lower().startswith('on'):
                raise ValueError(f'DIAGRAM contains an event handler: {path}')
            if key == 'id':
                node.set(key, id_map[value])
            elif key in ('aria-labelledby', 'aria-describedby'):
                node.set(key, ' '.join(id_map.get(token, token) for token in value.split()))
            elif key.endswith('href') and value.startswith('#'):
                node.set(key, '#' + id_map.get(value[1:], value[1:]))
            else:
                node.set(key, references(value))
        if node.tag == '{' + SVG_NS + '}style':
            css = references(node.text or '')
            for old, new in sorted(id_map.items(), key=lambda item: -len(item[0])):
                css = re.sub(r'#' + re.escape(old) + r'(?![\w-])', '#' + new, css)
            for name in animation_names:
                css = re.sub(r'(?<![\w-])' + re.escape(name) + r'(?![\w-])', prefix + '-' + name, css)
            # Exported local font-face declarations must not override page fonts.
            for name in face_names:
                def rename_family(match):
                    family = re.sub(r'([\"\'])' + re.escape(name) + r'\1',
                                    lambda quoted: quoted[1] + prefix + '-' + name + quoted[1], match[2])
                    return match[1] + family
                css = re.sub(r'(font-family\s*:\s*)([^;}]+)', rename_family, css)
            node.text = scope_svg_css(css, root_id)
    tree.set('id', root_id)
    tree.set('role', 'img')
    title_node = tree.find('{' + SVG_NS + '}title')
    desc_node = tree.find('{' + SVG_NS + '}desc')
    title = ''.join(title_node.itertext()).strip() if title_node is not None else slug.replace('-', ' ')
    if title_node is None:
        title_node = ET.Element('{' + SVG_NS + '}title')
        title_node.text = title
        tree.insert(0, title_node)
    elif list(tree).index(title_node) != 0:
        tree.remove(title_node); tree.insert(0, title_node)
    title_node.set('id', prefix + '-title')
    labelledby = prefix + '-title'
    if desc_node is not None:
        desc_node.set('id', prefix + '-desc')
        labelledby += ' ' + prefix + '-desc'
    tree.set('aria-labelledby', labelledby)
    tree.set('style', tree.get('style', '') + ';display:block;width:100%;height:auto;')
    svg = ET.tostring(tree, encoding='unicode')
    return (f'<figure class="lesson-diagram">{svg}<figcaption>{html.escape(title)}'
            f' <a href="assets/diagrams/{slug}.svg" target="_blank" rel="noopener">開啟大圖 ↗</a>'
            '</figcaption></figure>')


def expand_assets(source, root=ROOT):
    counts = {}
    marker = re.compile(r'<!--(DIAGRAM|INCLUDE):([^\n]*?)-->')

    def expand(text, stack=()):
        def replacement(match):
            kind, value = match[1], match[2].strip()
            if kind == 'DIAGRAM':
                if not re.fullmatch(r'[a-z0-9]+(?:-[a-z0-9]+)*', value):
                    raise ValueError(f'Invalid DIAGRAM slug: {value}')
                path = root / 'assets/diagrams' / (value + '.svg')
                if not path.is_file():
                    raise FileNotFoundError(f'Missing required DIAGRAM asset: {path}')
                counts[value] = counts.get(value, 0) + 1
                return diagram_figure(path, value, counts[value])
            path = (root / value).resolve()
            allowed = (root / 'tools').resolve()
            if not value.startswith('tools/') or not path.is_relative_to(allowed) or path.suffix != '.html':
                raise ValueError(f'INCLUDE must name a trusted tools/*.html snippet: {value}')
            if path in stack:
                raise ValueError(f'Circular INCLUDE: {value}')
            if not path.is_file():
                raise FileNotFoundError(f'Missing required INCLUDE snippet: {path}')
            return expand(path.read_text(encoding='utf-8'), stack + (path,))
        return marker.sub(replacement, text)
    return expand(source)


def navigation(config, current, headings):
    items = ['<nav class="course-nav" aria-label="課程與本章目錄">']
    for group in config['groups']:
        items.append(f'<div class="nav-group"><p class="nav-group-title">{html.escape(group["title"])}</p><ul>')
        for slug in group['pages']:
            selected = slug == current
            state = ' aria-current="page"' if selected else ''
            items.append(f'<li><a class="chapter-link" href="{slug}.html"{state}>{html.escape(config["pages"][slug]["title"])}</a>')
            if selected and headings:
                items.append('<ul class="section-nav" aria-label="本章內容">')
                for anchor, label in headings:
                    items.append(f'<li><a href="#{html.escape(anchor, quote=True)}">{html.escape(label)}</a></li>')
                items.append('</ul>')
            items.append('</li>')
        items.append('</ul></div>')
    items.append('</nav>')
    return '\n'.join(items)


def pager(config, current):
    links = []
    for direction, label in [('prev', '上一章'), ('next', '下一章')]:
        target = config['pages'][current].get(direction)
        if target:
            title = html.escape(config['pages'][target]['title'])
            title = '← ' + title if direction == 'prev' else title + ' →'
            links.append(f'<a href="{target}.html" class="{direction}"><div class="d">{label}</div><div class="t2">{title}</div></a>')
    return '<nav class="pager" aria-label="章節順序">' + ''.join(links) + '</nav>' if links else ''


def compose_page(slug, source, config, head, tail, root=ROOT):
    metadata = re.match(r'<!--TITLE:(.*?)-->\s*\n<!--DESC:(.*?)-->\s*\n', source)
    if not metadata:
        raise ValueError(f'body_{slug}.html must begin with TITLE and DESC comments')
    title, description = metadata[1], metadata[2]
    body = expand_assets(remove_legacy_pagers(source[metadata.end():]), root)
    body, headings = add_heading_ids(body)
    for key, value in [('__TITLE__', title), ('__DESC__', description)]:
        head = head.replace(key, html.escape(value, quote=True))
    head = head.replace('__SITE_CSS__', (root / 'tools/site-layout.css').read_text(encoding='utf-8'))
    tail = tail.replace('__SITE_JS__', (root / 'tools/site-navigation.js').read_text(encoding='utf-8'))
    nav = navigation(config, slug, headings)
    output = (head + '\n<div class="site-shell">'
            '<aside class="lesson-sidebar" aria-label="教材導覽">'
            '<div class="desktop-course-menu">' + nav + '</div>'
            '<details class="course-menu"><summary>課程與本章目錄</summary>'
            + nav + '</details></aside>'
            '<main id="main-content" class="lesson-main" tabindex="-1">'
            + body + pager(config, slug) + '</main></div>\n' + tail)
    return '\n'.join(line.rstrip() for line in output.splitlines()) + '\n'


def main(argv=None):
    config = json.loads((ROOT / 'tools/pages.json').read_text(encoding='utf-8'))
    pages = argv if argv is not None else sys.argv[1:]
    pages = pages or [slug for group in config['groups'] for slug in group['pages']]
    head = (ROOT / 'tools/_head.fragment').read_text(encoding='utf-8')
    tail = (ROOT / 'tools/_tail.fragment').read_text(encoding='utf-8')
    pending = []
    # Resolve every requested asset before writing any source-derived output.
    for slug in pages:
        if slug not in config['pages']:
            raise ValueError(f'Unknown page slug: {slug}')
        markdown = ROOT / 'content' / (slug + '.md')
        body_path = ROOT / 'tools' / ('body_' + slug + '.html')
        generated = markdown.is_file()
        source = (render_page(slug, markdown.read_text(encoding='utf-8'), config['pages'][slug])
                  if generated else body_path.read_text(encoding='utf-8'))
        output = compose_page(slug, source, config, head, tail)
        pending.append((slug, body_path, source if generated else None, output))
    for slug, body_path, source, output in pending:
        if source is not None:
            body_path.write_text(source, encoding='utf-8')
        (ROOT / (slug + '.html')).write_text(output, encoding='utf-8')
        print(f'已產生 {slug}.html')


if __name__ == '__main__':
    try:
        main()
    except (OSError, ValueError, ET.ParseError) as error:
        raise SystemExit(f'建置失敗：{error}')
