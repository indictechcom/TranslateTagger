from enum import Enum
import re, sys

from .wikitranslator_utils import (
    capitalise_first_letter,
    is_emoji_unicode,
    fix_wiki_page_spacing,
    _wrap_in_translate
)

behaviour_switches = ['__NOTOC__', '__FORCETOC__', '__TOC__', '__NOEDITSECTION__', '__NEWSECTIONLINK__', '__NONEWSECTIONLINK__', '__NOGALLERY__', '__HIDDENCAT__', '__EXPECTUNUSEDCATEGORY__', '__NOCONTENTCONVERT__', '__NOCC__', '__NOTITLECONVERT__', '__NOTC__', '__START__', '__END__', '__INDEX__', '__NOINDEX__', '__STATICREDIRECT__', '__EXPECTUNUSEDTEMPLATE__', '__NOGLOBAL__', '__DISAMBIG__', '__EXPECTED_UNCONNECTED_PAGE__', '__ARCHIVEDTALK__', '__NOTALK__', '__EXPECTWITHOUTSCANS__']

def process_syntax_highlight(text):
    """
    Processes <syntaxhighlight> tags in the wikitext.
    It wraps the content in <translate> tags.
    """
    assert(text.startswith('<syntaxhighlight') and text.endswith('</syntaxhighlight>')), "Invalid syntax highlight tag"
    return "<tvar>" + text + "</tvar>"

def process_table(text):
    """
    Processes table blocks in the wikitext.
    It wraps the content in <translate> tags.
    """
    assert(text.startswith('{|') and text.endswith('|}')), "Invalid table tag"
    return text

def process_blockquote(text):
    """
    Processes blockquote tags in the wikitext.
    It wraps the content in <translate> tags.
    """
    assert(text.startswith('<blockquote>') and text.endswith('</blockquote>')), "Invalid blockquote tag"
    start_tag_end = text.find('>') + 1
    end_tag_start = text.rfind('<')
    if start_tag_end >= end_tag_start:
        return text 
    prefix = text[:start_tag_end]
    content = text[start_tag_end:end_tag_start].strip()
    suffix = text[end_tag_start:]
    if not content:
        return text
    # Wrap the content in <translate> tags
    wrapped_content = _wrap_in_translate(content)
    return f"{prefix}{wrapped_content}{suffix}"

def process_poem_tag(text):
    """
    Processes <poem> tags in the wikitext.
    It wraps the content in <translate> tags.
    """
    assert(text.startswith('<poem') and text.endswith('</poem>')), "Invalid poem tag"
    start_tag_end = text.find('>') + 1
    end_tag_start = text.rfind('<')
    if start_tag_end >= end_tag_start:
        return text 
    prefix = text[:start_tag_end]
    content = text[start_tag_end:end_tag_start].strip()
    suffix = text[end_tag_start:]
    if not content:
        return text
    # Wrap the content in <translate> tags
    wrapped_content = _wrap_in_translate(content)
    return f"{prefix}{wrapped_content}{suffix}"

def process_code_tag(text):
    """
    Processes <code> tags in the wikitext.
    It wraps the content in <translate> tags.
    """
    assert(text.startswith('<code') and text.endswith('</code>')), "Invalid code tag"
    # Get inside the <code> tag
    start_tag_end = text.find('>') + 1
    end_tag_start = text.rfind('<')
    if start_tag_end >= end_tag_start:
        return text 
    prefix = text[:start_tag_end]
    content = text[start_tag_end:end_tag_start].strip()
    suffix = text[end_tag_start:]
    if not content:
        return text
    # Wrap the content in <translate> tags
    wrapped_content = f'<tvar>{content}</tvar>'
    return f"{prefix}{wrapped_content}{suffix}"

def process_div(text):
    """
    Processes <div> tags in the wikitext.
    It wraps the content in <translate> tags.
    """
    assert(text.startswith('<div') and text.endswith('</div>')), "Invalid div tag"
    start_tag_end = text.find('>') + 1
    end_tag_start = text.rfind('<')
    if start_tag_end >= end_tag_start:
        return text 
    prefix = text[:start_tag_end]
    content = text[start_tag_end:end_tag_start].strip()
    suffix = text[end_tag_start:]
    if not content:
        return text
    # Wrap the content in <translate> tags
    wrapped_content = _wrap_in_translate(content)
    return f"{prefix}{wrapped_content}{suffix}"

