import re
import sys
from enum import Enum

import mwparserfromhell
from mwparserfromhell.nodes import Tag

behaviour_switches = [
    '__NOTOC__', '__FORCETOC__', '__TOC__', '__NOEDITSECTION__',
    '__NEWSECTIONLINK__', '__NONEWSECTIONLINK__', '__NOGALLERY__',
    '__HIDDENCAT__', '__EXPECTUNUSEDCATEGORY__', '__NOCONTENTCONVERT__',
    '__NOCC__', '__NOTITLECONVERT__', '__NOTC__', '__START__', '__END__',
    '__INDEX__', '__NOINDEX__', '__STATICREDIRECT__', '__EXPECTUNUSEDTEMPLATE__',
    '__NOGLOBAL__', '__DISAMBIG__', '__EXPECTED_UNCONNECTED_PAGE__',
    '__ARCHIVEDTALK__', '__NOTALK__', '__EXPECTWITHOUTSCANS__',
]


def capitalise_first_letter(text):
    if not text or not text.strip():
        return text
    return text[0].upper() + text[1:]


def is_emoji_unicode(char):
    if 0x1F600 <= ord(char) <= 0x1F64F:
        return True
    if 0x1F300 <= ord(char) <= 0x1F5FF:
        return True
    if 0x1F680 <= ord(char) <= 0x1F6FF:
        return True
    if 0x2600 <= ord(char) <= 0x26FF:
        return True
    if 0x2700 <= ord(char) <= 0x27BF:
        return True
    return False


def _wrap_in_translate(text):
    if not text or not text.strip():
        return text

    first_char_index = -1
    last_char_index = -1
    for i, char in enumerate(text):
        if char not in (' ', '\n', '\t', '\r', '\f', '\v'):
            if first_char_index == -1:
                first_char_index = i
            last_char_index = i

    if first_char_index == -1:
        return text

    leading_whitespace = text[:first_char_index]
    content = text[first_char_index : last_char_index + 1]
    trailing_whitespace = text[last_char_index + 1 :]

    return f"{leading_whitespace}<translate>{content}</translate>{trailing_whitespace}"


def process_syntax_highlight(text):
    assert text.startswith('<syntaxhighlight') and text.endswith('</syntaxhighlight>'), \
        "Invalid syntax highlight tag"
    start_tag_end = text.find('>') + 1
    end_tag_start = text.rfind('<')
    if start_tag_end >= end_tag_start:
        return text
    prefix = text[:start_tag_end]
    content = text[start_tag_end:end_tag_start].strip()
    suffix = text[end_tag_start:]
    if not content:
        return text
    return f"{prefix}{_wrap_in_translate(content)}{suffix}"


def process_table(text):
    try:
        wikicode = mwparserfromhell.parse(text)
    except Exception as e:
        print(f"Error parsing table: {e}")
        return text

    if not wikicode.nodes:
        return text

    table = wikicode.nodes[0]
    if not isinstance(table, Tag):
        return text

    def process_cells(nodes):
        for node in nodes:
            if isinstance(node, Tag):
                if node.tag in ('td', 'th'):
                    cell_content = str(node.contents)
                    if cell_content.strip():
                        node.contents = convert_to_translatable_wikitext(cell_content)
                elif node.tag == 'tr':
                    process_cells(node.contents.nodes)

    if hasattr(table, 'contents'):
        process_cells(table.contents.nodes)

    return str(wikicode)


def process_blockquote(text):
    assert text.startswith('<blockquote>') and text.endswith('</blockquote>'), \
        "Invalid blockquote tag"
    start_tag_end = text.find('>') + 1
    end_tag_start = text.rfind('<')
    if start_tag_end >= end_tag_start:
        return text
    prefix = text[:start_tag_end]
    content = text[start_tag_end:end_tag_start].strip()
    suffix = text[end_tag_start:]
    if not content:
        return text
    return f"{prefix}{_wrap_in_translate(content)}{suffix}"


def process_poem_tag(text):
    assert text.startswith('<poem') and text.endswith('</poem>'), "Invalid poem tag"
    start_tag_end = text.find('>') + 1
    end_tag_start = text.rfind('<')
    if start_tag_end >= end_tag_start:
        return text
    prefix = text[:start_tag_end]
    content = text[start_tag_end:end_tag_start].strip()
    suffix = text[end_tag_start:]
    if not content:
        return text
    return f"{prefix}{_wrap_in_translate(content)}{suffix}"


