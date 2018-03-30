from datetime import datetime, timedelta, date as odate
from collections import namedtuple
import bisect

__all__ = [
    'week_range', 

    'first_day_of_quarter',
    'last_day_of_quarter',
    'quarter_range', 

    'first_day_of_month',
    'last_day_of_month',
    'month_range', 

    'next_month', 

    'get_week_number',

    'get_weeks_of_year',

    'Week',
    'DateRange',
]



def quarter(date):
    return int((date.month - 1) / 3 + 1)


def first_day_of_quarter(date):
    return datetime(date.year, 3 * quarter(date) - 2, 1)


def last_day_of_quarter(date):
    month = 3 * quarter(date)
    remaining = int(month / 12)
    return datetime(date.year + remaining, month % 12 + 1, 1) + timedelta(days=-1)


def quarter_range(date=None, index=0):
    if not date:
        date = datetime.now().date()
    first_day = first_day_of_quarter(date)
    last_day = last_day_of_quarter(first_day)
    return first_day, last_day


def first_day_of_month(date):
    return date.replace(day=1)


def last_day_of_month(date):
    if date.month == 12:
        return date.replace(day=31)
    return date.replace(month=date.month+1, day=1) - timedelta(days=1)


def month_range(date=None, index=0):
    if not date:
        date = datetime.now().date()

    first_day = first_day_of_month(date)
    if index != 0:
        delta = first_day.month+index
        if delta < 1:
            delta = 12
        elif delta > 12:
            delta = 1
        first_day = first_day.replace(month=delta)
    last_day = last_day_of_month(first_day)
    return first_day, last_day


def week_range(date=None, index=0):

    one_day = timedelta(days=1)
    week = []
    if not date:
        date = datetime.now().date()
    day_idx = (date.weekday()) % 7  # turn sunday into 0, monday into 1, etc.
    sunday = date - timedelta(days=day_idx-(7*index))
    date = sunday
    for n in range(7):
        week.append(date)
        date += one_day
    return week[0], week[-1]




def next_month(date=None, index=1):
    if not date:
        date = datetime.now().date()
    year = date.year
    month = date.month+index
    if month > 12:
        month = month-12
    if month < 1:
        month = 12+month
        year -= 1
    return date.replace(month=month, day=1, year=year)


class DateRange():
    def __init__(self, start, stop):

        self.start = datetime.combine(start, datetime.min.time())
        self.stop = datetime.combine(stop, datetime.max.time())
        self.year = self.start.year

    def __contains__(self, date):
        return date >= self.start and date <= self.stop

    def __lt__(self, date):
        return date > self.stop 

    def __gt__(self, date):
        return date < self.start

    @property
    def range(self):
        return self.start, self.stop

    @property
    def is_past(self):
        return datetime.now() > self

    @property
    def is_future(self):
        return datetime.now() < self

    @property
    def is_now(self):
        return datetime.now() in self


    @property
    def days(self):
        return (self.stop - self.start).days + 1

    @property
    def next_year(self):
        return self.move_year(+1)

    @property
    def is_week(self):
        return self.start.weekday() == 0 and self.days == 7

    @property
    def week(self):
        return self.week_start

    @property
    def week_start(self):
        return Week(self.start)

    @property
    def week_stop(self):
        return Week(self.stop)

    @property
    def prev_year(self):
        return self.move_year(-1)

    def move_year(self, index):
        return self.__class__(
            self.start.replace(year=self.start.year+index), 
            self.stop.replace(year=self.stop.year+index)
        )

    @property
    def next(self):
        days_delta = abs(self.days)
        start = datetime.combine(self.stop + timedelta(days = 1), datetime.min.time())
        stop = datetime.combine(start + timedelta(days = days_delta), datetime.max.time())
        return self.__class__(start, stop)

    @property
    def prev(self):
        days_delta = abs(self.days)
        stop = datetime.combine(self.start - timedelta(days = 1), datetime.max.time())
        start = datetime.combine(stop - timedelta(days = days_delta), datetime.min.time())
        return self.__class__(start, stop)

    @property
    def weeks(self):
        if self.week_start != self.week_stop:
            return [self.week_start, self.week_stop]
        else:
            return [self.week_start]
    
    def weeks_range_repr(self, prefix="S"):
        return ' - '.join([ f'{prefix}{w}' for w in self.weeks])



