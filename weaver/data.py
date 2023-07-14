from __future__ import annotations

from dataclasses import dataclass
from typing import (
    Set,
    Any,
    Dict,
    Union,
    Tuple,
)

import weaver
from weaver.version import Versioning, AllVersions, Version, UnknownVersion


class IncorrectParseError(BaseException):
    pass


SerializeableType = Union[int, float, str, list]


def read_json_dict(
    item: Union[Dict, list[Dict]]
) -> Union[WovenClass, ArtefactID, list[Union[WovenClass, ArtefactID]]]:
    if isinstance(item, list):
        return [read_json_dict(i) for i in item]
    if not isinstance(item, Dict):
        return item
    for key in ["pointer", "metadata", "artefacts", "documentation", "json"]:
        if key not in item:
            if "_id" in item:
                return ArtefactID(item["_id"])
            print(f"Unusual key {key=} found")
            raise IncorrectParseError
        return WovenClass(
            pointer=item["pointer"],
            metadata=ItemMetadataWithVersion.read(item["metadata"]),
            artefacts=set([ArtefactID.from_dict(x) for x in item["artefacts"]]),
            documentation={
                ItemMetadata.read(key): value
                for (key, value) in item["documentation"].items()
            },
            method_source=item["method_source"],
            json={
                read_json_dict(key): read_json_dict(value)
                for (key, value) in item["json"].items()
            },
        )


@dataclass
class ArtefactID:
    _id: int

    def as_dict(self) -> Dict[str, Any]:
        return WovenClass(
            pointer=id(self),
            metadata=ItemMetadataWithVersion(
                module=tuple(["weaver", "data"]),
                name="ArtefactID",
                version=Version(*weaver.__version__),
            ),
            artefacts=set(),
            documentation={},
            method_source={},
            json={"_id": self._id},
        ).as_dict()
    
    @staticmethod
    def from_dict(item: dict) -> ArtefactID:
        return ArtefactID(
            _id=item['json']['_id']
        )

    def __hash__(self) -> int:
        return self.artefact_id

    @property
    def artefact_id(self) -> int:
        return self._id


@dataclass
class ItemMetadata:
    module: Tuple[str]
    name: str

    def __hash__(self) -> int:
        return hash(self.module + tuple([self.name]))

    @staticmethod
    def detect(item: Any) -> ItemMetadata:
        name = getattr(item, "__name__", getattr(item.__class__, "__name__"))
        module = tuple(
            getattr(item, "__module__", getattr(item.__class__, "__module__")).split(
                "."
            )
        )
        top_level_module = __import__(module[0], globals(), locals(), [], 0)
        return ItemMetadata(module=module, name=name)

    @staticmethod
    def read(item: Dict[str, Union[Tuple[str], str]] | str) -> ItemMetadata:
        if isinstance(item, str):
            return ItemMetadata.from_str(item)
        for key in ItemMetadata.__annotations__.keys():
            if key not in item:
                print(f"key {key=} not in item")
                print(f"{item=}")
                raise IncorrectParseError
        return ItemMetadata(item["module"], item["name"])
    
    def to_str(self) -> str:
        return f"{'$'.join(self.module)}:{self.name}"

    @staticmethod
    def from_str(item: str) -> ItemMetadata:
        module, name = item.split(':')
        return ItemMetadata(
            tuple(module.split('$')),
            name
        )