def process_formatting_tag(text, tag_name="center"):
    open_tag = f"<{tag_name}>"
    close_tag = f"</{tag_name}>"
    assert text.startswith(open_tag) and text.endswith(close_tag), \
        f"Invalid {tag_name} tag"
    start_tag_end = len(open_tag)
    end_tag_start = text.rfind(close_tag)
    if start_tag_end >= end_tag_start:
        return text
    prefix = text[:start_tag_end]
    content = text[start_tag_end:end_tag_start]
    suffix = text[end_tag_start:]
    if not content.strip():
        return text
    return f"{prefix}{convert_to_translatable_wikitext(content)}{suffix}"


def process_code_tag(text, tvar_code_id=0):
    assert text.startswith('<code') and text.endswith('</code>'), "Invalid code tag"
    start_tag_end = text.find('>') + 1
    end_tag_start = text.rfind('<')
    if start_tag_end >= end_tag_start:
        return text
    prefix = text[:start_tag_end]
    content = text[start_tag_end:end_tag_start].strip()
    suffix = text[end_tag_start:]
    if not content:
        return text
    return f'<tvar name="code{tvar_code_id}">{prefix}{content}{suffix}</tvar>'


def process_div(text):
    assert text.startswith('<div') and text.endswith('</div>'), "Invalid div tag"
    start_tag_end = text.find('>') + 1
    end_tag_start = text.rfind('</div>')
    if start_tag_end >= end_tag_start:
        return text
    prefix = text[:start_tag_end]
    content = text[start_tag_end:end_tag_start]
    suffix = '</div>'
    if not content.strip():
        return text
    return f"{prefix}{convert_to_translatable_wikitext(content)}{suffix}"


def process_hiero(text):
    assert text.startswith('<hiero>') and text.endswith('</hiero>'), "Invalid hiero tag"
    start_tag_end = text.find('>') + 1
    end_tag_start = text.rfind('<')
    if start_tag_end >= end_tag_start:
        return text
    prefix = text[:start_tag_end]
    content = text[start_tag_end:end_tag_start].strip()
    suffix = text[end_tag_start:]
    if not content:
        return text
    return f"{prefix}{_wrap_in_translate(content)}{suffix}"


def process_sub_sup(text):
    assert (
        (text.startswith('<sub>') and text.endswith('</sub>')) or
        (text.startswith('<sup>') and text.endswith('</sup>'))
    ), "Invalid sub/sup tag"
    start_tag_end = text.find('>') + 1
    end_tag_start = text.rfind('<')
    if start_tag_end >= end_tag_start:
        return text
    prefix = text[:start_tag_end]
    content = text[start_tag_end:end_tag_start].strip()
    suffix = text[end_tag_start:]
    if not content:
        return text
    return f"{prefix}{_wrap_in_translate(content)}{suffix}"


def process_math(text):
    assert text.startswith('<math>') and text.endswith('</math>'), "Invalid math tag"
    return text


def process_small_tag(text):
    assert text.startswith('<small>') and text.endswith('</small>'), "Invalid small tag"
    start_tag_end = text.find('>') + 1
    end_tag_start = text.rfind('<')
    if start_tag_end >= end_tag_start:
        return text
    prefix = text[:start_tag_end]
    content = text[start_tag_end:end_tag_start].strip()
    suffix = text[end_tag_start:]
    if not content:
        return text
    return f"{prefix}{_wrap_in_translate(content)}{suffix}"


def process_existing_translate(text):
    assert text.startswith('<translate>') and text.endswith('</translate>'), \
        "Invalid translate tag"
    start_tag_end = text.find('>') + 1
    end_tag_start = text.rfind('<')
    if start_tag_end >= end_tag_start:
        return ""
    content = text[start_tag_end:end_tag_start]
    if not content.strip():
        return content
    return convert_to_translatable_wikitext(content)


def process_nowiki(text):
    assert text.startswith('<nowiki>') and text.endswith('</nowiki>'), "Invalid nowiki tag"
    start_tag_end = text.find('>') + 1
    end_tag_start = text.rfind('<')
    if start_tag_end >= end_tag_start:
        return text
    prefix = text[:start_tag_end]
    content = text[start_tag_end:end_tag_start].strip()
    suffix = text[end_tag_start:]
    if not content:
        return text
    return f"{prefix}{_wrap_in_translate(content)}{suffix}"


