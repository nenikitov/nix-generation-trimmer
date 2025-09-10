#!/usr/bin/env python3

import json
import sys
from datetime import datetime

from .args import Args, args
from .generations import ProfileError


def main_args(args: Args):
    now = datetime.now()
    to_delete: dict[str, list[int]] = {}

    for profile in args.profile:
        try:
            generations = profile.generations()
        except ProfileError as e:
            print(f"Skipping: {e}", file=sys.stderr)
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

        if args.max:
            keep_index = min(keep_index, args.max)

        if args.min:
            keep_index = max(keep_index, args.min)

        to_delete[profile.path.as_posix()] = [g.id for g in generations[keep_index:]]

    if args.dry_run:
        print(json.dumps(to_delete))

def main():
    main_args(args())

if __name__ == "__main__":
    main()