@dataclass
class ItemMetadataWithVersion(ItemMetadata):
    version: Versioning

    @staticmethod
    def detect(item: Any) -> ItemMetadataWithVersion:
        name = getattr(item, "__name__", getattr(item.__class__, "__name__"))
        module = tuple(
            getattr(item, "__module__", getattr(item.__class__, "__module__")).split(
                "."
            )
        )
        top_level_module = __import__(module[0], globals(), locals(), [], 0)
        version = getattr(top_level_module, "__version__", None)
        if version is None:
            version = UnknownVersion()
        else:
            version = Version.from_str(version)
        return ItemMetadataWithVersion(module=module, name=name, version=version)

    def without_version(self) -> ItemMetadata:
        return ItemMetadata(self.module, self.name)

    @staticmethod
    def read(item: Dict[str, Union[Tuple[str], str, str]]) -> ItemMetadataWithVersion:
        for key in ItemMetadataWithVersion.__annotations__.keys():
            if key not in item:
                print(f"key {key=} not in item")
                raise IncorrectParseError
        if item["version"] == "AllVersions":
            version = AllVersions()
        elif item["version"] == "UnknownVersion":
            version = UnknownVersion()
        else:
            version = Version.from_str(item["version"])
        return ItemMetadataWithVersion(tuple(item["module"]), item["name"], version)

    def as_dict(self) -> Dict[str, Any]:
        return {
            "module": list(self.module),
            "name": self.name,
            "version": self.version.__str__(),
        }

    def __hash__(self) -> int:
        return hash(tuple(list(self.module) + list([self.name, self.version])))


@dataclass
class WovenClass:
    pointer: int
    metadata: ItemMetadataWithVersion
    artefacts: Set[ArtefactID]
    documentation: Dict[ItemMetadata, str]
    method_source: Dict[str, str]
    json: Dict[str, Any]

    @classmethod
    def _convert(cls, item) -> Any:
        if isinstance(item, (WovenClass, ArtefactID)):
            return item.as_dict()
        elif isinstance(item, list):
            return [cls._convert(i) for i in item]
        elif isinstance(item, set):
            return {cls._convert(i) for i in item}
        elif isinstance(item, tuple):
            return tuple([cls._convert(i) for i in item])
        elif isinstance(item, Dict):
            return {
                cls._convert(key): cls._convert(value) for (key, value) in item.items()
            }
        else:
            return item

    @classmethod
    def _minimal_convert(cls, item) -> Any:
        if isinstance(item, WovenClass):
            return item.as_minimal_dict()
        elif isinstance(item, ArtefactID):
            return f"ArtefactID: {item.artefact_id}"
        elif isinstance(item, list):
            return [cls._minimal_convert(i) for i in item]
        elif isinstance(item, set):
            return {cls._minimal_convert(i) for i in item}
        elif isinstance(item, tuple):
            return tuple([cls._minimal_convert(i) for i in item])
        elif isinstance(item, Dict):
            return {
                cls._minimal_convert(key): cls._minimal_convert(value)
                for (key, value) in item.items()
            }
        else:
            return item

    def as_dict(self) -> Dict[str, Any]:
        # TODO: Move Documentation into a single top level object - potentially move into Artefacts?
        return {
            "pointer": self.pointer,
            "metadata": self.metadata.as_dict(),
            "artefacts": [self._convert(a) for a in list(self.artefacts)],
            "documentation": {
                key.to_str(): self._convert(value)
                for (key, value) in self.documentation.items()
            },
            "method_source": self.method_source,
            "json": self._convert(self.json),
        }

    def as_minimal_dict(self) -> Dict[str, Any]:
        metadata = ".".join(self.metadata.module) + "." + self.metadata.name
        return self._minimal_convert(self.json | {"version": metadata})


@dataclass
class CacheMarker:
    _id: int

    def __write__(self) -> WovenClass:
        return WovenClass(
            pointer=self._id,
            metadata=ItemMetadataWithVersion(
                module=tuple(["weaver", "data"]),
                name="CacheMarker",
                version=weaver.__version__,
            ),
            artefacts=set(),
            documentation={},
            json={},
        )

    @staticmethod
    def read(item: Dict[str, Any]) -> CacheMarker:
        for key in ["__artefact_id__"]:
            if key not in item:
                print(f"key {key=} not in item")
                raise IncorrectParseError
        return CacheMarker(item["__artefact_id__"])
