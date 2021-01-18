import sys
from glob import glob
import re
import logging

import pandas as pd

from snakedeploy.exceptions import UserError

def collect_files(config_sheet_path: str):
    config_sheet = pd.read_csv(config_sheet_path, sep="\t")
    config_sheet["input_re"] = config_sheet["input_pattern"].apply(re.compile)

    for item in sys.stdin:
        item = item[:-1] # remove newline

        matches = list(filter(lambda match: match.match is not None, get_matches(item, config_sheet)))

        if not matches:
            raise UserError(f"No input pattern in config sheet matches {item}.")
        elif len(matches) > 1:
            raise UserError(f"Item {item} matches multiple input patterns.")
        else:
            match = matches[0]
            pattern = match.rule["glob_pattern"].format(**{key: autoconvert(value) for key, value in match.match.groupdict().items()})
            files = sorted(glob(pattern))
            if files:
                print(item, *files, sep="\t")
            else:
                raise UserError(f"No files were found for {item} with pattern {pattern}.")


Match = namedtuple("Match", "rule match")


def get_matches(item, config_sheet: pd.DataFrame):
    return (Match(rule, rule["input_re"].match(item)) for rule in config_sheet.itertuples())


def autoconvert(value):
    try:
        return int(value)
    except ValueError:
        return value