def process_item(text):
    offset = 0
    if text.startswith(';'):
        offset = 1
    elif text.startswith(':'):
        offset = 1
    elif text.startswith('#'):
        while text[offset] == '#':
            offset += 1
    elif text.startswith('*'):
        while text[offset] == '*':
            offset += 1
    item_content = text[offset:].strip()
    if not item_content:
        return text
    return text[:offset] + ' ' + convert_to_translatable_wikitext(item_content) + '\n'


class double_brackets_types(Enum):
    wikilink = 1
    category = 2
    inline_icon = 3
    not_inline_icon_file = 4
    special = 5
    invalid_file = 6


def _process_file(s, tvar_inline_icon_id=0):
    NON_TRANSLATABLE_KEYWORDS = {
        'left', 'right', 'centre', 'center', 'thumb', 'frameless', 'border', 'none',
        'upright', 'baseline', 'middle', 'sub', 'super', 'text-top', 'text-bottom',
        '{{dirstart}}', '{{dirend}}',
    }
    NON_TRANSLATABLE_KEYWORDS_PREFIXES = {'link=', 'upright=', 'alt='}
    NOT_INLINE_KEYWORDS = {
        'left', 'right', 'centre', 'center', 'thumb', 'frameless', 'border', 'none',
        '{{dirstart}}', '{{dirend}}',
    }
    file_aliases = ['File:', 'file:', 'Image:', 'image:']

    inner_content = s[2:-2]
    tokens = [token.strip() for token in inner_content.split('|')]

    if not tokens or not tokens[0].startswith(tuple(file_aliases)):
        return s, double_brackets_types.invalid_file

    filename = tokens[0].split(':', 1)[1] if ':' in tokens[0] else tokens[0]
    tokens[0] = f'File:{filename}'

    while 'left' in tokens:
        tokens[tokens.index('left')] = '{{dirstart}}'
    while 'right' in tokens:
        tokens[tokens.index('right')] = '{{dirend}}'

    is_inline_icon = True
    for token in tokens:
        if token in NOT_INLINE_KEYWORDS:
            is_inline_icon = False
            break
    if is_inline_icon:
        for token in tokens[1:]:
            if token.startswith('alt='):
                alt_text = token[len('alt='):].strip()
                if not any(is_emoji_unicode(char) for char in alt_text):
                    is_inline_icon = False
                    break
            elif token not in NON_TRANSLATABLE_KEYWORDS:
                is_inline_icon = False
                break
            elif any(token.startswith(prefix) for prefix in NON_TRANSLATABLE_KEYWORDS_PREFIXES):
                is_inline_icon = False
                break

    if is_inline_icon:
        returnline = f'<tvar name="icon{tvar_inline_icon_id}">[[' + '|'.join(tokens) + ']]</tvar>'
        return returnline, double_brackets_types.inline_icon

    output_parts = [tokens[0]]
    pixel_regex = re.compile(r'\d+(?:x\d+)?px')
    for token in tokens[1:]:
        if token.startswith('alt='):
            alt_text = token[len('alt='):].strip()
            output_parts.append('alt=' + _wrap_in_translate(alt_text))
        elif token in NON_TRANSLATABLE_KEYWORDS:
            output_parts.append(token)
        elif any(token.startswith(prefix) for prefix in NON_TRANSLATABLE_KEYWORDS_PREFIXES):
            output_parts.append(token)
        elif pixel_regex.match(token):
            output_parts.append(token)
        else:
            output_parts.append(f"<translate>{token}</translate>")

    returnline = '[[' + '|'.join(output_parts) + ']]'
    return returnline, double_brackets_types.not_inline_icon_file


