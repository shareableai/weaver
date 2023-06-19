__all__ = ["Serializable"]

import pathlib
import pickle
from abc import abstractmethod
from typing import Generic, Optional, TypeVar, Type

import weaver
from weaver.resource import Resource
from weaver.version import Version

T = TypeVar("T")


class Serializable(Generic[T]):
    @classmethod
    def version(cls) -> Version:
        major, minor, patch = weaver.__version__
        return Version(major, minor, patch)

    @staticmethod
    @abstractmethod
    def tag() -> str:
        raise NotImplementedError

    @staticmethod
    @abstractmethod
    def to_resource(item: T) -> Resource:
        raise NotImplementedError

    @classmethod
    def to_file(cls, item: T, filename: pathlib.Path) -> pathlib.Path:
        with open(filename, "wb") as f:
            f.write(cls.to_resource(item).inner)
        return filename

    @staticmethod
    @abstractmethod
    def from_resource(uninitialised_item: Optional[T], buffer: Resource) -> T:
        raise NotImplementedError

    def __hash__(self) -> int:
        return hash(self.__class__)


class PickleSerializer(Serializable[T]):
    @staticmethod
    def tag() -> str:
        return f"pickle;{Serializable.version}"

    @staticmethod
    def to_resource(item: T) -> Resource:
        return Resource(pickle.dumps(item), PickleSerializer.tag())

    @staticmethod
    def from_resource(uninitialised_item: Optional[T], buffer: Resource) -> T:
        return pickle.loads(buffer.__bytes__())


def serializer_factory(tag: str) -> Optional[Type[Serializable]]:
    for serializer in [PickleSerializer]:
        if serializer.tag() == tag:
            return serializer
