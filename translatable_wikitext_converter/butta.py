import re

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
    # 4. [\r\n\s]* : Non-capturing group for all existing whitespace/newlines after the heading.
    
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
    return corrected_text.lstrip('\r\n')


def main():
    """Hard-coded wiki page text for testing and debugging."""
    
    # Text demonstrates various input issues:
    # 1. Title 1: No internal space, no newline after content. (Needs \n\n before and after)
    # 2. Title 2: Too much internal space, one newline after content.
    # 3. Title 3: Correct internal space, three newlines after content.
    # 4. Title 4: Starts immediately after content (missing newline before).
    
    raw_wiki_page_text = (
        "This is the header text.\n"
        "This is the last line of the header.\n" # Content before first heading
        "==Topic1==\n\n\n"                       # Missing \n before, too many \n after
        "Content for topic 1.\n"
        "Content continues...\n"
        "===  Topic2  ===\n"                    # Missing \n before, one \n after
        "Content for topic 2.\n"             
        "== Topic3 ==\n\n\n"
        "Content for topic 3. Correct space, too many \n after.\n"
        "Some more content.\n"
        "====Topic4====\n"                      # Missing \n before, missing \n after
        "Final content."
    )

    print("--- Original Wiki Page Text ---\n")
    print(raw_wiki_page_text)
    print("\n" + "="*60 + "\n")

    corrected_text = fix_wiki_page_spacing(raw_wiki_page_text)

    print("--- Corrected Wiki Page Text (Enforcing: \n\n== Title ==\n\n) ---\n")
    print(corrected_text)
    print("\n" + "="*60 + "\n")


if __name__ == '__main__':
    main()