#!/bin/python3
from os import path
from package.lib import get_last_commit_date, render_template, DATA_DIR, RESULT_DIR

def build() -> list[str]:
    commit_date = get_last_commit_date()

    index_page = render_template(
        context={"commit_date": commit_date},
        source_path=path.join(DATA_DIR,
            'template/layout/index.html',
        ),
        dest_path=path.join(RESULT_DIR, 'index.html'),
    )
    print('[build] {}'.format(index_page))
    return [index_page]
