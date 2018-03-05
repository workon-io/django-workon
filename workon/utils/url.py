import re, os, functools
import sys
from urllib.parse import urlparse, urlunparse
from django.conf.urls import url
from django.apps import apps
from django.conf import settings
from django.contrib.sites.shortcuts import get_current_site
from django.urls import reverse, exceptions, NoReverseMatch
from django.http.request import HttpRequest
from django.core.exceptions import SuspiciousOperation
from workon.utils.cache import memoize

_url_composite = r"""(?i)\b((?:https?:(?:/{1,3}|[a-z0-9%])|[a-z0-9.\-]+[.](?:com|net|org|edu|gov|mil|aero|asia|biz|cat|coop|info|int|jobs|mobi|museum|name|post|pro|tel|travel|xxx|ac|ad|ae|af|ag|ai|al|am|an|ao|aq|ar|as|at|au|aw|ax|az|ba|bb|bd|be|bf|bg|bh|bi|bj|bm|bn|bo|br|bs|bt|bv|bw|by|bz|ca|cc|cd|cf|cg|ch|ci|ck|cl|cm|cn|co|cr|cs|cu|cv|cx|cy|cz|dd|de|dj|dk|dm|do|dz|ec|ee|eg|eh|er|es|et|eu|fi|fj|fk|fm|fo|fr|ga|gb|gd|ge|gf|gg|gh|gi|gl|gm|gn|gp|gq|gr|gs|gt|gu|gw|gy|hk|hm|hn|hr|ht|hu|id|ie|il|im|in|io|iq|ir|is|it|je|jm|jo|jp|ke|kg|kh|ki|km|kn|kp|kr|kw|ky|kz|la|lb|lc|li|lk|lr|ls|lt|lu|lv|ly|ma|mc|md|me|mg|mh|mk|ml|mm|mn|mo|mp|mq|mr|ms|mt|mu|mv|mw|mx|my|mz|na|nc|ne|nf|ng|ni|nl|no|np|nr|nu|nz|om|pa|pe|pf|pg|ph|pk|pl|pm|pn|pr|ps|pt|pw|py|qa|re|ro|rs|ru|rw|sa|sb|sc|sd|se|sg|sh|si|sj|Ja|sk|sl|sm|sn|so|sr|ss|st|su|sv|sx|sy|sz|tc|td|tf|tg|th|tj|tk|tl|tm|tn|to|tp|tr|tt|tv|tw|tz|ua|ug|uk|us|uy|uz|va|vc|ve|vg|vi|vn|vu|wf|ws|ye|yt|yu|za|zm|zw)/)(?:[^\s()<>{}\[\]]+|\([^\s()]*?\([^\s()]+\)[^\s()]*?\)|\([^\s]+?\))+(?:\([^\s()]*?\([^\s()]+\)[^\s()]*?\)|\([^\s]+?\)|[^\s`!()\[\]{};:'".,<>?«»“”‘’])|(?:(?<!@)[a-z0-9]+(?:[.\-][a-z0-9]+)*[.](?:com|net|org|edu|gov|mil|aero|asia|biz|cat|coop|info|int|jobs|mobi|museum|name|post|pro|tel|travel|xxx|ac|ad|ae|af|ag|ai|al|am|an|ao|aq|ar|as|at|au|aw|ax|az|ba|bb|bd|be|bf|bg|bh|bi|bj|bm|bn|bo|br|bs|bt|bv|bw|by|bz|ca|cc|cd|cf|cg|ch|ci|ck|cl|cm|cn|co|cr|cs|cu|cv|cx|cy|cz|dd|de|dj|dk|dm|do|dz|ec|ee|eg|eh|er|es|et|eu|fi|fj|fk|fm|fo|fr|ga|gb|gd|ge|gf|gg|gh|gi|gl|gm|gn|gp|gq|gr|gs|gt|gu|gw|gy|hk|hm|hn|hr|ht|hu|id|ie|il|im|in|io|iq|ir|is|it|je|jm|jo|jp|ke|kg|kh|ki|km|kn|kp|kr|kw|ky|kz|la|lb|lc|li|lk|lr|ls|lt|lu|lv|ly|ma|mc|md|me|mg|mh|mk|ml|mm|mn|mo|mp|mq|mr|ms|mt|mu|mv|mw|mx|my|mz|na|nc|ne|nf|ng|ni|nl|no|np|nr|nu|nz|om|pa|pe|pf|pg|ph|pk|pl|pm|pn|pr|ps|pt|pw|py|qa|re|ro|rs|ru|rw|sa|sb|sc|sd|se|sg|sh|si|sj|Ja|sk|sl|sm|sn|so|sr|ss|st|su|sv|sx|sy|sz|tc|td|tf|tg|th|tj|tk|tl|tm|tn|to|tp|tr|tt|tv|tw|tz|ua|ug|uk|us|uy|uz|va|vc|ve|vg|vi|vn|vu|wf|ws|ye|yt|yu|za|zm|zw)\b/?(?!@)))"""
_url_regex = re.compile(_url_composite)
_url_regex_multiline = re.compile(_url_composite, re.MULTILINE|re.UNICODE)

