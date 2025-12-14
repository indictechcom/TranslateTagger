# --- Utility Functions for Wikitext Conversion ---
# This module contains helper functions that are used across the
# wikitext conversion process. These functions handle tasks such as
# capitalising text, checking for emojis, and wrapping text in
# translation tags.

import re, sys

# --- Helper Functions for Processing Different Wikitext Elements ---
# These functions are designed to handle specific wikitext structures.
# Some will recursively call the main `convert_to_translatable_wikitext`
# function to process their internal content, ensuring nested elements
# are also handled correctly.

def capitalise_first_letter(text):
    """
    Capitalises the first letter of the given text.
    If the text is empty or consists only of whitespace, it returns the text unchanged.
    """
    if not text or not text.strip():
        return text
    return text[0].upper() + text[1:]

def is_emoji_unicode(char):
    # This is a very simplified set of common emoji ranges.
    # A comprehensive list would be much longer and more complex.
    # See https://www.unicode.org/Public/emoji/ for full details.
    if 0x1F600 <= ord(char) <= 0x1F64F:  # Emoticons
        return True
    if 0x1F300 <= ord(char) <= 0x1F5FF:  # Miscellaneous Symbols and Pictographs
        return True
    if 0x1F680 <= ord(char) <= 0x1F6FF:  # Transport and Map Symbols
        return True
    if 0x2600 <= ord(char) <= 0x26FF:    # Miscellaneous Symbols
        return True
    if 0x2700 <= ord(char) <= 0x27BF:    # Dingbats
        return True
    # Add more ranges as needed for full coverage
    return False

def _wrap_in_translate(text):
    """
    Wraps the given text with <translate> tags, preserving leading/trailing whitespace.
    """
    if not text or not text.strip():
        return text

    # Logic for finding non-whitespace content (as defined in your current code)
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


############################################
# Functions for Fixing Wiki Page Spacing #
############################################

def fix_section_title_spacing_internal(title: str) -> str:
    """
    Detects a section title and ensures there is exactly one space
    between the '=' characters and the title text.
    """
    # Pattern: (={2,}) [optional space] (.+?) [optional space] \1
    pattern = re.compile(r'(={2,})\s*(.+?)\s*\1', re.DOTALL)

    # Replacement: \1 [space] \2 [space] \1
    return pattern.sub(r'\1 \2 \1', title)

# --- Main Function to Fix Wiki Page Spacing ---

def fix_wiki_page_spacing(wiki_text: str) -> str:
    """
    Applies the section title spacing fix and enforces consistent newlines
    before (one blank line: \n\n) and after (one blank line: \n\n) 
    every section heading (Level 2 or higher).
    
    This method guarantees the output format:
    ...[Content]\n\n== Title ==\n\n[Next content]...
    
    :param wiki_text: The full text of the wiki page.
    :return: The corrected wiki page text.
    """
    
    # Pattern to match and replace a heading and its surrounding whitespace:
    # 1. (.*?)           : Group 1: Non-greedy capture of all content before the heading.
    # 2. [\r\n\s]* : Non-capturing group for all existing whitespace/newlines before the heading.
    # 3. (^={2,}.*?={2,}$) : Group 2: The actual heading line, anchored to the start of a line (re.M).
    # 4. [\n\s]* : Non-capturing group for all existing whitespace/newlines after the heading.
    
    # We use re.M (multiline) and re.DOTALL (dot matches newline)
    heading_and_surroundings_pattern = re.compile(
        r'(.*?)[\r\n\s]*(^={2,}.*?={2,}$)[\r\n\s]*', re.M | re.DOTALL
    )

    def heading_replacer_full_format(match):
        """
        Callback function for re.sub that fixes spacing and enforces \n\n separation.
        """
        # Group 1: Content preceding the heading
        content_before = match.group(1).rstrip()
        # Group 2: The raw heading line
        raw_heading = match.group(2)
        
        # 1. Fix the internal spacing of the heading
        corrected_heading = fix_section_title_spacing_internal(raw_heading)
        
        # 2. Determine the prefix separator: \n\n
        # If the heading is the first thing on the page (i.e., content_before is empty),
        # we don't want to prepend \n\n. Otherwise, we do.
        if content_before:
            prefix = '\n\n'
        else:
            prefix = ''
        
        # 3. The replacement structure:
        # {Content Before}{Prefix}\n{Corrected Heading}\n\n
        # The content that follows this match will immediately follow the final \n\n.
        return f'{content_before}{prefix}{corrected_heading}\n\n'

    # Apply the fix globally
    corrected_text = heading_and_surroundings_pattern.sub(
        heading_replacer_full_format, 
        wiki_text
    )
    
    # Clean up any residual excess newlines at the very beginning of the page
    return corrected_text.lstrip('\n')

# Aggiunto per permettere l'esecuzione del main
if __name__ == '__main__':
    
    # --- Dati di Test ---
    # Contiene vari casi di spaziatura non corretta per le sezioni:
    # 1. Spazi interni errati (sia troppi che mancanti).
    # 2. Spazi esterni errati (troppe newline o nessuna newline).
    # 3. Intestazione all'inizio della pagina (non deve avere \n\n prima).
    # 4. Contenuto in mezzo.
    
    test_wikitext = """

== Ciao ==

ciao
== Ciao ==
ciao
== Ciao ==

ciao
"""

    print("--- Test della funzione fix_wiki_page_spacing ---")
    print("Testo Wiki Originale:\n" + "-"*30)
    print(test_wikitext)
    print("-" * 30)

    # Esecuzione della funzione
    corrected_wikitext = fix_wiki_page_spacing(test_wikitext)

    print("\nTesto Wiki Corretto:\n" + "="*30)
    
    # Usiamo repr() per mostrare chiaramente tutte le newline (\n) e gli spazi
    print(corrected_wikitext)
    print("=" * 30)
    