import re
import datetime
from django.utils.dateformat import format


__all__ = ["ics"]


def ics(
        start_at,
        end_at,
        summary,
        uid=None,
        method="REQUEST",
        prodid="-//Microsoft Corporation//Outlook 10.0 MIMEDIR//EN",
        organizer=None,
        location=None,
        description=None,
        emails=None,
        users=None
    ):

    ics = u"BEGIN:VCALENDAR"
    ics += u"\nPRODID:%s" % prodid
    ics += u"\nVERSION:2.0"
    ics += u"\nMETHOD:%s" % method
    ics += u"\nBEGIN:VEVENT"

    attendees = []
    if users:
        for user in users:
            attendees.append('ATTENDEE;CN=%s;ROLE=REQ-PARTICIPANT;RSVP=TRUE:MAILTO:%s' % (user.get_full_name(), user.email,))
    if attendees:
        ics += "\n" + "\n".join(attendees)
    if organizer:
        ics += "\nORGANIZER:MAILTO:%s" % (organizer, )
    ics += "\nDTSTART:%sZ" % (format(start_at, 'Ymd\THis'),)
    ics += "\nDTEND:%sZ" % (format(end_at, 'Ymd\THis'),)
    ics += "\nDTSTAMP:%sZ" % (format(start_at, 'Ymd\THis'),)
    if location:
        ics += "\nLOCATION:%s" % location
    ics += "\nTRANSP:OPAQUE"
    ics += "\nSEQUENCE:0"
    if uid:
        ics += "\nUID:%s" % uid

    if description:
        ics += "\nDESCRIPTION:%s" % description.replace('\n', '\\n').strip()
    ics += "\nSUMMARY:%s" % summary.replace('\n', '\\n').strip()
    ics += "\nPRIORITY:5"
    ics += "\nCLASS:PUBLIC"
    ics += "\nBEGIN:VALARM"
    ics += "\nTRIGGER:-PT15M"
    ics += "\nACTION:DISPLAY"
    ics += "\nDESCRIPTION:Reminder"
    ics += "\nEND:VALARM"
    ics += "\nEND:VEVENT"
    ics += "\nEND:VCALENDAR"

    return ics

"""
DTSTAMP:20010823T021842Z
DESCRIPTION:When: Wednesday\, August 22\, 2001 7:30 PM-8:00 PM (GMT-08:00)
  Pacific Time (US & Canada)\; Tijuana.\nWhere: my
  office\n\n*~*~*~*~*~*~*~*~*~*\n\n\n
SUMMARY:Important Business Meeting with 15 minute reminder
PRIORITY:5
CLASS:PUBLIC
BEGIN:VALARM
TRIGGER:-PT15M
ACTION:DISPLAY
DESCRIPTION:Reminder
END:VALARM
END:VEVENT
END:VCALENDAR
"""