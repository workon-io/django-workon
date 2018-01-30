import json
import re
import os
from urllib.parse import urlparse, urlencode, parse_qs, urlsplit, urlunsplit
from django.conf import settings
from django import template, forms
from django.templatetags.static import static
from django.template.loader import get_template
from django.utils.safestring import mark_safe
from django.templatetags.static import StaticNode, static as original_static, do_static as original_do_static
from django.core.files.storage import get_storage_class, FileSystemStorage
from django import forms
import workon.utils


__all__ = ['lazy_register']


def lazy_register(register):
    
    @register.filter
    def absolute_url(url): return workon.utils.canonical_url(url)

    @register.filter
    def static(url): return original_static(url)

    @register.filter
    def external_url(url): return workon.utils.append_protocol(url)

    @register.filter
    def absolute_static(url): return absolute_url(original_static(url))

    class AbsoluteStaticNode(StaticNode):
        def url(self, context):
            path = self.path.resolve(context)
            return absolute_url(self.handle_simple(path))

    @register.tag('absolute_static')
    def absolute_static_tag(parser, token): 
        return AbsoluteStaticNode.handle_token(parser, token)

    @register.tag('static')
    def do_static(parser, token):
        return StaticNode.handle_token(parser, token)

    @register.filter
    def static_image(url):
        storage_class = get_storage_class(settings.STATICFILES_STORAGE)
        storage = storage_class()
        image = ImageFile(storage.open(url))
        image.storage = storage
        return image, image.url

    @register.filter
    def replace_urls_to_href(text):
        return mark_safe(workon.utils.replace_urls_to_href(text))

    @register.simple_tag()
    def url_replace_param(url, param_name, param_value):

        scheme, netloc, path, query_string, fragment = urlsplit(url)
        query_params = parse_qs(query_string)

        query_params[param_name] = [param_value]
        new_query_string = urlencode(query_params, doseq=True)

        return mark_safe(urlunsplit((scheme, netloc, path, new_query_string, fragment)))
