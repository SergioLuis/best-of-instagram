#!/usr/bin/env python3
"""Compresses a file and prints it through stdout. Useful to quickly compress
the html files of this project in order to have them embedded on the main file.
"""

import base64
import sys
import zlib

if __name__ == '__main__':
    if len(sys.argv) is not 2:
        print("Usage: python compressfile.py [input file]")
        sys.exit(1)

    with open(sys.argv[1], 'r') as input_file:
        print(
            base64.b64encode(
                zlib.compress(
                    bytes(input_file.read(), input_file.encoding)
                )
            )
        )
