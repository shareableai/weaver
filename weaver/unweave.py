from functools import partial
from typing import Any, Tuple, Union, Dict, List, Set, Optional

from weaver.artefact_registry import ArtefactRegistry
from weaver.data import WovenClass, ArtefactID, SerializeableType
from weaver.registry import WeaverRegistry


def identify_class(module: Tuple[str], module_name: str) -> Any:
    top_level_module = __import__(
        ".".join(module), globals(), locals(), [module_name], 0
    )
    return getattr(top_level_module, module_name)


def default_unweave(base_class: Any, state: Dict[str, Any]) -> Any:
    base_class = base_class.__new__(base_class)
    if hasattr(base_class, "__setstate__"):
        base_class.__setstate__(state)
    else:
        if hasattr(base_class, "__attrs_attrs__"):
            base_class.__init__(**state)
        else:
            base_class.__dict__.update(state)
    return base_class


def _unweave(
    nest: Union[WovenClass, ArtefactID, SerializeableType],
    registry: WeaverRegistry,
    cache: Dict[int, Any],
) -> Any:
    if nest is None:
        return None
    if isinstance(nest, list):
        return [_unweave(item, registry, cache) for item in nest]
    if isinstance(nest, set):
        return {_unweave(item, registry, cache) for item in nest}
    if isinstance(nest, Dict):
        return {key: _unweave(value, registry, cache) for (key, value) in nest.items()}
    if isinstance(nest, SerializeableType):
        return nest
    if isinstance(nest, ArtefactID):
        return ArtefactRegistry().load_from_id(nest)
    if nest.pointer in cache:
        return cache[nest.pointer]
    if (deserializer := registry.try_get_deserializer(nest)) is not None:
        return deserializer.unweave(
            nest, registry, cache, partial(_unweave, registry=registry, cache=cache)
        )
    state = {key: _unweave(value, registry, cache) for (key, value) in nest.json.items()}
    base_class = identify_class(nest.metadata.module, nest.metadata.name)
    return default_unweave(base_class, state)


def unweave(
    nest: Union[WovenClass, ArtefactID, List, Set],
    registry: Optional[WeaverRegistry] = None,
) -> Any:
    if registry is None:
        registry = WeaverRegistry.defaults()
    cache = {}
    return _unweave(nest, registry, cache)
