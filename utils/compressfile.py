#!/usr/bin/env python3
"""Compresses a file and prints it through stdout. Useful to quickly compress
the html files of this project in order to have them embedded on the main file.
"""

import base64
import sys
import zlib

def print_string(string, splitting, chars_per_line):
    """If 'splitting', prints 'chars_per_line' characters per line."""
    if not splitting:
        print(string)
        return

    i = 0
    while i < len(string):
        print(string[i:i+chars_per_line])
        i = i + chars_per_line


if __name__ == '__main__':
    if len(sys.argv) < 2:
        print("Usage: python compressfile.py [input file] {chars per line}")
        sys.exit(1)

    with open(sys.argv[1], 'r') as input_file:
        print_string(
            base64.b64encode(
                zlib.compress(
                    bytes(input_file.read(), input_file.encoding)
                )
            ),
            len(sys.argv) is 3,
            int(sys.argv[2]) if len(sys.argv) is 3 else 65
        )