def process_double_brackets(text, tvar_id=0):
    if not (text.startswith("[[") and text.endswith("]]")):
        print(f"Input >{text}< must be wrapped in double brackets [[ ]]")
        sys.exit(1)

    if '<tvar' in text:
        return text, double_brackets_types.wikilink

    inner_wl = text[2:-2].strip()
    s = inner_wl

    first = s.find('|')
    if first == -1:
        parts = [s]
    else:
        second = s.find('|', first + 1)
        if second != -1:
            parts = [s[:second], s[second + 1:]]
        else:
            parts = [s[:first], s[first + 1:]]

    category_aliases = ['Category:', 'category:', 'Cat:', 'cat:']
    file_aliases = ['File:', 'file:', 'Image:', 'image:']
    skip_namespaces = category_aliases + file_aliases + ['Special:', 'User:', 'User talk:']

    internal_namespaces = {
        'Talk:', 'talk:', 'User:', 'user:', 'User talk:', 'user talk:',
        'Project:', 'project:', 'Project talk:', 'project talk:',
        'File:', 'file:', 'File talk:', 'file talk:',
        'MediaWiki:', 'mediawiki:', 'MediaWiki talk:', 'mediawiki talk:',
        'Template:', 'template:', 'Template talk:', 'template talk:',
        'Help:', 'help:', 'Help talk:', 'help talk:',
        'Category:', 'category:', 'Category talk:', 'category talk:',
        'Special:', 'special:', 'Media:', 'media:',
        'Image:', 'image:', 'Image talk:', 'image talk:',
        'Cat:', 'cat:',
    }
    inter_language_prefixes = {
        'en', 'fr', 'de', 'es', 'it', 'pt', 'nl', 'pl', 'ru', 'ja', 'zh', 'ar',
        'hi', 'bn', 'ta', 'te', 'ml', 'kn', 'mr', 'gu', 'pa', 'or', 'as', 'ur',
        'fa', 'he', 'ko', 'vi', 'th', 'id', 'ms', 'tr', 'uk', 'cs', 'sv', 'fi',
        'da', 'no', 'nb', 'nn', 'el', 'hu', 'ro', 'bg', 'sr', 'hr', 'sk', 'sl',
        'et', 'lv', 'lt', 'ca', 'eu', 'gl', 'ga', 'cy', 'is', 'sq', 'simple',
    }

    ns = None
    if ':' in parts[0]:
        ns = parts[0].split(':', 1)[0] + ':'

    if parts[0].startswith(tuple(category_aliases)):
        cat_name = parts[0].split(':', 1)[1] if ':' in parts[0] else parts[0]
        return f'[[Category:{cat_name}{{{{#translation:}}}}]]', double_brackets_types.category
    if parts[0].startswith(tuple(file_aliases)):
        return _process_file(text)
    if ns in skip_namespaces:
        return text, double_brackets_types.special if ns == 'Special:' else double_brackets_types.wikilink
    if ns is not None and ns[:-1].lower() in inter_language_prefixes:
        return text, double_brackets_types.wikilink
    if ns is not None and ns not in internal_namespaces:
        link_target = capitalise_first_letter(parts[0])
        display_text = parts[0] if len(parts) == 1 else parts[1]
        return f'[[<tvar name="{tvar_id}">{link_target}</tvar>|{display_text}]]', double_brackets_types.wikilink
    if len(parts) == 1:
        return (
            f'[[<tvar name="{tvar_id}">Special:MyLanguage/{capitalise_first_letter(parts[0])}</tvar>|{parts[0]}]]',
            double_brackets_types.wikilink,
        )
    if len(parts) == 2:
        return (
            f'[[<tvar name="{tvar_id}">Special:MyLanguage/{capitalise_first_letter(parts[0])}</tvar>|{parts[1]}]]',
            double_brackets_types.wikilink,
        )

    return text


def process_external_link(text, tvar_url_id=0):
    match = re.match(r'\[(https?://[^\s]+)\s+([^\]]+)\]', text)
    if match:
        url_part = match.group(1)
        description_part = match.group(2)
        return f'[<tvar name="url{tvar_url_id}">{url_part}</tvar> {description_part}]'
    return text


def process_template(text):
    assert text.startswith('{{') and text.endswith('}}'), "Invalid template tag"
    code = mwparserfromhell.parse(text)
    template = code.filter_templates()[0]
    if template.has(2):
        param = template.get(2)
        param.value = f"2=<translate>{param.value.strip_code()}</translate>"
    return str(code)


def process_section_heading(text):
    match = re.match(r'^(=+)([^=]+)(=+)$', text.strip())
    if not match:
        return text
    level = match.group(1)
    heading_text = match.group(2).strip()
    return f'<translate>\n{level}{heading_text}{level}\n</translate>'


def process_raw_url(text):
    if not text.strip():
        return text
    return text.strip()


