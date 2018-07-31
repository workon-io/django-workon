from django.db import models
from workon.forms import EmbedInput
from workon.forms.embed import EMBED_TYPES
# - Youtube
# - Soundcloud
# - Vimeo
# - Bandcamp
# - Pinterest
# - Mixcloud
# - Dailymotion

__all__ = ['EmbedField']


class EmbedDescriptor(object):

    def __init__(self, field):
        self.field = field

    def __get__(self, instance=None, owner=None):
        if instance is None:
            raise AttributeError(
                "The '%s' attribute can only be accessed from %s instances."
                % (self.field.name, owner.__name__))


        value = instance.__dict__[self.field.name]

        if value in [None, False, '']:
            value = None

        elif isinstance(value, six.string_types):

            for type_name, patterns in EMBED_TYPES.items():
                for pattern in patterns:
                    # regex = re.compile(pattern)
                    result = re.search(pattern[0], type_value[0])
                    if result:
                        is_embed = True
                        value_type = type_name
                        value = MediaFieldEmbed(instance, self.field, result.group(0), type=value_type)

                    else:
                        value_type = 'youtube'
                        value = MediaFieldEmbed(instance, self.field, type_value[0], type=value_type)
                # value_type = 'youtube'
                # value = MediaFieldEmbed(instance, self.field, type_value[0], type=value_type)

            else:
                value_type = type_value[0]
                if value_type in ['image']:
                    value = MediaFieldImage(instance, self.field, type_value[1])
                else:
                    value = MediaFieldEmbed(instance, self.field, type_value[1], type=value_type)


            # value = 'image|%s' % name
            # attr = self.field.attr_class(instance, self.field, value)
            # instance.__dict__[self.field.name] = attr

        # Other types of files may be assigned as well, but they need to have
        # the FieldFile interface added to them. Thus, we wrap any other type of
        # File inside a FieldFile (well, the field's attr_class, which is
        # usually FieldFile).
        elif (isinstance(value, File)) and \
            not isinstance(value, MediaFieldImage):
            value = MediaFieldImage(instance, self.field, value.name)
            value.file = instance.__dict__[self.field.name]
            value._committed = False

        # Finally, because of the (some would say boneheaded) way pickle works,
        # the underlying FieldFile might not actually itself have an associated
        # file. So we need to reset the details of the FieldFile in those cases.
        elif isinstance(value, MediaFieldImage): # and not hasattr(value, 'field'):
            value.instance = instance
            value.field = self.field
            value.storage = self.field.storage
            # print "Already an image", value.name

        # Finally, because of the (some would say boneheaded) way pickle works,
        # the underlying FieldFile might not actually itself have an associated
        # file. So we need to reset the details of the FieldFile in those cases.
        elif isinstance(value, MediaFieldEmbed): # and not hasattr(value, 'field'):
            value.instance = instance
            value.field = self.field

        else:
            value = None

        instance.__dict__[self.field.name] = value
        return instance.__dict__[self.field.name]

    def __set__(self, instance, value):
        instance.__dict__[self.field.name] = value


class EmbedField(models.TextField):
    descriptor_class = EmbedDescriptor

    def __init__(self, *args, **kwargs):

        self.authorized_types = ['image', 'youtube', 'dailymotion']
        if kwargs.get('authorized_types'):
            self.authorized_types = kwargs.pop('authorized_types')

        kwargs['max_length'] = 255

        super(EmbedField, self).__init__(*args, **kwargs)


    def formfield(self, **kwargs):
        defaults = { 'widget': EmbedInput }
        defaults.update(kwargs)
        # defaults['form_class'] = EmbedField
        defaults['widget'] = EmbedInput(
            attrs = { 'class': 'image-ratio', },
            authorized_types = self.authorized_types,
        )
        return super(EmbedField, self).formfield(**defaults)