def process_hiero(text):
    """
    Processes <hiero> tags in the wikitext.
    It wraps the content in <translate> tags.
    """
    assert(text.startswith('<hiero>') and text.endswith('</hiero>')), "Invalid hiero tag"
    start_tag_end = text.find('>') + 1
    end_tag_start = text.rfind('<')
    if start_tag_end >= end_tag_start:
        return text 
    prefix = text[:start_tag_end]
    content = text[start_tag_end:end_tag_start].strip()
    suffix = text[end_tag_start:]
    if not content:
        return text
    # Wrap the content in <translate> tags
    wrapped_content = _wrap_in_translate(content)
    return f"{prefix}{wrapped_content}{suffix}"

def process_sub_sup(text):
    """
    Processes <sub> and <sup> tags in the wikitext.
    It wraps the content in <translate> tags.
    """
    assert((text.startswith('<sub>') and text.endswith('</sub>')) or
           (text.startswith('<sup>') and text.endswith('</sup>'))), "Invalid sub/sup tag"
    start_tag_end = text.find('>') + 1
    end_tag_start = text.rfind('<')
    if start_tag_end >= end_tag_start:
        return text 
    prefix = text[:start_tag_end]
    content = text[start_tag_end:end_tag_start].strip()
    suffix = text[end_tag_start:]
    if not content:
        return text
    # Wrap the content in <translate> tags
    wrapped_content = _wrap_in_translate(content)
    return f"{prefix}{wrapped_content}{suffix}"

def process_math(text):
    """
    Processes <math> tags in the wikitext.
    It wraps the content in <translate> tags.
    """
    assert(text.startswith('<math>') and text.endswith('</math>')), "Invalid math tag"
    return text

def process_small_tag(text):
    """
    Processes <small> tags in the wikitext.
    It wraps the content in <translate> tags.
    """
    assert(text.startswith('<small>') and text.endswith('</small>')), "Invalid small tag"
    start_tag_end = text.find('>') + 1
    end_tag_start = text.rfind('<')
    if start_tag_end >= end_tag_start:
        return text 
    prefix = text[:start_tag_end]
    content = text[start_tag_end:end_tag_start].strip()
    suffix = text[end_tag_start:]
    if not content:
        return text
    # Wrap the content in <translate> tags
    wrapped_content = _wrap_in_translate(content)
    return f"{prefix}{wrapped_content}{suffix}"

def process_nowiki(text):
    """
    Processes <nowiki> tags in the wikitext.
    It wraps the content in <translate> tags.
    """
    assert(text.startswith('<nowiki>') and text.endswith('</nowiki>')), "Invalid nowiki tag"
    start_tag_end = text.find('>') + 1
    end_tag_start = text.rfind('<')
    if start_tag_end >= end_tag_start:
        return text 
    prefix = text[:start_tag_end]
    content = text[start_tag_end:end_tag_start].strip()
    suffix = text[end_tag_start:]
    if not content:
        return text
    # Wrap the content in <translate> tags
    wrapped_content = _wrap_in_translate(content)
    return f"{prefix}{wrapped_content}{suffix}"

def process_item(text):
    """
    Processes list items in the wikitext.
    It wraps the content in <translate> tags.
    """
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
    # Add translate tags around the item content
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
    