def _find_balanced_close_tag(wikitext, start, open_tag, close_tag, open_check_chars=None):
    count = 1
    pos = start + len(open_tag)
    open_len = len(open_tag)
    close_len = len(close_tag)
    n = len(wikitext)

    while pos < n and count > 0:
        next_open = wikitext.find(open_tag, pos)
        next_close = wikitext.find(close_tag, pos)

        if next_close == -1:
            return n

        if next_open != -1 and next_open < next_close:
            after = next_open + open_len
            if open_check_chars is None or (after < n and wikitext[after] in open_check_chars):
                count += 1
                pos = after
            else:
                pos = next_open + 1
        else:
            count -= 1
            pos = next_close + close_len

    return pos


tvar_name = re.compile(r'<tvar\s+name=(?:"[^"]*"|[^\s">]+)\s*>')
boundary_pattern = re.compile(r'(\n[ \t]*\n|</?translate>)')


def renumber_tvars_per_unit(text):
    out = []
    for piece in boundary_pattern.split(text):
        if boundary_pattern.fullmatch(piece):
            out.append(piece)
            continue
        counter = {'n': 0}

        def _repl(_m):
            counter['n'] += 1
            return f'<tvar name="{counter["n"]}">'

        out.append(tvar_name.sub(_repl, piece))
    return ''.join(out)


