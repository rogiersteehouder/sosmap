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

from pydantic import BaseModel, Field, PrivateAttr

import jinja2
import jinja2.ext

try:
    import tomllib
except ImportError:
    import tomli as tomllib


class Alliance(BaseModel):
    """Alliance in State of Survival"""

    name: str
    color: str = "#000"
    extra: str = ""


class State(BaseModel):
    """State in State of Survival"""

    number: int
    description: str = ""
    extra: str = ""
    csv: str | None = None  # default derived from fields in __init__
    file_base: str | None = None  # default derived from fields in __init__
    alliances: list[Alliance] = Field(default_factory=list)
    svg_file: pathlib.Path | None = None
    html_file: pathlib.Path | None = None

    def __init__(self, **data):
        super().__init__(**data)
        if self.csv is None:
            self.csv = f"state-{self.number}.csv"
        if self.file_base is None:
            self.file_base = f"{self.number}"


class Config(BaseModel):
    """Configuration"""

    title: str = "State maps"
    output_dir: pathlib.Path = pathlib.Path("docs")
    states: list[State] = Field(default_factory=list)


def main():
    exts = [jinja2.ext.loopcontrols]

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

    cfg = Config.parse_obj(tomllib.loads(pathlib.Path("gen.toml").read_text()))
    #print(cfg)
    #return

    svg_tpl = j2_env.from_string(pathlib.Path("state map.svg.j2").read_text())
    html_tpl = j2_env.from_string(pathlib.Path("state map.html.j2").read_text())

    for state in cfg.states:
        file_base = cfg.output_dir / state.file_base

        context = {}
        context["cfg"] = cfg
        with open(state.csv, newline="") as f:
            context["buildings"] = list(csv.DictReader(f))
        context['state'] = state
        context["alliances"] = state.alliances
        context["owners"] = [x.name for x in state.alliances]
        context["svg_file"] = state.svg_file = file_base.with_suffix(".svg")
        context["html_file"] = state.html_file = file_base.with_suffix(".html")

        with context["svg_file"].open("w") as f:
            svg_tpl.stream(context).dump(f)

        with context["html_file"].open("w") as f:
            html_tpl.stream(context).dump(f)

    context = {"cfg": cfg}
    html_tpl = j2_env.from_string(pathlib.Path("index.html.j2").read_text())
    with (cfg.output_dir / "index.html").open("w") as f:
        html_tpl.stream(context).dump(f)


if __name__ == "__main__":
    # pylint: disable=all
    main()