def _process_file(s): 
    # Define keywords that should NOT be translated when found as parameters
    NON_TRANSLATABLE_KEYWORDS = {
        'left', 'right', 'centre', 'center', 'thumb', 'frameless', 'border', 'none', 
        'upright', 'baseline', 'middle', 'sub', 'super', 'text-top', 'text-bottom', '{{dirstart}}', '{{dirend}}'
    }
    NON_TRANSLATABLE_KEYWORDS_PREFIXES = {
        'link=', 'upright=', 'alt='
    }
    NOT_INLINE_KEYWORDS = {
        'left', 'right', 'centre', 'center', 'thumb', 'frameless', 'border', 'none', '{{dirstart}}', '{{dirend}}'
    }
    file_aliases = ['File:', 'file:', 'Image:', 'image:']

    tokens = []
    
    inner_content = s[2:-2]  # Remove the leading [[ and trailing ]]
    tokens = inner_content.split('|')
    tokens = [token.strip() for token in tokens]  # Clean up whitespace around tokens
    
    # The first token shall start with a file alias
    # e.g., "File:Example.jpg" or "Image:Example.png"
    if not tokens or not tokens[0].startswith(tuple(file_aliases)):
        return line, double_brackets_types.invalid_file
    
    # The first token is a file link
    filename = tokens[0].split(':', 1)[1] if ':' in tokens[0] else tokens[0]
    tokens[0] = f'File:{filename}' 
    
    # Substitute 'left' with {{dirstart}}
    while 'left' in tokens:
        tokens[tokens.index('left')] = '{{dirstart}}'
    # Substitute 'right' with {{dirend}}
    while 'right' in tokens:
        tokens[tokens.index('right')] = '{{dirend}}'
    
    ############################
    # Managing inline icons
    #############################
    is_inline_icon = True
    for token in tokens:
        if token in NOT_INLINE_KEYWORDS:
            is_inline_icon = False
            break
    if is_inline_icon :
        # Check if it contains 'alt=' followed by an emoji
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
        # return something like: <tvar name="icon">[[File:smiley.png|alt=🙂]]</tvar>
        returnline = f'<tvar>[[' + '|'.join(tokens) + ']]</tvar>'
        return returnline, double_brackets_types.inline_icon
    
    ############################
    # Managing general files
    #############################
    
    output_parts = []
    
    # The first token is the file name (e.g., "File:Example.jpg")
    # We substitute any occurrences of "Image:" with "File:"
    output_parts.append(tokens[0])

    pixel_regex = re.compile(r'\d+(?:x\d+)?px')  # Matches pixel values like "100px" or "100x50px)"
    for token in tokens[1:]:
        # Check for 'alt='
        if token.startswith('alt='):
            alt_text = token[len('alt='):].strip()
            output_parts.append('alt='+_wrap_in_translate(alt_text))
        # Check if the token is a known non-translatable keyword
        elif token in NON_TRANSLATABLE_KEYWORDS:
            output_parts.append(token)
        # If the token starts with a known non-translatable prefix, keep it as is
        elif any(token.startswith(prefix) for prefix in NON_TRANSLATABLE_KEYWORDS_PREFIXES):
            output_parts.append(token)
        # If the token is a pixel value, keep it as is
        elif pixel_regex.match(token):
            output_parts.append(token)
        # Otherwise, assume it's a caption or other translatable text
        else:
            output_parts.append(f"<translate>{token}</translate>")

    # Reconstruct the line with the transformed parts
    returnline = '[[' + '|'.join(output_parts) + ']]' 
    return returnline, double_brackets_types.not_inline_icon_file
    
