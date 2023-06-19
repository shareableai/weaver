from __future__ import annotations

from dataclasses import dataclass
from typing import Union


@dataclass(unsafe_hash=True)
class AllVersions:
    pass

    def __str__(self) -> str:
        return "AllVersions"

    @staticmethod
    def from_str(item: str) -> AllVersions:
        if item == "AllVersions":
            return AllVersions()


@dataclass(unsafe_hash=True)
class UnknownVersion:
    pass

    def __str__(self) -> str:
        return "UnknownVersion"

    @staticmethod
    def from_str(item: str) -> UnknownVersion:
        if item == "UnknownVersion":
            return UnknownVersion()


@dataclass(order=True, unsafe_hash=True)
class Version:
    major: int
    minor: int
    patch: int

    def __str__(self) -> str:
        return f"{self.major}.{self.minor}.{self.patch}"

    @staticmethod
    def from_str(item: str) -> Version:
        if "+" in item:
            versioning, _ = item.split("+", maxsplit=1)
        if item.count(".") == 0:
            major = int(item)
            return Version(major, 0, 0)
        if item.count(".") == 1:
            major, minor = item.split(".")
            return Version(int(major), int(minor), 0)
        major, minor, patch = item.split(".")
        return Version(int(major), int(minor), int(patch))


Versioning = Union[Version, AllVersions, UnknownVersion]
