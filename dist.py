#!/bin/python3
import subprocess
import locale
from datetime import datetime
import os
from os import path
import time
from sys import stderr
import shutil
from collections.abc import Callable
import math
from jinja2 import Environment, FileSystemLoader, select_autoescape, StrictUndefined

TEMPLATE_RENDER_SOURCE='src/templates/pages'
TEMPLATE_DIRS=('src/templates/pages', 'src/templates/components')
COPY_DIRS=('src/css', 'src/img')
DEST='dist'

def main():
    locale.setlocale(locale.LC_ALL, 'C')

    # Make sure current directory is correct relative to script path
    abs_file_path = path.abspath(__file__)
    abs_dir_path = path.dirname(abs_file_path)
    os.chdir(abs_dir_path)

    if path.isfile(DEST):
        print(f'Destination {DEST} is a file', file=stderr)
        exit(1)

    def run():
        context = get_context()
        templates = render_templates(context)
        statics = copy_static()
        remove_unknown(templates + statics)

    timer(run)

def timer(func: Callable[[], None]):
    start = time.time_ns()
    func()
    end = time.time_ns()

    diff = end - start
    scale = int(math.log(diff, 10**3))
    units = ['n', 'μ', 'm', '', 'k', 'M', 'T']

    print(f'Done in \033[31m{diff/(10**(3*scale)):.4}{units[scale]}s\033[0m')

def render_templates(context: dict) -> list[str]:
    env = Environment(
        loader=FileSystemLoader(TEMPLATE_DIRS),
        autoescape=select_autoescape(),
        auto_reload=False,
        undefined=StrictUndefined,
    )

    templates = []
    for root, _subdirs, files in os.walk(TEMPLATE_RENDER_SOURCE):
        for file in files:
            src_path = path.join(root, file) # e.g. src/templates/pages/index.html
            rel_path = path.relpath(src_path, TEMPLATE_RENDER_SOURCE) # e.g. index.html
            template = env.get_template(rel_path)
            export_path = path.join(DEST, rel_path) # e.g. dist/index.html
            export_dir = path.dirname(export_path) # e.g. dist/
            os.makedirs(export_dir, exist_ok=True)

            with open(export_path, 'w', encoding='utf-8') as file:
                file.write(template.render(context))
            print(f'[render] {src_path}')
            templates.append(export_path)

    return templates

def copy_static():
    statics = []
    for dir_ in COPY_DIRS: # dir_ e.g. src/css/
        rel_dir = path.split(dir_)[-1] # e.g. css/
        export_dir = path.join(DEST, rel_dir) # e.g. dist/css/
        for root, _subdirs, files in os.walk(dir_):
            for file in files:
                src_path = path.join(root, file) # e.g. src/css/compiled.css
                rel_path = path.relpath(src_path, dir_) # e.g. compiled.css
                export_path = path.join(export_dir, rel_path) # e.g. dist/css/compiled.css
                export_dir = path.dirname(export_path) # e.g. dist/css/
                os.makedirs(export_dir, exist_ok=True)

                statics.append(export_path)
                if path.exists(export_path) and path.getmtime(export_path) > path.getmtime(src_path):
                    continue
                shutil.copy(src_path, export_path)
                print(f'[copy] {src_path}')

    return statics

def remove_unknown(paths: list[str]):
    for root, _subdirs, files in os.walk(DEST):
        for file in files:
            dest_path = path.join(root, file)
            if dest_path not in paths:
                print(f'[delete] {dest_path}')

def get_context() -> dict:
    context = {}

    result = subprocess.run(
        'git log -1 --format="%at"',
        shell=True,
        capture_output=True,
        encoding='ascii'
    )
    if result.stderr != '':
        print('Failed to check last commit date', file=stderr)
        print(result.stderr, file=stderr)
        exit(1)
    assert result.stdout != ''
    epoch_time: int = int(result.stdout)
    context['commit_date'] = datetime.fromtimestamp(epoch_time)

    return context

if __name__ == '__main__':
    main()
