from weaver.artefact_registry import ArtefactRegistry
from weaver.data import ArtefactID
from weaver.serializer import PickleSerializer


def test_roundtrip():
    registry = ArtefactRegistry()
    item = 2
    serialized_item = PickleSerializer.to_resource(item)
    artefact_id = ArtefactID(hash(serialized_item))
    registry.save_using_id(artefact_id, serialized_item.inner)
    roundtrip_item = registry.load_from_id(artefact_id)
    assert roundtrip_item == item
