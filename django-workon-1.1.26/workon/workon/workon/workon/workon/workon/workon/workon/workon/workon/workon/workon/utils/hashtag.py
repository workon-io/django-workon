import re
from django.utils.safestring import mark_safe
from django.utils.html import escape
from html import unescape

__all__ = [
    'HASTAG_RE', 
    'replace_hashtags_with_hrefs', 
    'iter_hashtags',
    'iter_hashtags_at'
]

HASTAG_RE = re.compile(r'''[^&](\#([\'\"\w\-\_\d]+))''')
HASTAG_AT_RE = re.compile(r'''[^&](\@([\'\"\w\-\_\d]+))''')

HASTAG_RE_SEARCH = re.compile(r'''(\#([\'\"\w\-\_\d]+))''')
HASTAG_AT_RE_SEARCH = re.compile(r'''(\@([\'\"\w\-\_\d]+))''')

def replace_hashtags_with_hrefs(text, href='#{hastag}', label='#{hastag}'):
    text = unescape(text)
    href = href.format(hastag='\\2')
    label = label.format(hastag='\\2')
    html = HASTAG_RE.sub(f' <a href="{href}">{label}</a>', text)
    return mark_safe(html)


def iter_hashtags(text):
    if text:
        for full_hashtag, hashtag in HASTAG_RE_SEARCH.findall(text):
            yield hashtag

def iter_hashtags_at(text):
    if text:
        for full_hashtag, hashtag in HASTAG_AT_RE_SEARCH.findall(text):
            yield hashtag

def lazy_register(register):

    @register.filter(name='replace_hashtags_with_hrefs')
    def tt_replace_hashtags_with_hrefs(text, *args): return replace_hashtags_with_hrefs(text, *args)