def process_double_brackets(text):
    """
    Processes internal links in the wikitext.
    It wraps the content in <translate> tags.
    """
    if not (text.startswith("[[") and text.endswith("]]")) :
        print(f"Input >{text}< must be wrapped in double brackets [[ ]]")
        sys.exit(1)
    # Split the link into parts, handling both internal links and links with display text
    
    inner_wl = text[2:-2]  # Remove the leading [[ and trailing ]]
    parts = inner_wl.split('|')
    
    # part 0
    category_aliases = ['Category:', 'category:', 'Cat:', 'cat:']
    file_aliases = ['File:', 'file:', 'Image:', 'image:']
    
    # strip all parts
    parts = [part.strip() for part in parts]
    
    # Check if the first part is a category or file alias
    if parts[0].startswith(tuple(category_aliases)):
        # Handle category links
        cat_name = parts[0].split(':', 1)[1] if ':' in parts[0] else parts[0]
        return f'[[Category:{cat_name}{{{{#translation:}}}}]]', double_brackets_types.category
    elif parts[0].startswith(tuple(file_aliases)):
        # Handle file links
        return _process_file(text)
    elif parts[0].startswith('Special:'):
        # Handle special pages
        return f'[[{parts[0]}]]', double_brackets_types.special
    
    #############################
    # Managing wikilinks
    #############################

    # List of recognised prefixes for Wikimedia projects (e.g., wikipedia, commons)
    # and local/national chapters (e.g., wmde, wmit).
    interwiki_prefixes = [
        # Main Projects
        "wikipedia", "w",
        "wiktionary", "wikt",
        "wikinews", "n",
        "wikibooks", "b",
        "wikiquote", "q",
        "wikisource", "s",
        "oldwikisource", "s:mul",
        "wikispecies", "species",
        "wikiversity", "v",
        "wikivoyage", "voy",
        "wikimedia", "foundation", "wmf",
        "commons", "c",
        "metawiki", "metawikimedia", "metawikipedia", "meta", "m",
        "incubator",
        "strategy",
        "mediawikiwiki", "mw",
        "mediazilla", "bugzilla",
        "phabricator", "phab",
        "testwiki",
        "wikidata", "d",
        "wikifunctions", "f",
        "wikitech",
        "toolforge",

        # National Chapters
        "wmar", "wmau", "wmbd", "wmbe", "wmbr", "wmca", "wmcz", "wmdk",
        "wmde", "wmfi", "wmhk", "wmhu", "wmin", "wmid", "wmil", "wmit",
        "wmnl", "wmmk", "wmno", "wmpl", "wmru", "wmrs", "wmes", "wmse",
        "wmch", "wmtw", "wmua", "wmuk",

        # Other Wikimedia Prefixes
        "betawikiversity", "v:mul",
        "download", "dbdump", "gerrit", "mail", "mailarchive",
        "outreach", "otrs", "OTRSwiki", "quality", "spcom",
        "ticket", "tools", "tswiki", "svn", "sulutil",
        "rev", "wmania", "wm2016", "wm2017"
    ]
    # Convert the list to a set for efficient lookup/checking.
    interwiki_prefixes_set = set(interwiki_prefixes)
    # Regex to identify if the link starts with a language code (e.g., 'it:', 'bn:').
    LANGUAGE_CODE_PATTERN = re.compile(r'^[a-z]{2,3}:')

    # Determine the link target (before the pipe) and the display text (after the pipe).
    link_title = parts[0]
    # If a pipe is present, use the part after it; otherwise, use the link target itself.
    display_text = parts[1] if len(parts) > 1 else parts[0]

    # --- 1. Checking for Project/Chapter/Interwiki Prefixes ---

    # We try to extract the prefix (e.g. ":bn:" from ":bn:Page")
    first_part_lower = link_title.lower()

    has_known_prefix = False

    # A. Check 1: Simple Language Code Match (e.g., ":it:", ":bn:")
    # This covers the explicit requirement: "se inizia con un codice linguistico e i due punti..."
    if LANGUAGE_CODE_PATTERN.match(first_part_lower):
        has_known_prefix = True

    # B. Check 2: Complex Prefix Parsing (Covers "w:", "commons:", "wmde:", or combined forms)
    elif ':' in first_part_lower:
        # Split the link by colon, excluding the last part which is the page title.
        # Example: ":bn:s:Page" -> segments: ['','bn','s']
        # Example: ":w:de:Page" -> segments: ['', 'w','de']
        # Example: ":commons:File" -> segments: ['', 'commons']
        
        segments = first_part_lower.split(':')
        
        # We look at all segments except the last one (which is the actual page title).
        # We stop the search if the last segment (the title) is empty, which happens for links ending in a colon.
        # e.g., 'w:' splits to ['w', ''] -> we check 'w'.
        limit = len(segments) - 1
        if segments[-1] == '':
            limit = len(segments) - 2
        
        # Iterate through all prefix segments
        for segment in segments[:limit]:
            # The empty string segment resulting from a leading colon (e.g., ':w:de:Page' -> first segment is '') is ignored.
            if segment:
                # Check if the segment is a known project/chapter prefix.
                if segment in interwiki_prefixes_set:
                    has_known_prefix = True
                    break # Stop checking once any known prefix is found

                # Check if the segment is a language code (e.g., 'de' in 'w:de:Page').
                # We can't use the regex pattern here as it checks for start-of-string.
                # A quick check for typical language code length (2 or 3 chars) is used as a proxy, 
                # although a full language code check would be more robust.
                if 2 <= len(segment) <= 3: 
                    # Assuming a 2/3 letter segment that isn't a known prefix is treated as a language code
                    # for the purpose of avoiding Special:MyLanguage.
                    has_known_prefix = True
                    break
            
    # If the link is complex (multiple colons) or contains a known prefix, 
    # then it is an interwiki link and should not be routed through Special:MyLanguage.
    # The check below remains the same, but 'has_known_prefix' is now robustly set.

    if has_known_prefix or ':' in link_title:
        # If it has a prefix (linguistic or project/chapter), DO NOT use Special:MyLanguage.

        # --- 2. Special handling for the ":en:" prefix ---
        if first_part_lower.startswith(':en:'):
            # For links starting with ':en:', rewrite using the {{lwp|...}} template.
            
            # The suffix is the page title *without* the ":en:" prefix.
            en_suffix = link_title[4:] # Removes ":en:"
            capitalised_en_suffix = capitalise_first_letter(en_suffix)
            # Case 1: No pipe (e.g., "[[en:About]]")
            if len(parts) == 1:
                # Target: {{lwp|About}}. Display text: About (en_suffix).
                return f'[[<tvar>{{{{lwp|{capitalised_en_suffix}}}}}</tvar>|{en_suffix}]]', double_brackets_types.wikilink

            # Case 2: With pipe (e.g., "[[en:About|Read More]]")
            if len(parts) == 2:
                # Target: {{lwp|About}}. Display text: Read More (display_text).
                return f'[[<tvar>{{{{lwp|{capitalised_en_suffix}}}}}</tvar>|{display_text}]]', double_brackets_types.wikilink

        # --- 3. Handling all other interwiki/prefixed links (e.g., ":it:", "w:", "wmde:") ---

        # Find the index of the *last* colon to correctly separate the page title
        # from the potentially complex prefix (e.g., extract 'Page' from 'bn:Page').
        if link_title.rfind(':') != -1:
            # Extract the page title by finding the content after the final colon.
            title_without_prefix = link_title[link_title.rfind(':') + 1:]
        else:
            # Should not happen for prefixed links, but handles the fallback gracefully.
            title_without_prefix = link_title

        # Case 1: No pipe (e.g., "[[bn:Page]]" or "[[w:Page]]")
        if len(parts) == 1:
            # Link target remains link_title (e.g., bn:Page). 
            # Display text is the title *without* the prefix (e.g., Page).
            return f'[[<tvar>{link_title}</tvar>|{title_without_prefix}]]', double_brackets_types.wikilink

        # Case 2: With pipe (e.g., "[[bn:Page|Text]]")
        if len(parts) == 2:
            # Link target remains link_title (e.g., bn:Page). 
            # Display text is the text after the pipe (e.g., Text).
            return f'[[<tvar>{link_title}</tvar>|{display_text}]]', double_brackets_types.wikilink

    # --- 4. Standard internal links (No special prefix found) ---

    # For standard internal links, the target must be prefixed with Special:MyLanguage
    # to enable automatic localisation. 'capitalise_first_letter' is required here.
    
    # Case 1: No pipe (e.g., [[Page]])
    if len(parts) == 1:
        # Target: Special:MyLanguage/Page. Display text: Page (link_title).
        return f'[[<tvar>Special:MyLanguage/{capitalise_first_letter(link_title)}</tvar>|{link_title}]]', double_brackets_types.wikilink

    # Case 2: With pipe (e.g., [[Page|Text]])
    if len(parts) == 2:
        # Target: Special:MyLanguage/Page. Display text: Text (display_text).
        return f'[[<tvar>Special:MyLanguage/{capitalise_first_letter(link_title)}</tvar>|{display_text}]]', double_brackets_types.wikilink

    # Fallback for unexpected link format (e.g., more than one pipe).
    return text

