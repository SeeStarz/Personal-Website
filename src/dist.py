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

TEMPLATE_RENDER_SOURCES=('src/templates/pages',)
TEMPLATE_DIRS=('src/templates/pages', 'src/templates/components')
MARKDOWN_SOURCES=('src/markdown',)
COPY_DIRS=('src/css', 'src/img')
BUILD_DIR='build'
DEST='dist'

def main():
    locale.setlocale(locale.LC_ALL, 'C')

    # Make sure current directory is correct relative to script path
    abs_file_path = path.abspath(__file__)
    abs_dir_path = path.dirname(abs_file_path)
    os.chdir(abs_dir_path + '/..')

    if path.isfile(DEST):
        print(f'Destination {DEST} is a file', file=stderr)
        exit(1)

    def run():
        context = add_context_commit_date(context={})
        # markdown_pages = render_markdowns(MARKDOWN_SOURCES, BUILD_DIR)
        static_pages = render_templates(context, sources=TEMPLATE_RENDER_SOURCES, DEST)
        assets = copy_static(COPY_DIRS, DEST)
        remove_unknown(known_paths=static_pages + assets, DEST)

    timer(run)

def timer(func: Callable[[], None]):
    """
    No-argument function runner with timer output
    """
    start = time.time_ns()
    func()
    end = time.time_ns()

    diff = end - start
    scale = int(math.log(diff, 10**3))
    units = ['n', 'μ', 'm', '', 'k', 'M', 'T']

    print(f'Done in \033[31m{diff/(10**(3*scale)):.4}{units[scale]}s\033[0m')

def create_default_env() -> Environment:
    """
    Return default jinja2 environment for this project
    """
    return Environment(
        loader=FileSystemLoader(TEMPLATE_DIRS),
        autoescape=select_autoescape(),
        auto_reload=False,
        undefined=StrictUndefined,
    )


def render_templates(context: dict, sources: list[str], dest: str) -> list[str]:
    """
    Recursively render templates in sources directories with the given context to dest directory
    """
    env = create_default_env()
    templates = []
    for top_level in sources:
        for root, _subdirs, files in os.walk(top_level): # e.g. src/templates/pages
            for file in files:
                src_path = path.join(root, file) # e.g. src/templates/pages/index.html
                rel_path = path.relpath(src_path, top_level) # e.g. index.html
                template = env.get_template(rel_path)
                export_path = path.join(dest, rel_path) # e.g. dist/index.html
                export_dir = path.dirname(export_path) # e.g. dist/
                os.makedirs(export_dir, exist_ok=True)

                with open(export_path, 'w', encoding='utf-8') as file:
                    file.write(template.render(context))
                print(f'[render] {src_path}')
                templates.append(export_path)

    return templates

def copy_static(copy_dirs: list[str], dest: str) -> list[str]:
    """
    Recursively copy files from copy_dirs directories to dest directory
    """
    statics = []
    for dir_ in copy_dirs: # dir_ e.g. src/css/
        rel_dir = path.split(dir_)[-1] # e.g. css/
        export_dir = path.join(dest, rel_dir) # e.g. dist/css/
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

def remove_unknown(known_paths: list[str], dest: str) -> list[str]:
    """
    Deletes files not in known_paths list from dest directory
    """
    deletes = []
    for root, _subdirs, files in os.walk(dest):
        for file in files:
            dest_path = path.join(root, file)
            if dest_path not in known_paths:
                deletes.append(dest_path)
                print(f'[delete] {dest_path}')
    return deletes

def add_context_commit_date(context: dict | None = None) -> dict:
    """
    Adds "commit_date" entry to the given context (empty dict by default) representing python datetime object
    """
    if context is None:
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