class Week(DateRange):
    def __init__(self, current=None):

        if not current:
            current = datetime.now().date()
        self.current = current        
        self.start = datetime.combine(self.current - timedelta(days = self.current.weekday()), datetime.min.time())
        self.stop = datetime.combine(self.start + timedelta(days = 6), datetime.max.time())
        self.year = self.stop.year if self.number == 1 else self.start.year

    def __str__(self):
        return f'{self.number_zero_filled} ({self.year})'

    def __repr__(self):
        return f'{self.number_zero_filled} ({self.year})'

    def __eq__(self, other):
        return self.start == other.start and self.stop == other.stop

    @property
    def date_range(self):
        return DateRange(self.start, self.stop)

    @property
    def next_year(self):
        return self.move_year(+1)

    @property
    def prev_year(self):
        return self.move_year(-1)

    def move_year(self, index):
        week = self.__class__(self.start.replace(year=self.year+index))
        if week.number < self.number:
            week = week.next
        if week.number > self.number:
            week = week.prev
        return week

    @property
    def next(self):
        return self.__class__(self.stop + timedelta(days = 1))

    @property
    def prev(self):
        return self.__class__(self.start - timedelta(days = 1))

    @property
    def number(self):
        return self.start.isocalendar()[1]

    @property
    def number_zero_filled(self):
        return f'{self.number:02d}'

    @classmethod
    def all_of_year(cls, year=None):
        if not year:
            year = datetime.now().year
        # print(year, f'{odate(year, 1, 1):%a %d %B %Y}')
        week = cls(odate(year, 1, 1))

        # print(week, week.number, week.start.isocalendar(), f'{week.start:%a %d %B %Y}', f'{week.stop:%a %d %B %Y}')
        if week.number != 1:
            week = week.next
        
        while week.year == year:
            yield week
            week = week.next











def get_week_number(date=None, zfill=None, prefix=None):
    if not date:
        date = datetime.now().date()
    number = date.isocalendar()[1]

    return date.isocalendar()[1]

def get_weeks_of_year(year=None):
    weeks = []
    if not year:
        year = datetime.now().year

    start = date(year, 1, 1)     # January 1st
    while start.year == year:
        stop += timedelta(days = 6 - start.weekday())  # First Sunday
        yield start, stop
        start += timedelta(days = 7)














# class WeekOld(namedtuple('Week', ('year', 'week'))):
#     """A Week represents a period of 7 days starting with a Monday.
#     Weeks are identified by a year and week number within the year.
#     This corresponds to the read-only attributes 'year' and 'week'.
#     Week 1 of a year is defined to be the first week with 4 or more days in
#     January.  The preceeding week is either week 52 or 53 of the
#     preceeding year.
#     Week objects are tuples, and thus immutable, with an interface
#     similar to the standard datetime.date class.
#     """
#     __slots__ = ()

#     def __new__(cls, year, week):
#         """Initialize a Week tuple with the given year and week number.
#         The week number does not have to be within range.  The numbers
#         will be normalized if not.  The year must be within the range
#         1 to 9999.
#         """
#         if week < 1 or week > 52:
#             return cls(year, 1) + (week - 1)
#         if year < 1 or year > 9999:
#             raise ValueError("year is out of range")
#         return super(Week, cls).__new__(cls, year, week)

#     @classmethod
#     def thisweek(cls):
#         """Return the current week (local time)."""
#         return cls(*(odate.today().isocalendar()[:2]))

#     @classmethod
#     def fromordinal(cls, ordinal):
#         """Return the week corresponding to the proleptic Gregorian ordinal,
#         where January 1 of year 1 starts the week with ordinal 1.
#         """
#         if ordinal < 1:
#             raise ValueError("ordinal must be >= 1")
#         return super(Week, cls).__new__(cls, *(odate.fromordinal((ordinal-1) * 7 + 1).isocalendar()[:2]))

