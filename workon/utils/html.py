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
    try:
        from bs4 import BeautifulSoup
    except:
        raise ImportError('Beautiful Soup is missing to get html2text. Please pip install "beautifulsoup4>=4.6.0"')
    if html:
        soup = BeautifulSoup(html, "lxml")
        return soup.get_text()
    else:
        return ''

# def strip_tags(value):
#     "Returns the given HTML with all tags stripped"
#     return re.sub(r'<[^>]*?>', '', value)

# def strip_entities(value):
#     "Returns the given HTML with all entities (&something;) stripped"
#     return re.sub(r'&(?:\w+|#\d);', '', value)