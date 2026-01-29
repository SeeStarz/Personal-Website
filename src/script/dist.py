#!/bin/python3
from package.dist import main
import sys

if __name__ == '__main__':
    main()
else:
    print('ERROR: This python file is not intended to be used as an import', file=sys.stderr)
    exit(1)
