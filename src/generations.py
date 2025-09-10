import getpass
import os
import subprocess
from dataclasses import dataclass
from datetime import datetime
from enum import Enum
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


class ProfileError(RuntimeError): ...


class Profile(Enum):
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
                return (Path.home() / ".nix-profile").readlink()
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

    def generations(self) -> list[Generation]:
        try:
            generations = subprocess.check_output(
                ["nix-env", "--list-generations", "--profile", self.path],
                stderr=subprocess.STDOUT,
                encoding="utf-8",
            )
            generations = [Generation.from_string(g) for g in generations.splitlines()]
            generations = [g for g in generations if not g.current]
            generations.sort(key=lambda g: g.id, reverse=True)
            return generations
        except subprocess.CalledProcessError as e:
            raise ProfileError(
                f"Cannot get generations for {self}: {str(e.output).strip()}"
            )
