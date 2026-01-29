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
import ansicolor

DATA_DIR = 'src/data'
TEMPLATE_DIRS = (
    path.join(DATA_DIR, 'template/layout'),
    path.join(DATA_DIR, 'template/component'),
)
STATIC_DIR='src/static/'
RESULT_DIR='dist'

def timer(func: Callable[[], None], *args, **kwargs):
    """
    Timer function wrapper that prints human readable elapsed time
    """
    def wrapper(*args, **kwargs):
        start = time.time_ns()
        func(*args, **kwargs)
        end = time.time_ns()

        diff = end - start
        scale_unbounded = int(math.log(diff, 10**3))
        units = ['ns', 'μs', 'ms', 's']
        scale = min(scale_unbounded, len(units) - 1)

        print(ansicolor.red('{:.4}{}'.format(
                    diff / (10 ** (3 * scale)),
                    units[scale]
                )))

    return wrapper

def create_jinja2_env(templates_directory: list[str] = TEMPLATE_DIRS) -> Environment:
    """
    Return default jinja2 environment for this project
    """
    return Environment(
        loader=FileSystemLoader(templates_directory),
        autoescape=select_autoescape(),
        auto_reload=False,
        undefined=StrictUndefined,
    )

def render_template(context: dict, source_path: str, dest_path: str, env: Environment | None = None) -> str:
    """
    Render one template with the given context at dest_path
    Returns render_path if successful
    """
    source_dir: str = path.dirname(source_path)
    filename: str = path.relpath(source_path, source_dir)
    if env is None:
        env = create_jinja2_env()
    template = env.get_template(filename)
    with open(dest_path, 'w', encoding='utf-8') as file:
        file.write(template.render(context))
    return dest_path


# def render_templates(context: dict, sources: list[str], dest: str) -> list[str]:
#     """
#     Recursively render templates in sources directories with the given context to dest directory
#     Returns list of rendered paths if succesful
#     """
#     env = create_default_env()
#     templates = []
#     for top_level in sources:
#         for root, _subdirs, files in os.walk(top_level): # e.g. src/data/templates/pages
#             for file in files:
#                 src_path = path.join(root, file) # e.g. src/data/templates/pages/index.html
#                 rel_path = path.relpath(src_path, top_level) # e.g. index.html
#                 template = env.get_template(rel_path)
#                 export_path = path.join(dest, rel_path) # e.g. dist/index.html
#                 export_dir = path.dirname(export_path) # e.g. dist/
#                 os.makedirs(export_dir, exist_ok=True)
#
#                 with open(export_path, 'w', encoding='utf-8') as file:
#                     file.write(template.render(context))
#                 print(f'[render] {src_path}')
#                 templates.append(export_path)
#
#     return templates

def copy_dir(source_dir: str, dest_dir: str) -> list[str]:
    """
    Copies files from source_dir directory to dest_dir directory
    Return destination paths that has been copied
    """
    copies = []
    for root, _subdirs, files in os.walk(source_dir): # e.g. src/static/
        for file in files:
            src_path = path.join(root, file) # e.g. src/static/css/dark.css
            rel_path = path.relpath(src_path, source_dir) # e.g. css/dark.css
            copy_path = path.join(dest_dir, rel_path) # e.g. dist/css/dark.css
            copy_dir = path.dirname(copy_path) # e.g. dist/css

            os.makedirs(copy_dir, exist_ok=True)
            shutil.copyfile(src_path, copy_path)
            copies.append(copy_path)
            print(f'[copy] {copy_path}')

    return copies

def copy_file(source_path: str, dest_path: str) -> str:
    """
    Copy file from source_path to dest_path
    Returns dest_path
    """
    dest_dir = path.dirname(dest_path)
    os.makedirs(dest_dir, exist_ok=True)
    shutil.copy(source_path, dest_path)
    return dest_path

def remove_unknown(known_paths: list[str], dest: str) -> list[str]:
    """
    Deletes files not in known_paths list from dest directory
    Return paths that has been deleted
    """
    deletes = []
    for root, _subdirs, files in os.walk(dest):
        for file in files:
            dest_path = path.join(root, file)
            if dest_path not in known_paths:
                os.remove(dest_path)
                deletes.append(dest_path)
                print(f'[delete] {dest_path}')
    return deletes

def get_last_commit_date() -> datetime:
    """
    Returns datetime object from current repository's
    """
    result = subprocess.run(
        'git log -1 --format="%at"',
        shell=True,
        capture_output=True,
        encoding='ascii'
    )
    if result.stderr != '':
        print('Failed to check last commit date. Output:\n{}\n'.format(result.stderr.rstrip()), file=stderr)
        exit(1)
    assert result.stdout != ''
    epoch_time: int = int(result.stdout)
    return datetime.fromtimestamp(epoch_time)
