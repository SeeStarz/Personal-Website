#!/bin/python3
import os
import shutil

def main():
    abspath = os.path.abspath(__file__)
    dirname = os.path.dirname(abspath)
    os.chdir(dirname)

    shutil.rmtree('dist')
    shutil.copytree('src/serve', 'dist/')
    __import__('src.py.compile').py.compile.compile('dist/')

if __name__ == '__main__':
    main()
