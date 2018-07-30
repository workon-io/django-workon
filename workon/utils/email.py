import datetime
import re
from email.utils import parseaddr

from django.conf import settings
from django.core.exceptions import ImproperlyConfigured
from django.core.mail import EmailMultiAlternatives
from django.core.mail import get_connection, EmailMultiAlternatives
from django.core.mail.backends.base import BaseEmailBackend
from django.core.mail.backends.smtp import EmailBackend
from django.core.mail.message import sanitize_address, DEFAULT_ATTACHMENT_MIME_TYPE
from django.template import Context, RequestContext
from django.template.loader import get_template
from django.utils import six
from django.utils.html import strip_tags
from urllib.parse import urlparse
try:
    from premailer import transform
except:
    def premailer(s, *args, **kwargs): return s


_email_regex = re.compile("([a-z0-9!#$%&'*+\/=?^_`{|}~-]+(?:\.[a-z0-9!#$%&'*+\/=?^_`"
                          "{|}~-]+)*(@|\sat\s)(?:[a-z0-9](?:[a-z0-9-]*[a-z0-9])?(\.|"
                          "\sdot\s))+[a-z0-9](?:[a-z0-9-]*[a-z0-9])?)")

__all__ = [
    'EmailStagingBackend',
    'EmailProductionBackend',

    "extract_emails",
    "emails_to_html",
    "extract_emails_to_html",
    "is_valid_email",
    "ContentEmail",
    "HtmlTemplateEmail",
    "send_email",
    "send_mass_email",
    "send_html_email",
    "send_template_email",
    "set_mailchimp_vars",
    "clean_html_for_email",
    "make_email",
    "send_emails",
]


class EmailStagingBackend(EmailBackend):

    def route_recipients(self, recipients):
        return [
            email for name, email in settings.ADMINS
        ]

    def _send(self, message):
        orginial_receiver = ", ".join(message.to)
        message.to = self.route_recipients(message.to)
        message.cc = self.route_recipients(message.cc)
        message.bcc = self.route_recipients(message.bcc)
        message.subject += ' <TESTFOR : %s>' % orginial_receiver
        super()._send(message)


class EmailProductionBackend(EmailBackend):

    def route_recipients(self, recipients):
        return recipients

    def _send(self, message):
        super()._send(message)


def extract_emails(text):
    if text is not None:
        return list(set((email[0] for email in _email_regex.findall(text) if not email[0].startswith('//'))))
    else:
        return []


def emails_to_html(emails, reverse=True, classname=None, divider="<br />"):
    emails = [
        u'<a href="mailto:%s" %s/>%s</a>' % (
            email,
            ('class="%s" ' % classname) if classname else "",
            email.strip('/')
        ) for email in emails
    ]
    if reverse:
        emails.reverse()
    html = divider.join(emails)
    return html


def extract_emails_to_html(text, **kwargs):
    return emails_to_html(extract_emails(text), **kwargs)


def is_valid_email(email):
    if email is None:
        return None
    result = parseaddr(email.strip().lower())
    if '@' in result[1]:
        return result[1]
    else:
        return None


class ContentEmail(EmailMultiAlternatives):
    def __init__(self, subject, content, sender, receivers, content_type=None, context={}, files=[], **kwargs):
        self.is_sent = False

        subject = " ".join(subject.splitlines())
        content = kwargs.pop('body', content)

        if isinstance(receivers, six.string_types):
            receivers = [receivers]

        if content_type:
            super(ContentEmail, self).__init__(
                subject, '', sender, receivers, **kwargs)
        else:
            super(ContentEmail, self).__init__(
                subject, content, sender, receivers, **kwargs)

        if content_type:
            self.attach_alternative(content, content_type)
        if files:
            for file in files:
                # (nom de fichier, contenu, type mime)
                self.attach(*file)


class HtmlTemplateEmail(EmailMultiAlternatives):

    def __init__(self, subject, html, sender, receivers, context={}, files=[], **kwargs):
        self.is_sent = False
        self.html = html

        if isinstance(receivers, six.string_types):
            receivers = [receivers]

        subject = " ".join(subject.splitlines())
        text_template = strip_tags(html)
        if kwargs.get('clean_html') == True:
            kwargs.pop('clean_html')
            self.html = clean_html_for_email(self.html)
        super().__init__(subject, text_template, sender, receivers, **kwargs)
        self.attach_alternative(self.html, "text/html")
        if files:
            for file in files:
                self.attach(*file)

# django : send_mail(subject, message, from_email, recipient_list,
# fail_silently=False, auth_user=None, auth_password=None,
# connection=None, html_message=None)


def send_email(*args, return_email=False, **kwargs):
    fail_silently = kwargs.pop('fail_silently', False)
    message = make_email(*args, **kwargs)
    if return_email:
        message.is_sent = message.send(fail_silently=fail_silently)
        return message
    return message.send(fail_silently=fail_silently)


def make_email(subject, sender, receivers, content=None, html=None, template=None, context={}, content_type=None, files=[], **kwargs):
    if template:
        html_template = get_template(template)
        html = html_template.render(context)
        message = HtmlTemplateEmail(
            subject, html, sender, receivers, context, files=files, **kwargs)
    elif html:
        message = HtmlTemplateEmail(
            subject, html, sender, receivers, context, files=files, **kwargs)
    elif content:
        message = ContentEmail(subject, content, sender, receivers,
                               content_type=content_type, files=files, **kwargs)

    return message


def send_emails(*emails, **kwargs):
    fail_silently = kwargs.pop('fail_silently', False)
    connection = get_connection()
    connection.open()
    check = connection.send_messages(emails)
    connection.close()
    return check


def send_mass_email(messages, **kwargs):
    fail_silently = kwargs.pop('fail_silently', False)
    connection = get_connection()
    connection.open()
    check = connection.send_messages(messages)
    connection.close()
    return check



def send_html_email(subject, sender, receivers, html='', context={}, files=[], **kwargs):
    fail_silently = kwargs.pop('fail_silently', False)
    message = HtmlTemplateEmail(
        subject, html, sender, receivers, context, files=files, **kwargs)
    return message.send(fail_silently=fail_silently)


def send_template_email(subject, sender, receivers, template=None, context={}, files=[], **kwargs):
    html_template = get_template(template)
    context = Context(context)
    html = html_template.render(context)
    return send_html_email(subject, sender, receivers, html=html, context=context, files=files, **kwargs)


def set_mailchimp_vars(template):
    template = template.replace(
        '*|CURRENT_YEAR|*', str(datetime.date.today().year))
    return template


def clean_html_for_email(html):
    return transform(html)
