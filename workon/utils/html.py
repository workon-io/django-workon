from django.shortcuts import render
from django.template.loader import get_template


__all__ = ['render_content', 'sanitize', 'html2text']


def render_content(request, template, context):
    if request:
        return str(render(request, template, context).content, 'utf-8')
    else:
        html_template = get_template(template)
        return html_template.render(context)

def sanitize(html):
    if not has_bleach:
        logger.warning('Bleach is missing for sanitizing HTML.')
        return html
    else:
        return bleach.clean(html)

def html2text(html):
    from bs4 import BeautifulSoup
    soup = BeautifulSoup(html, "lxml")
    return soup.get_text()

# def strip_tags(value):
#     "Returns the given HTML with all tags stripped"
#     return re.sub(r'<[^>]*?>', '', value)

# def strip_entities(value):
#     "Returns the given HTML with all entities (&something;) stripped"
#     return re.sub(r'&(?:\w+|#\d);', '', value)