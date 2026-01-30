"""
Distribute script of the python package, please run from top level dist.py script
"""

import subprocess
import locale
from datetime import datetime
from itertools import chain
import os
from os import path

from package.lib import timer, copy_dir, copy_file, remove_unknown, RESULT_DIR, STATIC_DIR, DATA_DIR
import package.module as module

def main():
    locale.setlocale(locale.LC_ALL, 'C')

    # Make sure current directory is correct relative to script path
    abs_file_path = path.abspath(__file__)
    abs_dir_path = path.dirname(abs_file_path)
    target_path = path.join(abs_dir_path, '../../..')
    os.chdir(target_path)

    if path.isfile(RESULT_DIR):
        print(f'Destination {RESULT_DIR} is a file', file=stderr)
        exit(1)

    os.makedirs(RESULT_DIR, exist_ok=True)

    build_scripts = [module.homepage.build]

    @timer
    def run():
        static_assets = copy_dir(source_dir=STATIC_DIR, dest_dir=RESULT_DIR)

        script_artifacts = list(chain.from_iterable(
            (script() for script in build_scripts)
        ))
        assert len(script_artifacts) == len(set(script_artifacts)) # No duplicates

        tailwind_artifacts = [
            copy_file(
                source_path=path.join(DATA_DIR, 'css/compiled.css'),
                dest_path=path.join(RESULT_DIR, 'css/compiled.css'),
            )
        ]

        known_paths = static_assets + script_artifacts + tailwind_artifacts
        remove_unknown(known_paths=known_paths, dest=RESULT_DIR)

    run()
