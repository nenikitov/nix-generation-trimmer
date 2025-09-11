#!/usr/bin/env python3

import json
import subprocess
import sys
from datetime import datetime

from . import color
from .args import Args, args
from .generations import ProfileError


def main_args(args: Args):
    now = datetime.now()
    to_delete: dict[str, list[int]] = {}

    for profile in args.profile:
        try:
            generations = profile.generations()
        except ProfileError as e:
            print(
                color.FG_RED + f"Skipping: {e}" + color.RESET,
                file=sys.stderr,
            )
            continue

        keep_index = 0
        if args.older_than:
            keep_index = next(
                (
                    i
                    for i, g in enumerate(generations)
                    if g.date <= now - args.older_than
                ),
                len(generations),
            )

        if args.keep_at_most:
            keep_index = min(keep_index, args.keep_at_most)

        if args.keep_at_least:
            keep_index = max(keep_index, args.keep_at_least)

        to_delete[profile.path.as_posix()] = [g.id for g in generations[keep_index:]]

    if args.dry_run:
        print(json.dumps(to_delete))
    else:
        for profile, generations in to_delete.items():
            generations = [f"{g}" for g in generations]
            print(
                color.FG_BLUE
                + f"# Cleaning up profile ({profile}) by deleting generations ({", ".join(generations)})"
                + color.RESET
            )
            subprocess.run(
                [
                    "nix-env",
                    "-vvvv",
                    "--profile",
                    profile,
                    "--delete-generations",
                    *generations,
                ]
            )


def main():
    main_args(args())


if __name__ == "__main__":
    main()
