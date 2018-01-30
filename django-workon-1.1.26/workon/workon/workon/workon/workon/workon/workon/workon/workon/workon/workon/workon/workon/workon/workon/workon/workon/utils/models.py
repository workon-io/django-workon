__all__ = ['m2m_auto_create']

def m2m_auto_create(instance, field_name, active=True):
    getattr(instance._meta.model, field_name).through._meta.auto_created = active