from __future__ import annotations

import ast
from dataclasses import dataclass, field
from typing import (
    Dict,
    Type,
    Generic,
    TypeVar,
    Optional,
    Any,
    Callable,
    Union,
    Tuple,
    List,
    Set,
)

from weaver.data import ItemMetadata, WovenClass, ItemMetadataWithVersion, ArtefactID
from weaver.version import Versioning, AllVersions

T = TypeVar("T")


class WeaverSerde:
    @classmethod
    def generic_class(cls) -> type:
        """Return T"""
        return cls.__orig_bases__[0].__args__[0]


class WeaverSerializer(Generic[T], WeaverSerde):
    _metadata: ItemMetadataWithVersion

    @classmethod
    def weave(
            cls,
            item: T,
            registry: WeaverRegistry,
            cache: Dict[int, Any],
            weave_fn: Callable,
    ) -> WovenClass:
        raise NotImplementedError

    @classmethod
    def metadata(cls) -> ItemMetadata:
        return cls._metadata.without_version()


class WeaverDeserializer(Generic[T], WeaverSerde):
    _metadata: ItemMetadataWithVersion

    @classmethod
    def unweave(
            cls,
            woven_class: WovenClass,
            registry: WeaverRegistry,
            cache: Dict[int, Any],
            unweave_fn: Callable,
    ) -> T:
        raise NotImplementedError

    @classmethod
    def metadata(cls) -> ItemMetadata:
        return cls._metadata.without_version()


class WeaverBytesSerializer(WeaverSerializer[bytes]):
    _metadata = ItemMetadataWithVersion(
        module=tuple(["builtins"]), name="bytes", version=AllVersions()
    )

    @classmethod
    def weave(
            cls,
            item: bytes,
            registry: WeaverRegistry,
            cache: Dict[int, Any],
            weave_fn: Callable,
    ) -> WovenClass:
        return WovenClass(
            pointer=id(item),
            metadata=cls._metadata,
            artefacts=set(),
            documentation={cls._metadata: bytes.__doc__},
            method_source={},
            json={"__inner__": str(item)},
        )


class WeaverBytesDeserializer(WeaverDeserializer[bytes]):
    _metadata = ItemMetadataWithVersion(
        module=tuple(["builtins"]), name="bytes", version=AllVersions()
    )

    @classmethod
    def unweave(
            cls,
            item: WovenClass,
            registry: WeaverRegistry,
            cache: Dict[int, Any],
            unweave_fn: Callable,
    ) -> Any:
        return ast.literal_eval(item.json["__inner__"])


class WeaverTupleSerializer(WeaverSerializer[tuple]):
    _metadata = ItemMetadataWithVersion(
        module=tuple(["builtins"]), name="tuple", version=AllVersions()
    )

    @classmethod
    def weave(
            cls,
            item: Tuple,
            registry: WeaverRegistry,
            cache: Dict[int, Any],
            weave_fn: Callable,
    ) -> WovenClass:
        return WovenClass(
            pointer=id(item),
            metadata=cls._metadata,
            artefacts=set(),
            documentation={cls._metadata: Tuple.__doc__},
            method_source={},
            json={"__inner__": tuple([weave_fn(i) for i in item])},
        )


class WeaverTupleDeserializer(WeaverDeserializer[tuple]):
    _metadata = ItemMetadataWithVersion(
        module=tuple(["builtins"]), name="tuple", version=AllVersions()
    )

    @classmethod
    def unweave(
            cls,
            item: WovenClass,
            registry: WeaverRegistry,
            cache: Dict[int, Any],
            unweave_fn: Callable,
    ) -> Tuple:
        return tuple(unweave_fn(i) for i in item.json["__inner__"])


class WeaverSetSerializer(WeaverSerializer[set]):
    _metadata = ItemMetadataWithVersion(
        module=tuple(["builtins"]), name="set", version=AllVersions()
    )

    @classmethod
    def weave(
            cls,
            item: Set,
            registry: WeaverRegistry,
            cache: Dict[int, Any],
            weave_fn: Callable,
    ) -> WovenClass:
        return WovenClass(
            pointer=id(item),
            metadata=cls._metadata,
            artefacts=set(),
            documentation={cls._metadata: Set.__doc__},
            method_source={},
            json={"__inner__": [weave_fn(i) for i in item]},
        )


class WeaverSetDeserializer(WeaverDeserializer[set]):
    _metadata = ItemMetadataWithVersion(
        module=tuple(["builtins"]), name="set", version=AllVersions()
    )

    @classmethod
    def unweave(
            cls,
            item: WovenClass,
            registry: WeaverRegistry,
            cache: Dict[int, Any],
            unweave_fn: Callable,
    ) -> Set:
        return {unweave_fn(i) for i in item.json["__inner__"]}


