#!/bin/python3
import subprocess
import locale
from datetime import datetime
import os
from os import path
from sys import stderr
import shutil
from jinja2 import Environment, FileSystemLoader, select_autoescape, StrictUndefined

TEMPLATE_RENDER_SOURCE='src/templates/pages/'
TEMPLATE_DIRS=('src/templates/pages/', 'src/templates/components/')
COPY_DIRS=('src/css',)
DEST='dist/'

def main():
    locale.setlocale(locale.LC_ALL, 'C')

    abs_file_path = os.path.abspath(__file__)
    abs_dir_path = os.path.dirname(abs_file_path)
    os.chdir(abs_dir_path)

    shutil.rmtree(DEST)
    os.mkdir(DEST)

    env = Environment(
        loader=FileSystemLoader(TEMPLATE_DIRS),
        autoescape=select_autoescape(),
        auto_reload=False,
        undefined=StrictUndefined,
    )
    context = get_context()

    # Render templates
    for root, subdirs, files in os.walk(TEMPLATE_RENDER_SOURCE):
        for file in files:
            template = env.get_template(file)
            rel_path = path.relpath(path.join(root, file), TEMPLATE_RENDER_SOURCE)
            export_path = path.join(DEST, rel_path)
            with open(export_path, 'w', encoding='utf-8') as file:
                file.write(template.render(context))

    # Distribute non-render contents
    for dir_ in COPY_DIRS:
        export_directory_name = path.split(dir_)[-1]
        shutil.copytree(dir_, path.join(DEST, export_directory_name))

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