#     @classmethod
#     def fromstring(cls, isostring):
#         """Return a week initialized from an ISO formatted string like "2011W08" or "2011-W08"."""
#         if isinstance(isostring, basestring) and len(isostring) == 7 and isostring[4] == 'W':
#            return cls(int(isostring[0:4]), int(isostring[5:7]))
#         elif isinstance(isostring, basestring) and len(isostring) == 8 and isostring[4:6] == '-W':
#            return cls(int(isostring[0:4]), int(isostring[6:8]))
#         else:
#             raise ValueError("Week.tostring argument must be on the form <yyyy>W<ww>; got %r" % (isostring,))

#     @classmethod
#     def withdate(cls, date):
#         """Return the week that contains the given datetime.date"""
#         return cls(*(date.isocalendar()[:2]))

#     @classmethod
#     def weeks_of_year(cls, year):
#         """Return an iterator over the weeks of the given year.
#         Years have either 52 or 53 weeks."""
#         w = cls(year, 1)
#         while w.year == year:
#             yield w
#             w += 1

#     @classmethod
#     def last_week_of_year(cls, year):
#         """Return the last week of the given year.
#         This week with either have week-number 52 or 53.
#         This will be the same as Week(year+1, 0), but will even work for
#         year 9999 where this expression would overflow.
#         The first week of a given year is simply Week(year, 1), so there
#         is no dedicated classmethod for that.
#         """
#         if year == cls.max.year:
#             return cls.max
#         return cls(year+1, 0)

#     def day(self, num):
#         """Return the given day of week as a date object.  Day 0 is the Monday."""
#         d = odate(self.year, 1, 4)  # The Jan 4th must be in week 1 according to ISO
#         return d + timedelta(weeks=self.week-1, days=-d.weekday() + num)

#     def monday(self):
#         """Return the first day of the week as a date object"""
#         return self.day(0)

#     def monday(self):
#         """Return the first day of the week as a date object"""
#         return self.day(0)

#     def tuesday(self):
#         """Return the second day the week as a date object"""
#         return self.day(1)

#     def wednesday(self):
#         """Return the third day the week as a date object"""
#         return self.day(2)

#     def thursday(self):
#         """Return the fourth day the week as a date object"""
#         return self.day(3)

#     def friday(self):
#         """Return the fifth day the week as a date object"""
#         return self.day(4)

#     def saturday(self):
#         """Return the sixth day the week as a date object"""
#         return self.day(5)

#     def sunday(self):
#         """Return the last day the week as a date object"""
#         return self.day(6)

#     def days(self):
#         """Return the 7 days of the week as a list (of datetime.date objects)"""
#         monday = self.day(0)
#         return [monday + timedelta(days=i) for i in range(7)]

#     def contains(self, day):
#         """Check if the given datetime.date falls within the week"""
#         return self.day(0) <= day < self.day(7)

#     def toordinal(self):
#         """Return the proleptic Gregorian ordinal the week, where January 1 of year 1 starts the first week."""
#         return self.monday().toordinal() // 7 + 1

#     def replace(self, year=None, week=None):
#         """Return a Week with either the year or week attribute value replaced"""
#         return self.__class__(self.year if year is None else year,
#                               self.week if week is None else week)

#     def year_week(self):
#         """Return a regular tuple containing the (year, week)"""
#         return self.year, self.week

#     def __str__(self):
#         """Return a ISO formatted week string like "2011W08". """
#         return '%04dW%02d' % self

#     isoformat = __str__  # compatibility with datetime.date

#     def __repr__(self):
#         """Return a string like "isoweek.Week(2011, 35)"."""
#         return __name__ + '.' + self.__class__.__name__ + '(%d, %d)' % self

#     def __add__(self, other):
#         """Adding integers to a Week gives the week that many number of weeks into the future.
#         Adding with datetime.timedelta is also supported.
#         """
#         if isinstance(other, timedelta):
#             other = other.days // 7
#         return self.__class__.fromordinal(self.toordinal() + other)

#     def __sub__(self, other):
#         """Subtracting two weeks give the number of weeks between them as an integer.
#         Subtracting an integer gives another Week in the past."""
#         if isinstance(other, (int, long, timedelta)):
#             return self.__add__(-other)
#         return self.toordinal() - other.toordinal()

# Week.min = Week(1,1)
# Week.max = Week(9999,52)
# Week.resolution = timedelta(weeks=1)