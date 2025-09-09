#!/usr/bin/env python3

from args import args, Args

from dateutil.relativedelta import relativedelta
import argparse
from  datetime import datetime
import enum
import sys
import getpass
import os
import subprocess
import typing as t
from dataclasses import dataclass
from pathlib import Path


@dataclass
class Generation:
    id: int
    date: datetime
    current: bool

    @classmethod
    def from_string(cls, string: str):
        [id, date, time, *rest] = string.split()
        rest = " ".join(rest)

        return Generation(
            int(id),
            datetime.strptime(f"{date} {time}", "%Y-%m-%d %H:%M:%S"),
            "current" in rest,
        )


class Profile(enum.Enum):
    USER = "user"
    CHANNEL = "channel"
    HOME_MANAGER = "home-manager"
    SYSTEM = "system"

    def __str__(self) -> str:
        return self.value

    @property
    def path(self) -> Path:
        match self:
            case Profile.USER:
                return (Path.home() / ".nixprofile").absolute()
            case Profile.CHANNEL:
                return (
                    Path("/")
                    / "nix"
                    / "var"
                    / "nix"
                    / "profiles"
                    / "per-user"
                    / getpass.getuser()
                    / "channels"
                )
            case Profile.HOME_MANAGER:
                return (
                    Path(
                        os.getenv("XDG_STATE_HOME", Path().home() / ".local" / "state")
                    )
                    / "nix"
                    / "profiles"
                    / "home-manager"
                )
            case Profile.SYSTEM:
                return Path("/") / "nix" / "var" / "nix" / "profiles" / "system"

    def generations(self) -> None | list[Generation]:
        try:
            generations = subprocess.check_output(
                ["nix-env", "--list-generations", "--profile", self.path],
                stderr=subprocess.STDOUT,
                encoding="utf-8",
            )
            generations = [Generation.from_string(g) for g in generations.splitlines()]
            generations = [g for g in generations if not g.current]
            generations.sort(key=lambda g: g.id)
            return generations
        except subprocess.CalledProcessError as e:
            print(f"Skipping, cannot get generations for '{self}': {str(e.output).strip()}", file=sys.stderr)
            return None


def main(args: Args):
    print(args)


if __name__ == "__main__":
    main(args())
