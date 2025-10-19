#!/bin/python3
import os
from os import path
import shutil
from jinja2 import Environment, FileSystemLoader, select_autoescape

SOURCE='src/templates/pages/'
BASE=('src/templates/pages', 'src/templates/components/', 'src/templates/base.html')
DEST='dist/'

def main():
    abs_file_path = os.path.abspath(__file__)
    abs_dir_path = os.path.dirname(abs_file_path)
    os.chdir(abs_dir_path)

    shutil.rmtree(DEST)
    os.mkdir(DEST)

    env = Environment(
        loader=FileSystemLoader(BASE),
        autoescape=select_autoescape(),
        auto_reload=False,
    )

    for root, subdirs, files in os.walk(SOURCE):
        for file in files:
            template = env.get_template(file)
            rel_path = path.relpath(path.join(root, file), SOURCE)
            export_path = path.join(DEST, rel_path)
            with open(export_path, 'w') as file:
                file.write(template.render() + '\n') # Because jinja2 stripts one trailing newline

if __name__ == '__main__':
    main()
