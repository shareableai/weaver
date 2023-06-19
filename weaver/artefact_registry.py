import pathlib
from typing import Optional, Any

from weaver.data import ArtefactID
from weaver.resource import Resource
from weaver.serializer import serializer_factory


class ArtefactRegistry:
    def __init__(self, base_path: Optional[pathlib.Path] = None) -> None:
        if base_path is None:
            base_path = pathlib.Path.home() / ".weaver"
        base_path = base_path / "artefacts"
        base_path.mkdir(parents=True, exist_ok=True)
        self.base_path = base_path

    def load_from_id(self, artefact_id: ArtefactID) -> Any:
        with open(self.base_path / str(artefact_id), "rb") as f:
            resource = Resource.from_weaver_artefact(f.read())
            return serializer_factory(resource.tag()).from_resource(None, resource)

    def save_using_id(self, artefact_id: ArtefactID, item: bytes) -> None:
        with open(self.base_path / str(artefact_id), "wb") as f:
            f.write(item)
