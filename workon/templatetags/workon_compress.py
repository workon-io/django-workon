from django.conf import settings


__all__ = ['lazy_register']


def lazy_register(register):

	if "compressor" in settings.INSTALLED_APPS:
	    @register.tag
	    def compress(parser, token):
	        from compressor.templatetags.compress import compress
	        return compress(parser, token)
	else:
	    @register.to_end_tag
	    def compress(parsed, context, token):
	        return parsed