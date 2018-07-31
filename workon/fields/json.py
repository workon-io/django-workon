
try:
    from django.contrib.postgres.fields import JSONField
    
except ImportError:
    
    import copy
    from django.db import models
    from django.utils.translation import ugettext_lazy as _
    try:
        from django.utils import six
    except ImportError:
        import six

    try:
        import json
    except ImportError:
        from django.utils import simplejson as json

    from django.forms import fields
    try:
        from django.forms.utils import ValidationError
    except ImportError:
        from django.forms.util import ValidationError

    # This file was copied from django.db.models.fields.subclassing so that we could
    # change the Creator.__set__ behavior. Read the comment below for full details.

    """
    Convenience routines for creating non-trivial Field subclasses, as well as
    backwards compatibility utilities.

    Add SubfieldBase as the __metaclass__ for your Field subclass, implement
    to_python() and the other necessary methods and everything will work seamlessly.
    """


    class SubfieldBase(type):
        """
        A metaclass for custom Field subclasses. This ensures the model's attribute
        has the descriptor protocol attached to it.
        """
        def __new__(cls, name, bases, attrs):
            new_class = super(SubfieldBase, cls).__new__(cls, name, bases, attrs)
            new_class.contribute_to_class = make_contrib(
                new_class, attrs.get('contribute_to_class')
            )
            return new_class


    class Creator(object):
        """
        A placeholder class that provides a way to set the attribute on the model.
        """
        def __init__(self, field):
            self.field = field

        def __get__(self, obj, type=None):
            if obj is None:
                return self
            return obj.__dict__[self.field.name]

        def __set__(self, obj, value):
            # Usually this would call to_python, but we've changed it to pre_init
            # so that we can tell which state we're in. By passing an obj,
            # we can definitively tell if a value has already been deserialized
            # More: https://github.com/bradjasper/django-jsonfield/issues/33
            obj.__dict__[self.field.name] = self.field.pre_init(value, obj)


    def make_contrib(superclass, func=None):
        """
        Returns a suitable contribute_to_class() method for the Field subclass.

        If 'func' is passed in, it is the existing contribute_to_class() method on
        the subclass and it is called before anything else. It is assumed in this
        case that the existing contribute_to_class() calls all the necessary
        superclass methods.
        """
        def contribute_to_class(self, cls, name):
            if func:
                func(self, cls, name)
            else:
                super(superclass, self).contribute_to_class(cls, name)
            setattr(cls, self.name, Creator(self))

        return contribute_to_class
    from django.db.models.query import QuerySet
    from django.utils import six, timezone
    from django.utils.encoding import force_text
    from django.utils.functional import Promise
    import datetime
    import decimal
    import json
    import uuid


    class JSONEncoder(json.JSONEncoder):
        """
        JSONEncoder subclass that knows how to encode date/time/timedelta,
        decimal types, generators and other basic python objects.
        Taken from https://github.com/tomchristie/django-rest-framework/blob/master/rest_framework/utils/encoders.py
        """
        def default(self, obj):  # noqa
            # For Date Time string spec, see ECMA 262
            # http://ecma-international.org/ecma-262/5.1/#sec-15.9.1.15
            if isinstance(obj, Promise):
                return force_text(obj)
            elif isinstance(obj, datetime.datetime):
                representation = obj.isoformat()
                if obj.microsecond:
                    representation = representation[:23] + representation[26:]
                if representation.endswith('+00:00'):
                    representation = representation[:-6] + 'Z'
                return representation
            elif isinstance(obj, datetime.date):
                return obj.isoformat()
            elif isinstance(obj, datetime.time):
                if timezone and timezone.is_aware(obj):
                    raise ValueError("JSON can't represent timezone-aware times.")
                representation = obj.isoformat()
                if obj.microsecond:
                    representation = representation[:12]
                return representation
            elif isinstance(obj, datetime.timedelta):
                return six.text_type(obj.total_seconds())
            elif isinstance(obj, decimal.Decimal):
                # Serializers will coerce decimals to strings by default.
                return float(obj)
            elif isinstance(obj, uuid.UUID):
                return six.text_type(obj)
            elif isinstance(obj, QuerySet):
                return tuple(obj)
            elif hasattr(obj, 'tolist'):
                # Numpy arrays and array scalars.
                return obj.tolist()
            elif hasattr(obj, '__getitem__'):
                try:
                    return dict(obj)
                except:
                    pass
            elif hasattr(obj, '__iter__'):
                return tuple(item for item in obj)
            return super(JSONEncoder, self).default(obj)


    class JSONFormFieldBase(object):
        def __init__(self, *args, **kwargs):
            self.load_kwargs = kwargs.pop('load_kwargs', {})
            super(JSONFormFieldBase, self).__init__(*args, **kwargs)

        def to_python(self, value):
            if isinstance(value, six.string_types) and value:
                try:
                    return json.loads(value, **self.load_kwargs)
                except ValueError:
                    raise ValidationError(_("Enter valid JSON"))
            return value

        def clean(self, value):

            if not value and not self.required:
                return None

            # Trap cleaning errors & bubble them up as JSON errors
            try:
                return super(JSONFormFieldBase, self).clean(value)
            except TypeError:
                raise ValidationError(_("Enter valid JSON"))


    class JSONFormField(JSONFormFieldBase, fields.CharField):
        pass


    class JSONCharFormField(JSONFormFieldBase, fields.CharField):
        pass


    class JSONFieldBase(six.with_metaclass(SubfieldBase, models.Field)):

        def __init__(self, *args, **kwargs):
            self.dump_kwargs = kwargs.pop('dump_kwargs', {
                'cls': JSONEncoder,
                'separators': (',', ':')
            })
            self.load_kwargs = kwargs.pop('load_kwargs', {})

            super(JSONFieldBase, self).__init__(*args, **kwargs)

        def pre_init(self, value, obj):
            """Convert a string value to JSON only if it needs to be deserialized.

            SubfieldBase metaclass has been modified to call this method instead of
            to_python so that we can check the obj state and determine if it needs to be
            deserialized"""

            try:
                if obj._state.adding:
                    # Make sure the primary key actually exists on the object before
                    # checking if it's empty. This is a special case for South datamigrations
                    # see: https://github.com/bradjasper/django-jsonfield/issues/52
                    if getattr(obj, "pk", None) is not None:
                        if isinstance(value, six.string_types):
                            try:
                                return json.loads(value, **self.load_kwargs)
                            except ValueError:
                                raise ValidationError(_("Enter valid JSON"))

            except AttributeError:
                # south fake meta class doesn't create proper attributes
                # see this:
                # https://github.com/bradjasper/django-jsonfield/issues/52
                pass

            return value

        def to_python(self, value):
            """The SubfieldBase metaclass calls pre_init instead of to_python, however to_python
            is still necessary for Django's deserializer"""
            return value

        def get_prep_value(self, value):
            """Convert JSON object to a string"""
            if self.null and value is None:
                return None
            return json.dumps(value, **self.dump_kwargs)

        def value_to_string(self, obj):
            value = self.value_from_object(obj, dump=False)
            return self.get_db_prep_value(value, None)

        def value_from_object(self, obj, dump=True):
            value = super(JSONFieldBase, self).value_from_object(obj)
            if self.null and value is None:
                return None
            return self.dumps_for_display(value) if dump else value

        def dumps_for_display(self, value):
            return json.dumps(value, **self.dump_kwargs)

        def formfield(self, **kwargs):

            if "form_class" not in kwargs:
                kwargs["form_class"] = self.form_class

            field = super(JSONFieldBase, self).formfield(**kwargs)

            if isinstance(field, JSONFormFieldBase):
                field.load_kwargs = self.load_kwargs

            if not field.help_text:
                field.help_text = "Enter valid JSON"

            return field

        def get_default(self):
            """
            Returns the default value for this field.

            The default implementation on models.Field calls force_unicode
            on the default, which means you can't set arbitrary Python
            objects as the default. To fix this, we just return the value
            without calling force_unicode on it. Note that if you set a
            callable as a default, the field will still call it. It will
            *not* try to pickle and encode it.

            """
            if self.has_default():
                if callable(self.default):
                    return self.default()
                return copy.deepcopy(self.default)
            # If the field doesn't have a default, then we punt to models.Field.
            return super(JSONFieldBase, self).get_default()


    class JSONField(JSONFieldBase, models.TextField):
        """JSONField is a generic textfield that serializes/deserializes JSON objects"""
        form_class = JSONFormField

        def dumps_for_display(self, value):
            kwargs = {"indent": 2}
            kwargs.update(self.dump_kwargs)
            return json.dumps(value, ensure_ascii=False, **kwargs)


    class JSONCharField(JSONFieldBase, models.CharField):
        """JSONCharField is a generic textfield that serializes/deserializes JSON objects,
        stored in the database like a CharField, which enables it to be used
        e.g. in unique keys"""
        form_class = JSONCharFormField


    try:
        from south.modelsinspector import add_introspection_rules
        add_introspection_rules([], ["^jsonfield\.fields\.(JSONField|JSONCharField)"])
    except ImportError:
        pass

__all__ = ['JSONField']