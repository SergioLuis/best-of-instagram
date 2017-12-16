"""Creates a release of this module."""

import base64
import sys
import zlib

usage = """Usage: python createrelease.py [input file] [output file]"""

template = (
"""#!/usr/bin/env python3

import base64
import zlib

if __name__ == '__main__':
    exec(
        zlib.decompress(
            base64.b64decode({})
        ).decode('utf-8')
    )
"""
)

if __name__ == '__main__':
    if len(sys.argv) is not 3:
        print(usage, file=sys.stderr)
        sys.exit(1)

    with open(sys.argv[1], 'r') as input_file:
        with open(sys.argv[2], 'w') as output_file:
            output_file.write(
                template.format(
                    base64.b64encode(
                        zlib.compress(
                            bytes(input_file.read(), 'utf-8')
                        )
                    )
                )
            )
