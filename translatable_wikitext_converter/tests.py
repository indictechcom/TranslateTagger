import unittest

from translatable_wikitext_converter.app import tag_for_translation

class TestTranslatableWikitext(unittest.TestCase):

    def test_section_headers(self):
        self.assertEqual(
            tag_for_translation("==HELLO=="),
            """<translate>\n== HELLO ==\n</translate>""" 
        )

    def test_file_tag_translations(self):
        self.assertEqual(
            tag_for_translation(
                '[[File:landscape.jpg |thumb |left | alt=sunset |Photo of a beautiful landscape]]'
            ),
            '[[File:landscape.jpg|thumb|{{dirstart}}|alt=<translate>sunset</translate>|<translate>Photo of a beautiful landscape</translate>]]'
        )

    def test_internal_and_external_links(self):
        self.assertEqual(
            tag_for_translation(
                'This is a text with an [[internal link]] and an [https://openstreetmap.org external link].'
            ),
            '<translate>This is a text with an [[<tvar name="1">Special:MyLanguage/Internal link</tvar>|internal link]] and an [<tvar name="2">https://openstreetmap.org</tvar> external link].</translate>'
        )
    
    def test_category_with_translation(self):
        self.assertEqual(
            tag_for_translation("[[Category:Wikipedia]]"),
            "[[Category:Wikipedia{{#translation:}}]]"
        )
    
    def test_notoc_preserved(self):
        self.assertEqual(
            tag_for_translation("__NOTOC__"),
            "__NOTOC__"
        )
    
    def test_simple_internal_link(self):
        self.assertEqual(
            tag_for_translation('[[link]]'),
            '<translate>[[<tvar name="1">Special:MyLanguage/Link</tvar>|link]]</translate>'
        )
    
    def test_multiline_text(self):
        self.assertEqual(
            tag_for_translation('\nhi iam charan\n<br>\nhappy\n\n'),
            '<translate>hi iam charan</translate>\n<br>\n<translate>happy</translate>' 
        )
    
    def test_double_namespace_processing(self):
        self.assertEqual(
            tag_for_translation(
                '[[File:pretty hello word.png | alt=Hello everybody!]] [[File:smiley.png|alt=🙂]] How are you?'
            ),
            '[[File:pretty hello word.png|alt=<translate>Hello everybody!</translate>]] <translate><tvar name="1">[[File:smiley.png|alt=🙂]]</tvar> How are you?</translate>'
        )
    
    def test_double_namespace_without_list_case_1(self):
        self.assertEqual(
            tag_for_translation(
                '[[Help]]ing'
            ),
            '<translate>[[<tvar name="1">Special:MyLanguage/Help</tvar>|Help]]ing</translate>'
        )
    
    def test_double_namespace_without_list_case_2(self):
        self.assertEqual(
            tag_for_translation(
                '[[Help]] ing'
            ),
            '<translate>[[<tvar name="1">Special:MyLanguage/Help</tvar>|Help]] ing</translate>'
        )

    def test_template_simple(self):
        self.assertEqual(
            tag_for_translation("{{Template Name}}"),
            "{{Template Name}}"
        )

    def test_template_with_parameters(self):
        self.assertEqual(
            tag_for_translation("{{Template|param1=Value 1|Value 2}}"),
            "{{Template|param1=Value 1|Value 2}}"
        )

    def test_template_nested_in_text(self):
        self.assertEqual(
            tag_for_translation('Some text with {{a template here}} and more text.'),
            '<translate>Some text with</translate> {{A template here}} <translate>and more text.</translate>'
        )

    def test_nowiki_tag(self):
        self.assertEqual(
            tag_for_translation("Some text with <nowiki>[[Raw link]]</nowiki> content."),
            "<translate>Some text with</translate> <nowiki><translate>[[Raw link]]</translate></nowiki> <translate>content.</translate>"
        )
    
    def test_blockquote_tag(self):
        self.assertEqual(
            tag_for_translation("<blockquote>This is a quote.</blockquote>"),
            "<blockquote><translate>This is a quote.</translate></blockquote>"
        )

    def test_poem_tag(self):
        self.assertEqual(
            tag_for_translation("<poem>Line 1\nLine 2</poem>"),
            "<poem><translate>Line 1\nLine 2</translate></poem>"
        )

    def test_code_tag_with_tvar(self):
        # Assuming process_code_tag assigns tvar names sequentially starting from 0
        self.assertEqual(
            tag_for_translation("Here is <code>some code</code> for you."),
            """<translate>Here is <code><tvar name="1">some code</tvar></code> for you.</translate>"""
        )

    def test_div_tag(self):
        self.assertEqual(
            tag_for_translation("<div>Div content here.</div>"),
            "<div><translate>Div content here.</translate></div>"
        )

    def test_hiero_tag(self):
        self.assertEqual(
            tag_for_translation("<hiero>hieroglyphics</hiero>"),
            "<hiero><translate>hieroglyphics</translate></hiero>"
        )

    def test_sub_sup_tags(self):
        self.assertEqual(
            tag_for_translation("H<sub>2</sub>O and E=mc<sup>2</sup>"),
            "<translate>H</translate><sub><translate>2</translate></sub><translate>O and E=mc</translate><sup><translate>2</translate></sup>"
        )

    def test_math_tag(self):
        self.assertEqual(
            tag_for_translation("<math>x^2 + y^2 = z^2</math>"),
            "<math>x^2 + y^2 = z^2</math>"
        )

    def test_small_tag(self):
        self.assertEqual(
            tag_for_translation("<small>Small text</small>"),
            "<small><translate>Small text</translate></small>"
        )
  
    def test_image_with_upright(self):
        self.assertEqual(
            tag_for_translation("[[File:Example.jpg|upright=1.5|A larger image]]"),
            "[[File:Example.jpg|upright=1.5|<translate>A larger image</translate>]]"
        )

    def test_multiple_elements_in_one_line(self):
        self.assertEqual(
            tag_for_translation("Hello world! [[Link]] {{Template}} [https://meta.wikimedia.org/wiki/Main_Page Home]"),
            '<translate>Hello world! [[<tvar name="1">Special:MyLanguage/Link</tvar>|Link]]</translate> {{Template}} <translate>[<tvar name="1">https://meta.wikimedia.org/wiki/Main_Page</tvar> Home]</translate>'
        )

    def test_text_around_br_tag(self):
        self.assertEqual(
            tag_for_translation("First line.<br>Second line."),
            "<translate>First line.</translate><br><translate>Second line.</translate>"
        )

    def test_empty_string_input(self):
        self.assertEqual(
            tag_for_translation(""),
            ""
        )
    
    def test_whitespace_only_input(self):
        self.assertEqual(
            tag_for_translation("   \n\t "),
            "\t"
        )

    def test_list_items(self):
        self.assertEqual(
            tag_for_translation("* Item 1\n** Sub-item 1.1\n* Item 2"),
            "* <translate>Item 1</translate>\n** <translate>Sub-item 1.1</translate>\n* <translate>Item 2</translate>"
        )

    def test_definition_list(self):
        self.assertEqual(
            tag_for_translation(";Term\n:Definition\n:Description"),
            "; <translate>Term</translate>\n: <translate>Definition</translate>\n: <translate>Description</translate>"
        )
        
    def test_standard_internal_link(self):
        # Standard link without prefix or pipe. Should use Special:MyLanguage.
        # Assumes tag_for_translation calls the logic that produces <tvar>...</tvar>
        self.assertEqual(
            tag_for_translation("[[Some Page]]"),
            """<translate>[[<tvar name="1">Special:MyLanguage/Some Page</tvar>|Some Page]]</translate>"""
        )

    def test_internal_link_with_display_text(self):
        # Standard link with display text. Should use Special:MyLanguage.
        self.assertEqual(
            tag_for_translation("[[About|Read more here]]"),
            """<translate>[[<tvar name="1">Special:MyLanguage/About</tvar>|Read more here]]</translate>"""
        )

    def test_simple_language_prefix_no_pipe(self):
        # Link starting with a simple language code (e.g., 'bn:'). Should NOT use Special:MyLanguage.
        # Should auto-generate the display text without the prefix.
        self.assertEqual(
            tag_for_translation("[[:it:mozzarella]]"),
            """<translate>[[<tvar name="1">:it:mozzarella</tvar>|mozzarella]]</translate>"""
        )

    def test_complex_interwiki_prefix(self):
        # Link using a complex interwiki prefix (e.g., :bn:s: for Bengali Wikisource).
        # This tests the segment parsing fix implemented. Should NOT use Special:MyLanguage.
        self.assertEqual(
            tag_for_translation("[[:bn:s:article Title]]"),
            """<translate>[[<tvar name="1">:bn:s:article Title</tvar>|article Title]]</translate>"""
        )

    def test_simple_english_special_handling(self):
        # Link with the 'en:' prefix, which has special handling using the {{lwp|...}} template.
        self.assertEqual(
            tag_for_translation("[[:en:kerala]]"),
            """<translate>[[<tvar name="1">{{lwp|Kerala}}</tvar>|kerala]]</translate>"""
        )
        
    def test_complex_english_special_handling(self):
        # Link with the 'en:' prefix, which has special handling using the {{lwp|...}} template.
        self.assertEqual(
            tag_for_translation("[[:en:kerala|text]]"),
            """<translate>[[<tvar name="1">{{lwp|Kerala}}</tvar>|text]]</translate>"""
        )

if __name__ == '__main__':
    unittest.main(exit=False, failfast=True)
