try:
    from colour import Color
except:
    Color = dict()

__all__ = ['PColors']


class PColors:
    HEADER = '\033[95m'
    OKBLUE = '\033[94m'
    OKGREEN = '\033[92m'
    GREEN = OKGREEN
    WARNING = '\033[93m'
    YELLOW = WARNING
    FAIL = '\033[91m'
    ERROR = FAIL
    ENDC = '\033[0m'
    BOLD = '\033[1m'
    UNDERLINE = '\033[4m'

    OK = f'''{BOLD}{OKGREEN}[OK]{ENDC}'''