class WeaverTypeSerializer(WeaverSerializer[type]):
    _metadata = ItemMetadataWithVersion(
        module=tuple(["builtins"]), name="type", version=AllVersions()
    )

    @classmethod
    def weave(
            cls,
            item: Type,
            registry: WeaverRegistry,
            cache: Dict[int, Any],
            weave_fn: Callable,
    ) -> WovenClass:
        return WovenClass(
            pointer=id(item),
            metadata=cls._metadata,
            artefacts=set(),
            documentation={cls._metadata: Type.__doc__},
            method_source={},
            json={"__inner__": str(item)},
        )


class WeaverTypeDeserializer(WeaverDeserializer[type]):
    _metadata = ItemMetadataWithVersion(
        module=tuple(["builtins"]), name="type", version=AllVersions()
    )

    @classmethod
    def unweave(
            cls,
            item: WovenClass,
            registry: WeaverRegistry,
            cache: Dict[int, Any],
            unweave_fn: Callable,
    ) -> Type:
        raise NotImplementedError


class WeaverArtefactIDSerializer(WeaverSerializer[ArtefactID]):
    _metadata = ItemMetadataWithVersion(
        module=tuple(["weaver", "data"]), name="ArtefactID", version=AllVersions()
    )

    @classmethod
    def weave(
            cls,
            item: ArtefactID,
            registry: WeaverRegistry,
            cache: Dict[int, Any],
            weave_fn: Callable,
    ) -> WovenClass:
        return WovenClass(
            pointer=id(item),
            metadata=cls._metadata,
            artefacts=set(),
            documentation={cls._metadata: ArtefactID.__doc__},
            method_source={},
            json={"__inner__": item.artefact_id},
        )


class WeaverArtefactIDDeserializer(WeaverDeserializer[ArtefactID]):
    _metadata = ItemMetadataWithVersion(
        module=tuple(["weaver", "data"]), name="ArtefactID", version=AllVersions()
    )

    @classmethod
    def unweave(
            cls,
            item: WovenClass,
            registry: WeaverRegistry,
            cache: Dict[int, Any],
            unweave_fn: Callable,
    ) -> ArtefactID:
        return ArtefactID(int(item.json["_id"]))


@dataclass
class WeaverRegistry:
    _serializer: Dict[ItemMetadata, Dict[Versioning, Type[WeaverSerializer]]] = field(
        default_factory=dict
    )
    _deserializer: Dict[
        ItemMetadata, Dict[Versioning, Type[WeaverDeserializer]]
    ] = field(default_factory=dict)

    @classmethod
    def defaults(cls) -> WeaverRegistry:
        registry = WeaverRegistry()
        registry.add_serializer(
            [
                WeaverBytesSerializer,
                WeaverBytesDeserializer,
                WeaverTupleSerializer,
                WeaverTupleDeserializer,
                WeaverSetSerializer,
                WeaverSetDeserializer,
                WeaverTypeSerializer,
                WeaverTypeDeserializer,
                WeaverArtefactIDSerializer,
                WeaverArtefactIDDeserializer,
            ]
        )
        return registry

    def add_serializer(
            self,
            serializer: Union[
                Type[WeaverSerializer],
                Type[WeaverDeserializer],
                List[Type[WeaverSerializer]],
                List[Type[WeaverDeserializer]],
            ],
    ) -> None:
        if isinstance(serializer, list):
            for s in serializer:
                self.add_serializer(s)
        elif WeaverSerializer in serializer.__mro__:
            metadata = serializer.metadata()
            try:
                self._serializer[metadata][AllVersions()] = serializer
            except KeyError:
                self._serializer[metadata] = {}
                self._serializer[metadata][AllVersions()] = serializer
        elif WeaverDeserializer in serializer.__mro__:
            metadata = serializer.metadata()
            try:
                self._deserializer[metadata][AllVersions()] = serializer
            except KeyError:
                self._deserializer[metadata] = {}
                self._deserializer[metadata][AllVersions()] = serializer

    def try_get_serializer(self, item) -> Optional[Type[WeaverSerializer]]:
        metadata_with_version = ItemMetadataWithVersion.detect(item)
        metadata = metadata_with_version.without_version()
        if metadata in self._serializer:
            serializers = self._serializer[metadata]
            if metadata_with_version.version in serializers:
                return serializers[metadata_with_version.version]
            elif AllVersions() in serializers:
                return serializers[AllVersions()]

    def try_get_deserializer(
            self, item: WovenClass
    ) -> Optional[Type[WeaverDeserializer]]:
        metadata_with_version = item.metadata
        metadata = metadata_with_version.without_version()
        if metadata in self._deserializer:
            deserializers = self._deserializer[metadata]
            if metadata_with_version.version in deserializers:
                return deserializers[metadata_with_version.version]
            elif AllVersions() in deserializers:
                return deserializers[AllVersions()]
