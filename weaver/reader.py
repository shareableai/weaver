import json

from typing import Union, Dict, Any

from weaver.data import WovenClass, ArtefactID, IncorrectParseError


def read_file(file: str) -> Union[ArtefactID, WovenClass]:
    json_file: Dict[str, Any] = json.loads(file)
    try:
        item = ArtefactID.read(json_file)
        return item
    except IncorrectParseError:
        pass
    # Assume Dicts will always be converted to WovenClasses.
    return WovenClass.read(json_file)
