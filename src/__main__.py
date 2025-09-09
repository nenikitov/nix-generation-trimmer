#!/usr/bin/env python3

import sys
from datetime import datetime

from args import Args, args
from generations import ProfileError


def main(args: Args):
    now = datetime.now()

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
                -1,
            )

        print(keep_index)

        if args.max:
            keep_index = max(keep_index, args.max)

        if args.min:
            keep_index = min(keep_index, args.min)

        print(*generations[:keep_index], sep="\n")


if __name__ == "__main__":
    main(args())