def process_external_link(text):
    """
    Processes external links in the format [http://example.com Description] and ensures
    that only the description part is wrapped in <translate> tags, leaving the URL untouched.
    """
    match = re.match(r'\[(https?://[^\s]+)\s+([^\]]+)\]', text)

    if match:
        url_part = match.group(1)
        description_part = match.group(2)
        # Wrap only the description part in <translate> tags, leave the URL untouched
        return f'[<tvar>{url_part}</tvar> {description_part}]'
    return text

def process_template(text):
    """
    Processes the text to ensure that only the content outside of double curly braces {{ ... }} is wrapped in <translate> tags,
    while preserving the template content inside the braces without translating it.
    """
    assert(text.startswith('{{') and text.endswith('}}')), "Invalid template tag"
    # Split the template content from the rest of the text
    inner_content = text[2:-2].strip()  # Remove the leading {{ and trailing }}
    inner_content = capitalise_first_letter(inner_content)  # Capitalise the first letter of the inner content
    
    # If the inner content is empty, return an empty string
    if not inner_content :
        return text
    
    # Wrap the inner content in <translate> tags
    return '{{' + inner_content + '}}'

def process_raw_url(text):
    """
    Processes raw URLs in the wikitext.
    It wraps the URL in <translate> tags.
    """
    # This function assumes the text is a raw URL, e.g., "http://example.com"
    # and wraps it in <translate> tags.
    if not text.strip():
        return text
    return text.strip()

def tag_for_translation(text):
    converted_text = convert_to_translatable_wikitext(text)
    return set_tvar_names(converted_text)

# --- Main Tokenisation Logic ---

