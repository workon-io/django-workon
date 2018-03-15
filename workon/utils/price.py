import locale


__all__ = ['currency']


def currency(value, strip_zero=True):
    price = locale.currency(float(value), grouping=True)
    if strip_zero:
    	price = price.replace(',00','')
    return price