import inspect
import types
from typing import (
    Any,
    Dict,
    Union,
    Optional,
    List, Callable,
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


def _weave_fn(
        item: Callable, registry: WeaverRegistry, cache: Dict[int, Any] = None
) -> Union[WovenClass, CacheMarker, ArtefactID, SerializeableType, None]:
    try:
        fn_source = inspect.getsource(item)
        if fn_source is None:
            raise ValueError
        # Weave the fn_source string
        return _weave(fn_source, registry, cache)
    except (OSError, ValueError, TypeError):
        return None


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


def getmembers(object, predicate=None):
    """Return all members of an object as (name, value) pairs sorted by name.
    Optionally, only return members that satisfy a given predicate."""
    if inspect.isclass(object):
        mro = (object,) + inspect.getmro(object)
    else:
        mro = ()
    results = []
    processed = set()
    names = dir(object)
    # :dd any DynamicClassAttributes to the list of names if object is a class;
    # this may result in duplicate entries if, for example, a virtual
    # attribute with the same name as a DynamicClassAttribute exists
    try:
        for base in object.__bases__:
            for k, v in base.__dict__.items():
                if isinstance(v, types.DynamicClassAttribute):
                    names.append(k)
    except AttributeError:
        pass
    for key in names:
        # First try to get the value via getattr.  Some descriptors don't
        # like calling their __get__ (see bug #1785), so fall back to
        # looking in the __dict__.
        try:
            value = getattr(object, key)
            # handle the duplicate key
            if key in processed:
                raise AttributeError
        except (RuntimeError, AttributeError):
            for base in mro:
                if key in base.__dict__:
                    value = base.__dict__[key]
                    break
            else:
                # could be a (currently) missing slot member, or a buggy
                # __dir__; discard and move on
                continue
        if not predicate or predicate(value):
            results.append((key, value))
        processed.add(key)
    results.sort(key=lambda pair: pair[0])
    return results


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
    method_documentation = {key: _weave_fn(value, registry, cache) for (key, value) in getmembers(item, inspect.ismethod)}
    return WovenClass(
        pointer=id(item),
        metadata=ItemMetadataWithVersion.detect(item),
        artefacts=artefacts,
        documentation=documentation,
        method_source={method_name: fn_source for (method_name, fn_source) in method_documentation.items() if fn_source is not None},
        json={key: _weave(value, registry, cache) for (key, value) in state.items()}
    )