def convert_to_translatable_wikitext(wikitext):
    """
    Converts standard wikitext to translatable wikitext by wrapping
    translatable text with <translate> tags, while preserving and
    correctly handling special wikitext elements.
    This function tokenizes the entire text, not line by line.
    """
    if not wikitext:
        return ""
    
    wikitext = wikitext.replace('\r\n', '\n').replace('\r', '\n')
    wikitext = fix_wiki_page_spacing(wikitext)
    
    # add an extra newline at the beginning, useful to process items at the beginning of the text
    wikitext = '\n' + wikitext

    parts = []
    last = 0
    curr = 0
    text_length = len(wikitext)

    while curr < text_length :
        found = None
        # Syntax highlight block
        pattern = '<syntaxhighlight'
        if wikitext.startswith(pattern, curr):
            end_pattern = wikitext.find('</syntaxhighlight>', curr) + len('</syntaxhighlight>')
            if last < curr:
                parts.append((wikitext[last:curr], _wrap_in_translate))
            parts.append((wikitext[curr:end_pattern], process_syntax_highlight))
            curr = end_pattern
            last = curr
            continue 
        # Table block
        pattern = '{|'
        if wikitext.startswith(pattern, curr):
            end_pattern = wikitext.find('|}', curr) + len('|}')
            if last < curr:
                parts.append((wikitext[last:curr], _wrap_in_translate))
            parts.append((wikitext[curr:end_pattern], process_table))
            curr = end_pattern
            last = curr
            continue
        # Blockquote
        pattern = '<blockquote>'
        if wikitext.startswith(pattern, curr):
            end_pattern = wikitext.find('</blockquote>', curr) + len('</blockquote>')
            if last < curr:
                parts.append((wikitext[last:curr], _wrap_in_translate))
            parts.append((wikitext[curr:end_pattern], process_blockquote))
            curr = end_pattern
            last = curr
            continue
        # Poem tag
        pattern = '<poem'
        if wikitext.startswith(pattern, curr):
            end_pattern = wikitext.find('</poem>', curr) + len('</poem>')
            if last < curr:
                parts.append((wikitext[last:curr], _wrap_in_translate))
            parts.append((wikitext[curr:end_pattern], process_poem_tag))
            curr = end_pattern
            last = curr
            continue
        # Code tag
        pattern = '<code'
        if wikitext.startswith(pattern, curr):
            end_pattern = wikitext.find('</code>', curr) + len('</code>')
            if last < curr:
                parts.append((wikitext[last:curr], _wrap_in_translate))
            parts.append((wikitext[curr:end_pattern], process_code_tag))
            curr = end_pattern
            last = curr
            continue
        # Div tag
        pattern = '<div'
        if wikitext.startswith(pattern, curr):
            end_pattern = wikitext.find('</div>', curr) + len('</div>')
            if last < curr:
                parts.append((wikitext[last:curr], _wrap_in_translate))
            parts.append((wikitext[curr:end_pattern], process_div))
            curr = end_pattern
            last = curr
            continue
        # Hiero tag
        pattern = '<hiero>'
        if wikitext.startswith(pattern, curr):
            end_pattern = wikitext.find('</hiero>', curr) + len('</hiero>')
            if last < curr:
                parts.append((wikitext[last:curr], _wrap_in_translate))
            parts.append((wikitext[curr:end_pattern], process_hiero))
            curr = end_pattern
            last = curr
            continue
        # Sub tag
        pattern = '<sub>'
        if wikitext.startswith(pattern, curr):
            end_pattern = wikitext.find('</sub>', curr) + len('</sub>')
            if last < curr:
                parts.append((wikitext[last:curr], _wrap_in_translate))
            parts.append((wikitext[curr:end_pattern], process_sub_sup))
            curr = end_pattern
            last = curr
            continue
        # Sup tag
        pattern = '<sup>'
        if wikitext.startswith(pattern, curr):
            end_pattern = wikitext.find('</sup>', curr) + len('</sup>')
            if last < curr:
                parts.append((wikitext[last:curr], _wrap_in_translate))
            parts.append((wikitext[curr:end_pattern], process_sub_sup))
            curr = end_pattern
            last = curr
            continue
        # Math tag
        pattern = '<math>'
        if wikitext.startswith(pattern, curr):
            end_pattern = wikitext.find('</math>', curr) + len('</math>')
            if last < curr:
                parts.append((wikitext[last:curr], _wrap_in_translate))
            parts.append((wikitext[curr:end_pattern], process_math))
            curr = end_pattern
            last = curr
            continue
        # Small tag
        pattern = '<small>'
        if wikitext.startswith(pattern, curr):
            end_pattern = wikitext.find('</small>', curr) + len('</small>')
            if last < curr:
                parts.append((wikitext[last:curr], _wrap_in_translate))
            parts.append((wikitext[curr:end_pattern], process_small_tag))
            curr = end_pattern
            last = curr
            continue
        # Nowiki tag
        pattern = '<nowiki>'
        if wikitext.startswith(pattern, curr):
            end_pattern = wikitext.find('</nowiki>', curr) + len('</nowiki>')
            if last < curr:
                parts.append((wikitext[last:curr], _wrap_in_translate))
            parts.append((wikitext[curr:end_pattern], process_nowiki))
            curr = end_pattern
            last = curr
            continue
        # br tag
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
        # Lists
        patterns_newline = ['\n*', '\n#', '\n:', '\n;']
        if any(wikitext.startswith(p, curr) for p in patterns_newline) :
            curr += 1 # Discard the newline character
            parts.append((wikitext[last:curr], _wrap_in_translate))
            # Iterate through the list items
            patterns = ['*', '#', ':', ';']
            while any(wikitext.startswith(p, curr) for p in patterns) :
                end_pattern = wikitext.find('\n', curr)
                if end_pattern == -1:
                    end_pattern = text_length
                else :
                    end_pattern += 1 # Include the newline in the part
                parts.append((wikitext[curr:end_pattern], process_item))
                curr = end_pattern
                last = curr
            continue
        # Internal links
        pattern = '[['
        if wikitext.startswith(pattern, curr):
            # Count the number of opening double brackets '[[' and closing ']]' to find the end
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
            if end_pos > curr + 2:  # Ensure we have a valid link
                parts.append((wikitext[curr:end_pos], process_double_brackets))
            curr = end_pos
            last = curr
            continue
        # External links
        pattern = '[http'
        if wikitext.startswith(pattern, curr):
            # Find the end of the external link
            end_pos = wikitext.find(']', curr)
            if end_pos == -1:
                end_pos = text_length
            else :
                end_pos += 1 # Include the closing ']' in the part
            if last < curr:
                parts.append((wikitext[last:curr], _wrap_in_translate))
            parts.append((wikitext[curr:end_pos + 1], process_external_link))
            curr = end_pos
            last = curr
            continue
        # Templates
        pattern = '{{'
        if wikitext.startswith(pattern, curr):
            # Find the end of the template
            end_pos = wikitext.find('}}', curr) + 2
            if end_pos == 1:
                end_pos = text_length
            if last < curr:
                parts.append((wikitext[last:curr], _wrap_in_translate))
            parts.append((wikitext[curr:end_pos], process_template))
            curr = end_pos
            last = curr
            continue
        # Raw URLs
        pattern = 'http'
        if wikitext.startswith(pattern, curr):
            # Find the end of the URL (space or end of string)
            end_pos = wikitext.find(' ', curr)
            if end_pos == -1:
                end_pos = text_length
            if last < curr:
                parts.append((wikitext[last:curr], _wrap_in_translate))
            parts.append((wikitext[curr:end_pos], process_raw_url))
            curr = end_pos
            last = curr
            continue
        # Behaviour switches
        for switch in behaviour_switches:
            if wikitext.startswith(switch, curr):
                end_pos = curr + len(switch)
                if last < curr:
                    parts.append((wikitext[last:curr], _wrap_in_translate))
                parts.append((wikitext[curr:end_pos], lambda x: x))
                curr = end_pos
                last = curr
                
        
        curr += 1  # Move to the next character if no pattern matched
        
    # Add any remaining text after the last processed part
    if last < text_length:
        parts.append((wikitext[last:], _wrap_in_translate))
    
    """
    print ('*' * 20)
    for i, (part, handler) in enumerate(parts):
        print(f"--- Start element {i} with handler {handler.__name__} ---")
        print(part) 
        print(f"---\n") 
        
    print ('*' * 20)
    """
    
    # Process links
    for i, (part, handler) in enumerate(parts):
        # Handlers for links require a tvar_id
        if handler == process_double_brackets:
            new_part, double_brackets_type = handler(part)
            if double_brackets_type in [double_brackets_types.wikilink, double_brackets_types.special, double_brackets_types.inline_icon]:
                new_handler = _wrap_in_translate  # Change handler to _wrap_in_translate
            else :
                new_handler = lambda x: x  # No further processing for categories and files
            parts[i] = (new_part, new_handler)
        elif handler == process_external_link:
            new_part = handler(part)
            new_handler = _wrap_in_translate  # Change handler to _wrap_in_translate
            parts[i] = (new_part, new_handler)
        elif handler == process_code_tag:
            new_part = handler(part)
            new_handler = _wrap_in_translate  # Change handler to _wrap_in_translate
            parts[i] = (new_part, new_handler)
        elif handler == process_double_brackets :
            new_part, double_brackets_type = handler(part)
            if double_brackets_type == double_brackets_types.inline_icon:
                new_handler = _wrap_in_translate  # Change handler to _wrap_in_translate
            else:
                new_handler = lambda x: x
        elif handler == process_syntax_highlight :
            new_part = handler(part)
            new_handler = _wrap_in_translate  # Change handler to _wrap_in_translate
            parts[i] = (new_part, new_handler)
            
    # Scan again the parts: merge consecutive parts handled by _wrap_in_translate
    _parts = []
    if parts:
        current_part, current_handler = parts[0]
        for part, handler in parts[1:]:
            if handler == _wrap_in_translate and current_handler == _wrap_in_translate:
                # Merge the parts
                current_part += part
            else:
                _parts.append((current_part, current_handler))
                current_part, current_handler = part, handler
        # Add the last accumulated part
        _parts.append((current_part, current_handler))
        
    # Process the parts with their respective handlers
    processed_parts = [handler(part) for part, handler in _parts]            
    
    # Debug output
    """
    print("Processed parts:")
    for i, (ppart, (part, handler)) in enumerate(zip(processed_parts, _parts)):
        print(f"--- Start element {i} with handler {handler.__name__} ---")
        print(f"@{part}@")
        print(f"---\n") 
        print(f'@{ppart}@')  
        print(f"---\n") 
    """
    
    # Join the processed parts into a single string
    out_wikitext =  ''.join(processed_parts)
    
    # Keep removing all trailing and leading newlines and spaces
    while out_wikitext.startswith('\n') or out_wikitext.startswith(' ') or out_wikitext.endswith('\n') or out_wikitext.endswith(' '):
        out_wikitext = out_wikitext.strip('\n')
        out_wikitext = out_wikitext.strip(' ')
    
    return out_wikitext

