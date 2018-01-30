from datetime import datetime, timedelta


__all__ = ['week_range', 'next_month']


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