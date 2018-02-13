from datetime import datetime, timedelta, date as odate
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

    if index != 0:
        delta = date.month+index
        if delta < 1:
            delta = 12
        elif delta > 12:
            delta = 1
        date = date.replace(month=delta)
    first_day = first_day_of_month(date)
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