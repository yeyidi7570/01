"""Keep the V4 data, images and translation blocks byte-for-byte."""
from pathlib import Path
import re

here = Path(__file__).resolve().parent
out = here.parent.parent
for lang in ('zh', 'kk'):
    original = out / f'math_grade4_lesson1_review_{lang}_v4.html'
    html = original.read_text(encoding='utf-8')
    replacements = {
        r'<style>.*?</style>': '<style>' + (here / 'review.css').read_text() + '</style>',
        r'<section class="review".*?</section>': (here / 'panel.html').read_text(),
        r'<script>.*?</script>': '<script>' + (here / 'review.js').read_text() + '</script>',
    }
    for pattern, content in replacements.items():
        html, count = re.subn(pattern, lambda _match: content.strip(), html, flags=re.S)
        if count != 1:
            raise ValueError(f'Expected one {pattern} in {original.name}, found {count}')
    html = html.replace('  <div class="progress">\n    <div id="statistics"></div>\n    <progress id="meter"></progress>\n    <div id="draft"></div>\n  </div>', '  <div id="draft"></div>')
    file = out / f'math_grade4_lesson1_review_{lang}_v4_continuous.html'
    file.write_text(html, encoding='utf-8')
