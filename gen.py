#!/usr/bin/env python3
# encoding: UTF-8

"""Generate ViV state map files.
"""

__author__  = 'Rogier Steehouder'
__date__    = '2021-03-24'
__version__ = '1.0'

import sys
import datetime
import pathlib
import csv

import jinja2
import jinja2.ext


class NewlineRemover(jinja2.ext.Extension):
    def filter_stream(self, stream):
        skip = True
        for token in stream:
            if skip:
                if token.type == 'data' and token.value == '\n':
                    continue
                if token.type == 'data' and token.value.lstrip().startswith('<!DOCTYPE'):
                    token = jinja2.lexer.Token(token.lineno, token.type, token.value.lstrip())
                    skip = False
            yield token


def main():
    exts = [jinja2.ext.loopcontrols]
    exts.append(NewlineRemover)

    j2_env = jinja2.Environment(
        loader=jinja2.FileSystemLoader('.'),
        autoescape=jinja2.select_autoescape(['html', 'xml']),
        extensions=exts,
        trim_blocks=True,
        lstrip_blocks=True,
        keep_trailing_newline=True
    )
    j2_env.globals['datetime'] = datetime.datetime
    j2_env.globals['Path'] = pathlib.Path

    #####
    # State 393
    #####

    tpl = j2_env.from_string(pathlib.Path('viv state map.svg.j2').read_text())

    context = {}
    with open('state 393.csv', newline='') as f:
        context['state'] = list(csv.DictReader(f))

    with open('docs/393.svg', 'w') as f:
        tpl.stream(context).dump(f)

    tpl = j2_env.from_string(pathlib.Path('viv state map.html.j2').read_text())

    context = { 'filename': '393.svg' }

    with open('docs/393.html', 'w') as f:
        tpl.stream(context).dump(f)

    #####
    # State 795
    #####

    tpl = j2_env.from_string(pathlib.Path('viv state map.svg.j2').read_text())

    context = {}
    with open('state 795.csv', newline='') as f:
        context['state'] = list(csv.DictReader(f))

    with open('docs/795.svg', 'w') as f:
        tpl.stream(context).dump(f)

    tpl = j2_env.from_string(pathlib.Path('viv state map.html.j2').read_text())

    context = { 'filename': '795.svg' }

    with open('docs/795.html', 'w') as f:
        tpl.stream(context).dump(f)

if __name__ == '__main__':
	# pylint: disable=all
    main()