__all__ = [
    'urlify',
    'append_protocol',
    'extract_urls',
    'urls_to_html',
    'extract_urls_to_html',
    'replace_urls_to_href',
    'get_current_site_domain',
    'build_absolute_url',
    'get_current_site',
    'external_url',
    'canonical_url',
    'canonical_url_static',
    'absolute_url',
    'url_signature',
    'default_redirect',
    'ensure_safe_url',
]


# _urlfinderregex = re.compile(r'''http[s]?://(?:[a-zA-Z]|[0-9]|[$-_@.&+^"']|[!*\(\),^"']|(?:%[0-9a-fA-F][0-9a-fA-F]))+''', re.MULTILINE|re.UNICODE)
def urlify(text, reverse=True, target="_blank", hide_protocol=True, classname=None, divider="<br />"):
    if not text:
        return text

    def replacewithlink(matchobj):
        url = matchobj.group(0)
        sin = matchobj.start()
        bef2 = text[sin-2:sin]
        if bef2 != '="' and bef2 != "='":
            postfix = ''
            url_postfix = url.split('&nbsp')
            if len(url_postfix) > 1:
                url = url_postfix[0]
                postfix = f'&nbsp{url_postfix[-1]}'
            return f'<a href="{url.strip()}" target="_blank" rel="nofollow">{url}</a>{postfix}'
        else:
            return url

    if text != None and text != '':
        return _url_regex_multiline.sub(replacewithlink, text)
    else:
        return ''

def append_protocol(url):
    if url:
        if not (url.startswith('http://') or url.startswith('https://')):
            url = f"http://{url}"
    return url

def extract_urls(text):
    if text is not None:
        urls = []
        for url in _url_regex.findall(text):
            if not url.startswith('//'):
                urls.append(append_protocol(url))

        return list(set(urls))
    else:
        return []

def urls_to_html(urls, reverse=True, target="_blank", hide_protocol=True, classname=None, divider="<br />"):
    if not urls:
        return urls
    urls = [
        u'<a %shref="%s" %s/>%s</a>' % (
            ('target="%s" ' % target) if target else "",
            url,
            ('class="%s" ' % classname) if classname else "",
            (url.replace('https://', '').replace('http://', '') if hide_protocol else url).strip('/')
        ) for url in urls
    ]
    if reverse:
        urls.reverse()
    html = divider.join(urls)
    return html

def extract_urls_to_html(text, **kwargs):
    return urls_to_html(extract_urls(text), **kwargs)


def replace_urls_to_href(text, target="_blank", hide_protocol=True):
    if not text:
        return text
    text = _url_regex_multiline.sub(r'<a href="http://\1" %s rel="nofollow">\1</a>' % (
        ('target="%s" ' % target) if target else ""
    ), text)
    text = text.replace('http://http', 'http')
    # Replace email to mailto
    # urls = re.compile(r"([\w\-\.]+@(\w[\w\-]+\.)+[\w\-]+)", re.MULTILINE|re.UNICODE)
    # value = urls.sub(r'<a href="mailto:\1">\1</a>', value)
    return text

# urlfinder = re.compile("([0-9]{1,3}\\.[0-9]{1,3}\\.[0-9]{1,3}\\.[0-9]{1,3}|((news|telnet|nttp|file|http|ftp|https)://)|(www|ftp)[-A-Za-z0-9]*\\.)[-A-Za-z0-9\\.]+):[0-9]*)?/[-A-Za-z0-9_\\$\\.\\+\\!\\*\\(\\),;:@&=\\?/~\\#\\%]*[^]'\\.}>\\),\\\"]")