def set_tvar_names(input_text: str) -> str:
    """
    Sets the 'name' attribute of every <tvar> tag inside a <translate> block,
    using an increasing counter (starting from 1) for each <translate> block.

    This version assumes <tvar> tags are initially simple, e.g., <tvar> or <tvar/>.

    Args:
        input_text: The input string containing <translate> and <tvar> tags.

    Returns:
        The modified string with the 'name' attributes set.
    """

    # 1. Regular expression to find all <translate> blocks, including content.
    # We use re.DOTALL to ensure the match spans multiple lines.
    translate_pattern = re.compile(r'(<translate>.*?<\/translate>)', re.DOTALL)

    def process_translate_block(full_block_match):
        """
        Callback function for re.sub that processes one <translate> block.
        It finds all simple <tvar> tags inside and gives them an incremental 'name' attribute.
        """
        # The entire matched <translate> block
        full_block = full_block_match.group(0)
        
        # Initialise the counter for the current block
        count = 1
        
        def substitute_simple_tvar(tvar_match):
            """
            Inner callback function to substitute a simple <tvar> and increment the counter.
            """
            nonlocal count
            
            # The match group 1 captures the opening tag parts: '<tvar'
            opening_part = tvar_match.group(1)
            
            # Construct the modified tag: insert name="count" before the closing bracket
            # We assume a simple structure like <tvar> becomes <tvar name="1">
            # or <tvar/> becomes <tvar name="1"/>
            
            # This expression handles both <tvar> and <tvar/> by replacing the final '>' or '/>'
            # with the insertion plus the captured closing part (group 2).
            name_attribute = f' name="{count}"'
            
            # Group 2 captures the closing element (either '>' or '/>')
            closing_part = tvar_match.group(2)
            
            new_tag = f'{opening_part}{name_attribute}{closing_part}'
            
            # Increment the counter for the next <tvar>
            count += 1
            
            return new_tag
            
        # Internal pattern: finds <tvar> or <tvar/> where 'name' is not present.
        # This is a robust pattern for HTML/XML tags where an attribute is to be inserted
        # right before the closing bracket.
        
        # Group 1: (<tvar\s*) - The opening tag up to the first space/end
        # Group 2: (/?\s*>) - The closing angle bracket (possibly with / for self-closing)
        # We need to ensure we don't accidentally match existing 'name' attributes.
        
        # Simpler pattern for *all* <tvar> tags, assuming no existing name:
        tvar_pattern_inner = re.compile(r'(<tvar\s*)(/?\s*>)', re.DOTALL)

        # To strictly avoid tags that *already* contain 'name':
        # We use a negative lookahead to ensure "name=" is not present inside <tvar...>
        # This pattern is more complex but safer:
        tvar_pattern_safer = re.compile(r'(<tvar(?![^>]*name=)[^>]*)(>)', re.IGNORECASE | re.DOTALL)
        
        # We will utilise the simpler pattern, assuming the context is pre-processing before translation:
        tvar_pattern_to_use = re.compile(r'(<tvar\s*)(/?\s*>)', re.DOTALL)

        # Apply the substitution to all <tvar> tags within the current block
        modified_block = re.sub(
            tvar_pattern_to_use,
            substitute_simple_tvar,
            full_block
        )
        
        return modified_block
        
    # 2. Apply the block processor function to all <translate> blocks.
    final_result = re.sub(
        translate_pattern,
        process_translate_block,
        input_text
    )
    
    return final_result