def convert_to_translatable_wikitext(wikitext):
    if not wikitext:
        return ""
    wikitext = wikitext.replace('\r\n', '\n').replace('\r', '\n')
    wikitext = '\n' + wikitext

    parts = []
    last = 0
    curr = 0
    text_length = len(wikitext)

    while curr < text_length:
        found = None
        if wikitext[curr] == '=':
            end_line = wikitext.find('\n', curr)
            if end_line == -1:
                end_line = text_length
            line = wikitext[curr:end_line]
            if re.match(r'^(=+)[^=]+(=+)$', line.strip()):
                if last < curr:
                    parts.append((wikitext[last:curr], _wrap_in_translate))
                parts.append((line, process_section_heading))
                curr = end_line
                last = curr
                continue
        pattern = '<syntaxhighlight'
        if wikitext.startswith(pattern, curr):
            end_pattern = wikitext.find('</syntaxhighlight>', curr) + len('</syntaxhighlight>')
            if last < curr:
                parts.append((wikitext[last:curr], _wrap_in_translate))
            parts.append((wikitext[curr:end_pattern], process_syntax_highlight))
            curr = end_pattern
            last = curr
            continue
        pattern = '<translate>'
        if wikitext.startswith(pattern, curr):
            end_pattern = wikitext.find('</translate>', curr) + len('</translate>')
            if last < curr:
                parts.append((wikitext[last:curr], _wrap_in_translate))
            parts.append((wikitext[curr:end_pattern], process_existing_translate))
            curr = end_pattern
            last = curr
            continue
        pattern = '<languages/>'
        if wikitext.startswith(pattern, curr):
            end_pattern = curr + len(pattern)
            if last < curr:
                parts.append((wikitext[last:curr], _wrap_in_translate))
            parts.append((wikitext[curr:end_pattern], lambda x: x))
            curr = end_pattern
            last = curr
            continue
        pattern = '<language>'
        if wikitext.startswith(pattern, curr):
            end_pattern = curr + len('<language>')
            if last < curr:
                parts.append((wikitext[last:curr], _wrap_in_translate))
            parts.append((wikitext[curr:end_pattern], lambda x: x))
            curr = end_pattern
            last = curr
            continue
        pattern = '{|'
        if wikitext.startswith(pattern, curr):
            end_pattern = _find_balanced_close_tag(wikitext, curr, '{|', '|}')
            if last < curr:
                parts.append((wikitext[last:curr], _wrap_in_translate))
            parts.append((wikitext[curr:end_pattern], process_table))
            curr = end_pattern
            last = curr
            continue
        pattern = '<blockquote>'
        if wikitext.startswith(pattern, curr):
            end_pattern = wikitext.find('</blockquote>', curr) + len('</blockquote>')
            if last < curr:
                parts.append((wikitext[last:curr], _wrap_in_translate))
            parts.append((wikitext[curr:end_pattern], process_blockquote))
            curr = end_pattern
            last = curr
            continue
        pattern = '<poem'
        if wikitext.startswith(pattern, curr):
            end_pattern = wikitext.find('</poem>', curr) + len('</poem>')
            if last < curr:
                parts.append((wikitext[last:curr], _wrap_in_translate))
            parts.append((wikitext[curr:end_pattern], process_poem_tag))
            curr = end_pattern
            last = curr
            continue
        pattern = '<center>'
        if wikitext.startswith(pattern, curr):
            end_pattern = wikitext.find('</center>', curr) + len('</center>')
            if last < curr:
                parts.append((wikitext[last:curr], _wrap_in_translate))
            parts.append((wikitext[curr:end_pattern], lambda x: process_formatting_tag(x, "center")))
            curr = end_pattern
            last = curr
            continue
        pattern = '<big>'
        if wikitext.startswith(pattern, curr):
            end_pattern = wikitext.find('</big>', curr) + len('</big>')
            if last < curr:
                parts.append((wikitext[last:curr], _wrap_in_translate))
            parts.append((wikitext[curr:end_pattern], lambda x: process_formatting_tag(x, "big")))
            curr = end_pattern
            last = curr
            continue
        pattern = '<code'
        if wikitext.startswith(pattern, curr):
            end_pattern = wikitext.find('</code>', curr) + len('</code>')
            if last < curr:
                parts.append((wikitext[last:curr], _wrap_in_translate))
            parts.append((wikitext[curr:end_pattern], process_code_tag))
            curr = end_pattern
            last = curr
            continue
        pattern = '<div'
        if wikitext.startswith(pattern, curr) and (
            curr + 4 >= text_length or wikitext[curr + 4] in ('>', ' ', '\t', '\n', '/')
        ):
            end_pattern = _find_balanced_close_tag(
                wikitext, curr, '<div', '</div>',
                open_check_chars={'>', ' ', '\t', '\n', '/'},
            )
            if last < curr:
                parts.append((wikitext[last:curr], _wrap_in_translate))
            parts.append((wikitext[curr:end_pattern], process_div))
            curr = end_pattern
            last = curr
            continue
        pattern = '<hiero>'
        if wikitext.startswith(pattern, curr):
            end_pattern = wikitext.find('</hiero>', curr) + len('</hiero>')
            if last < curr:
                parts.append((wikitext[last:curr], _wrap_in_translate))
            parts.append((wikitext[curr:end_pattern], process_hiero))
            curr = end_pattern
            last = curr
            continue
        pattern = '<sub>'
        if wikitext.startswith(pattern, curr):
            end_pattern = wikitext.find('</sub>', curr) + len('</sub>')
            if last < curr:
                parts.append((wikitext[last:curr], _wrap_in_translate))
            parts.append((wikitext[curr:end_pattern], process_sub_sup))
            curr = end_pattern
            last = curr
            continue
        pattern = '<sup>'
        if wikitext.startswith(pattern, curr):
            end_pattern = wikitext.find('</sup>', curr) + len('</sup>')
            if last < curr:
                parts.append((wikitext[last:curr], _wrap_in_translate))
            parts.append((wikitext[curr:end_pattern], process_sub_sup))
            curr = end_pattern
            last = curr
            continue
        pattern = '<math>'
        if wikitext.startswith(pattern, curr):
            end_pattern = wikitext.find('</math>', curr) + len('</math>')
            if last < curr:
                parts.append((wikitext[last:curr], _wrap_in_translate))
            parts.append((wikitext[curr:end_pattern], process_math))
            curr = end_pattern
            last = curr
            continue
        pattern = '<small>'
        if wikitext.startswith(pattern, curr):
            end_pattern = wikitext.find('</small>', curr) + len('</small>')
            if last < curr:
                parts.append((wikitext[last:curr], _wrap_in_translate))
            parts.append((wikitext[curr:end_pattern], process_small_tag))
            curr = end_pattern
            last = curr
            continue
        pattern = '<nowiki>'
        if wikitext.startswith(pattern, curr):
            end_pattern = wikitext.find('</nowiki>', curr) + len('</nowiki>')
            if last < curr:
                parts.append((wikitext[last:curr], _wrap_in_translate))
            parts.append((wikitext[curr:end_pattern], process_nowiki))
            curr = end_pattern
            last = curr
            continue
        patterns = ['<br>', '<br/>', '<br />']
        for p in patterns:
            if wikitext.startswith(p, curr):
                end_pattern = curr + len(p)
                if last < curr:
                    parts.append((wikitext[last:curr], _wrap_in_translate))
                parts.append((wikitext[curr:end_pattern], lambda x: x))
                curr = end_pattern
                last = curr
                found = True
                break
        if found:
            continue
        patterns_newline = ['\n*', '\n#', '\n:', '\n;']
        if any(wikitext.startswith(p, curr) for p in patterns_newline):
            curr += 1
            parts.append((wikitext[last:curr], _wrap_in_translate))
            patterns = ['*', '#', ':', ';']
            while any(wikitext.startswith(p, curr) for p in patterns):
                end_pattern = wikitext.find('\n', curr)
                if end_pattern == -1:
                    end_pattern = text_length
                else:
                    end_pattern += 1
                parts.append((wikitext[curr:end_pattern], process_item))
                curr = end_pattern
                last = curr
            continue
        pattern = '[['
        if wikitext.startswith(pattern, curr):
            end_pos = curr + 2
            bracket_count = 1
            while end_pos < text_length and bracket_count > 0:
                if wikitext.startswith('[[', end_pos):
                    bracket_count += 1
                    end_pos += 2
                elif wikitext.startswith(']]', end_pos):
                    bracket_count -= 1
                    end_pos += 2
                else:
                    end_pos += 1
            if last < curr:
                parts.append((wikitext[last:curr], _wrap_in_translate))
            if end_pos > curr + 2:
                parts.append((wikitext[curr:end_pos], process_double_brackets))
            curr = end_pos
            last = curr
            continue
        pattern = '[http'
        if wikitext.startswith(pattern, curr):
            end_pos = wikitext.find(']', curr)
            if end_pos == -1:
                end_pos = text_length
            else:
                end_pos += 1
            if last < curr:
                parts.append((wikitext[last:curr], _wrap_in_translate))
            parts.append((wikitext[curr:end_pos + 1], process_external_link))
            curr = end_pos
            last = curr
            continue
        pattern = '{{'
        if wikitext.startswith(pattern, curr):
            end_pos = wikitext.find('}}', curr) + 2
            if end_pos == 1:
                end_pos = text_length
            if last < curr:
                parts.append((wikitext[last:curr], _wrap_in_translate))
            parts.append((wikitext[curr:end_pos], process_template))
            curr = end_pos
            last = curr
            continue
        pattern = 'http'
        if wikitext.startswith(pattern, curr):
            end_pos = wikitext.find(' ', curr)
            if end_pos == -1:
                end_pos = text_length
            if last < curr:
                parts.append((wikitext[last:curr], _wrap_in_translate))
            parts.append((wikitext[curr:end_pos], process_raw_url))
            curr = end_pos
            last = curr
            continue
        for switch in behaviour_switches:
            if wikitext.startswith(switch, curr):
                end_pos = curr + len(switch)
                if last < curr:
                    parts.append((wikitext[last:curr], _wrap_in_translate))
                parts.append((wikitext[curr:end_pos], lambda x: x))
                curr = end_pos
                last = curr

        curr += 1

    if last < text_length:
        parts.append((wikitext[last:], _wrap_in_translate))

    tvar_id = 0
    tvar_url_id = 0
    tvar_code_id = 0
    tvar_inline_icon_id = 0
    for i, (part, handler) in enumerate(parts):
        if handler == process_double_brackets:
            new_part, double_brackets_type = handler(part, tvar_id)
            if double_brackets_type in [
                double_brackets_types.wikilink,
                double_brackets_types.special,
                double_brackets_types.inline_icon,
            ]:
                new_handler = _wrap_in_translate
            else:
                new_handler = lambda x: x
            parts[i] = (new_part, new_handler)
            tvar_id += 1
        elif handler == process_external_link:
            new_part = handler(part, tvar_url_id)
            parts[i] = (new_part, _wrap_in_translate)
            tvar_url_id += 1
        elif handler == process_code_tag:
            new_part = handler(part, tvar_code_id)
            parts[i] = (new_part, _wrap_in_translate)
            tvar_code_id += 1

    _parts = []
    if parts:
        current_part, current_handler = parts[0]
        for part, handler in parts[1:]:
            if handler == _wrap_in_translate and current_handler == _wrap_in_translate:
                current_part += part
            else:
                _parts.append((current_part, current_handler))
                current_part, current_handler = part, handler
        _parts.append((current_part, current_handler))

    processed_parts = [handler(part) for part, handler in _parts]

    return renumber_tvars_per_unit(''.join(processed_parts)[1:])
