#!/usr/bin/env python3
# encoding: UTF-8

"""Generate ViV state map files.
"""

__author__ = "Rogier Steehouder"
__date__ = "2022-09-17"
__version__ = "1.1"

# 2021-03-24 - 1.0
# 2022-09-17 - 1.1

import datetime
import pathlib
import csv

import jinja2
import jinja2.ext

try:
    import tomllib
except ImportError:
    import tomli as tomllib


class NewlineRemover(jinja2.ext.Extension):
    def filter_stream(self, stream):
        skip = True
        for token in stream:
            if skip:
                if token.type == "data" and token.value == "\n":
                    continue
                if token.type == "data" and token.value.lstrip().startswith(
                    "<!DOCTYPE"
                ):
                    token = jinja2.lexer.Token(
                        token.lineno, token.type, token.value.lstrip()
                    )
                    skip = False
            yield token


def main():
    exts = [jinja2.ext.loopcontrols]
    exts.append(NewlineRemover)

    j2_env = jinja2.Environment(
        loader=jinja2.FileSystemLoader("."),
        autoescape=jinja2.select_autoescape(["html", "xml"]),
        extensions=exts,
        trim_blocks=True,
        lstrip_blocks=True,
        keep_trailing_newline=True,
    )
    j2_env.globals["datetime"] = datetime.datetime
    j2_env.globals["Path"] = pathlib.Path

    out_dir = pathlib.Path("docs")
    svg_tpl = j2_env.from_string(pathlib.Path("state map.svg.j2").read_text())
    html_tpl = j2_env.from_string(pathlib.Path("state map.html.j2").read_text())

    cfg = tomllib.loads(pathlib.Path("gen.toml").read_text())

    for state in cfg["states"].values():
        print(state)
        file_base = out_dir / state["file_base"]

        context = {}
        with open(state["csv"], newline="") as f:
            context["state"] = list(csv.DictReader(f))
        context["alliances"] = list(state["alliances"].values())
        context["owners"] = [x["name"] for x in state["alliances"].values()]

        print(context)

        with file_base.with_suffix(".svg").open("w") as f:
            svg_tpl.stream(context).dump(f)
            context["filename"] = f.name

        with file_base.with_suffix(".html").open("w") as f:
            html_tpl.stream(context).dump(f)


if __name__ == "__main__":
    # pylint: disable=all
    main()
