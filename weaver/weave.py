from typing import (
    Any,
    Dict,
    Union,
    Optional,
    List,
)

from weaver.artefact_registry import ArtefactRegistry
from weaver.data import (
    WovenClass,
    ItemMetadataWithVersion,
    CacheMarker,
    ArtefactID,
    SerializeableType,
)
from weaver.registry import WeaverRegistry
from weaver.serializer import PickleSerializer

from functools import partial


def weave(
    item: Any, registry: Optional[WeaverRegistry] = None
) -> Union[WovenClass, ArtefactID, List]:
    if registry is None:
        registry = WeaverRegistry.defaults()
    res = _weave(item, registry, None)
    # Top level return will always be a WovenClass or an ArtefactID
    assert isinstance(res, (WovenClass, ArtefactID, list))
    return res


def _weave(
    item: Any, registry: WeaverRegistry, cache: Dict[int, Any] = None
) -> Union[WovenClass, CacheMarker, ArtefactID, SerializeableType, None]:
    if item is None:
        return None
    if cache is None:
        cache = {}
    item_id = id(item)
    if isinstance(item, List):
        return [_weave(i, registry, cache) for i in item]
    if isinstance(item, SerializeableType):
        return item
    if item_id in cache:
        return CacheMarker(item_id)
    if (serializer := registry.try_get_serializer(item)) is not None:
        return serializer.weave(
            item, registry, cache, partial(_weave, registry=registry, cache=cache)
        )
    return generic_write(cache, registry, item)


def write_as_artefact(item: Any) -> ArtefactID:
    resource = PickleSerializer.to_resource(item)
    ArtefactRegistry().save_using_id(
        artefact_id=ArtefactID(hash(resource)), item=resource.inner
    )
    return ArtefactID(hash(resource))


def generic_write(
    cache: Dict[int, Any], registry: WeaverRegistry, item: Any
) -> Union[WovenClass, ArtefactID]:
    if hasattr(item, "__pyx_vtable__"):
        return write_as_artefact(item)
    try:
        _ = item.__new__(item.__class__ if hasattr(item, "__class__") else item)
    except TypeError:
        return write_as_artefact(item)

    if isinstance(item, dict):
        state = item
    elif hasattr(item, "__getstate__"):
        state = item.__getstate__()
    else:
        state = item.__dict__
    metadata = ItemMetadataWithVersion.detect(item)
    artefacts = set()
    if hasattr(item, "__doc__"):
        documentation_artefact = write_as_artefact(getattr(item, "__doc__"))
        documentation = {metadata: documentation_artefact}
        artefacts = artefacts | {documentation_artefact}
    else:
        documentation = {}
    return WovenClass(
        pointer=id(item),
        metadata=ItemMetadataWithVersion.detect(item),
        artefacts=artefacts,
        documentation=documentation,
        json={key: _weave(value, registry, cache) for (key, value) in state.items()},
    )
