import sys


def eprint(*args, **kwargs):
    print(*args, file=sys.stderr, **kwargs)


def hex_string_to_hex(hex_string):
    return int(hex_string, 16)
