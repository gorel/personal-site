import jinja2

from personal_site import constants


def safe_html(s):
    # Jinja2 + markdown will double-escape inside code blocks, so we need to
    # manually extract code blocks before escaping for jinja, then restore the
    # code blocks afterwards
    regex = constants.MARKDOWN_CODE_PATTERN
    md_code_template = "_%_%_MARKDOWN_CODE_SAVE_TEMPLATE_{i}_%_%_"

    # Saving code blocks
    saved_code_blocks = []
    for i, (match, _) in enumerate(regex.findall(s)):
        saved_code_blocks.append(match)
        s = s.replace(match, md_code_template.format(i=i), 1)

    # Normal jinja2 escaping
    # We convert to string because otherwise jinja2 will escape replaced text
    s = str(jinja2.escape(s))

    # Restore code blocks
    for i, saved_code_block in enumerate(saved_code_blocks):
        old = md_code_template.format(i=i)
        s = s.replace(old, saved_code_block, 1)
    return s
