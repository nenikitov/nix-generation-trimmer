import argparse
import re
import typing as t
from enum import Enum
from operator import itemgetter
from textwrap import dedent

from dateutil.relativedelta import relativedelta


class Profile(Enum):
    USER = "user"
    CHANNEL = "channel"
    HOME_MANAGER = "home-manager"
    SYSTEM = "system"

    def __str__(self) -> str:
        return self.value


PATTERN_RELATIVE_DELTA = re.compile(
    r"""
    ^
    \s*
    (?:(?P<years>[1-9]\d*)\s*(?:y|year|years))?
    \s*
    (?:(?P<months>[1-9]\d*)\s*(?:m|month|months))?
    \s*
    (?:(?P<days>[1-9]\d*)\s*(?:d|day|days))?
    \s*
    (?:(?P<hours>[1-9]\d*)\s*(?:h|hour|hours))?
    \s*
    $
    """,
    re.VERBOSE,
)


def parse_relativedetla(string: str):
    if string == "":
        raise argparse.ArgumentTypeError(f"String cannot be empty.")

    match = PATTERN_RELATIVE_DELTA.fullmatch(string)

    if match is None:
        raise argparse.ArgumentTypeError(
            f"String '{string}' does not follow the format '#y#m#d#h' where '#' is a positive non-zero integer and each section is optional."
        )

    [years, months, days, hours] = itemgetter("years", "months", "days", "hours")(
        match.groupdict()
    )

    return relativedelta(
        years=int(years) if years else 0,
        months=int(months) if months else 0,
        days=int(days) if days else 0,
        hours=int(hours) if hours else 0,
    )


def parse_int_range(
    min: None | int = None, max: None | int = None
) -> t.Callable[[str], int]:
    def parse(string: str) -> int:
        try:
            val = int(string)
        except ValueError as e:
            raise argparse.ArgumentTypeError(repr(e))

        if min is not None and val < min:
            raise argparse.ArgumentTypeError(f"Integer '{val}' must be >= {min}")
        if max is not None and val >= max:
            raise argparse.ArgumentTypeError(f"Integer '{val}' must be < {max}")

        return val

    return parse


class Args(argparse.Namespace):
    profile: list[Profile]
    older_than: None | relativedelta
    min: None | int
    max: None | int
    dry_run: bool


def args() -> Args:
    parser = argparse.ArgumentParser(
        description="Delete old Nix generations.",
        formatter_class=argparse.RawTextHelpFormatter,
    )
    parser.add_argument(
        "profile",
        help=dedent(
            """\
                Scope which should be cleaned up.
                Should be composed out of 1 or more duration sections in decreasing order:
                - A section is '# duration' where '#' is a positive non-zero number and 'duration' is one of 'year', 'month', 'day', or 'hour'
                - Each duration specifier has a plural and a 1 letter version
                - Spaces are optional
                Examples:
                - '1year'
                - '1m10d'
                - '17 years 1 month 3d     2          h'
            """
        ),
        type=Profile,
        choices=Profile,
        nargs="+",
    )
    parser.add_argument(
        "--older-than",
        help="Age of an oldest generation to keep.",
        type=parse_relativedetla,
    )
    parser.add_argument(
        "--min",
        help="Minimum amount of generations to keep.",
        type=parse_int_range(min=1),
    )
    parser.add_argument(
        "--max",
        help="Maximum amount of generations to keep.",
        type=parse_int_range(min=1),
    )
    parser.add_argument(
        "--dry-run",
        help="Print generations to be removed, do not delete.",
        action="store_true",
    )

    return parser.parse_args(namespace=Args())