# def urlify2(value):
#     return urlfinder.sub(r'<a href="\1">\1</a>', value)

def get_current_site_domain(request=None):
    try:
        from django.contrib.sites.models import Site
        domain = Site.objects.get_current().domain
    except:
        domain = getattr(settings, 'APP_DOMAIN', '')
    return domain

def build_absolute_url(url="", request=None):
    domain = get_current_site_domain(request=request)
    return "{0}://{1}{2}".format(
        getattr(settings, "DEFAULT_HTTP_PROTOCOL", "http"),
        domain.split('//')[-1],
        url
    ).strip('/')


def external_url(url):
    if not url.startswith('http') and not url.startswith('//'):
        return f"http://{url}"
    return url


def canonical_url(url, domain_check=False):
    """
    Ensure that the url contains the `http://mysite.com` part,
    particularly for requests made on the local dev server
    """

    domain = get_current_site_domain()
    if not domain.startswith('http') and not domain.startswith('//'):
        domain = f"http://{domain}"

    if not url.startswith('http') and not url.startswith('//'):
        url = os.path.join(domain, url.lstrip('/'))

    if domain_check:
        url_parts = URL(url)
        current_site_parts = URL(URL().domain(domain).as_string())
        if url_parts.subdomains()[-2:] != current_site_parts.subdomains()[-2:]:
            raise ValueError("Suspicious domain '%s' that differs from the "
                "current Site one '%s'" % (url_parts.domain(), current_site_parts.domain()))

    return url

def absolute_url(*args, **kwargs):
    return canonical_url(*args, **kwargs)

def canonical_url_static(url, domain_check=False):# False because of S3
    """
    Ensure that the url contains the `http://mysite.com/STATIC_URL` part,
    particularly for requests made on the local dev server
    """
    if url.startswith('http') or url.startswith('//'):
        return url
    return canonical_url( os.path.join(settings.STATIC_URL, url), domain_check)


def url_signature(resolver_match):
    """
    Convert
        a `django.core.urlresolvers.ResolverMatch` instance
        usually retrieved from a `django.core.urlresolvers.resolve` call
    To
        'namespace:view_name'

    that `django.core.urlresolvers.reverse` can use
    """
    signature = resolver_match.url_name
    if resolver_match.namespace:
        signature = "%s:%s" % (resolver_match.namespace, signature)
    return signature


def default_redirect(request, fallback_url, **kwargs):
    redirect_field_name = kwargs.get("redirect_field_name", "next")
    next_url = request.POST.get(redirect_field_name, request.GET.get(redirect_field_name))
    if not next_url:
        # try the session if available
        if hasattr(request, "session"):
            session_key_value = kwargs.get("session_key_value", "redirect_to")
            if session_key_value in request.session:
                next_url = request.session[session_key_value]
                del request.session[session_key_value]
    is_safe = functools.partial(
        ensure_safe_url,
        allowed_protocols=kwargs.get("allowed_protocols"),
        allowed_host=request.get_host()
    )
    if next_url and is_safe(next_url):
        return next_url
    else:
        try:
            fallback_url = reverse(fallback_url)
        except NoReverseMatch:
            if callable(fallback_url):
                raise
            if "/" not in fallback_url and "." not in fallback_url:
                raise
        # assert the fallback URL is safe to return to caller. if it is
        # determined unsafe then raise an exception as the fallback value comes
        # from the a source the developer choose.
        is_safe(fallback_url, raise_on_fail=True)
        return fallback_url


def ensure_safe_url(url, allowed_protocols=None, allowed_host=None, raise_on_fail=False):
    if allowed_protocols is None:
        allowed_protocols = ["http", "https"]
    parsed = urlparse(url)
    # perform security checks to ensure no malicious intent
    # (i.e., an XSS attack with a data URL)
    safe = True
    if parsed.scheme and parsed.scheme not in allowed_protocols:
        if raise_on_fail:
            raise SuspiciousOperation("Unsafe redirect to URL with protocol '{0}'".format(parsed.scheme))
        safe = False
    if allowed_host and parsed.netloc and parsed.netloc != allowed_host:
        if raise_on_fail:
            raise SuspiciousOperation("Unsafe redirect to URL not matching host '{0}'".format(allowed_host))
        safe = False
    return safe
