import json

import pytest

from weaver.data import read_json_dict
from weaver.unweave import unweave
from weaver.weave import weave


class SimpleClass:
    b: int

    def __init__(self, b: int = 5) -> None:
        self.b = b

    def __eq__(self, other):
        return self.b == other.b


class ClassWithArtefact:
    b: bytes

    def __init__(self):
        self.b = b"123"

    def __eq__(self, other):
        return self.b == other.b


@pytest.mark.parametrize("dut", [SimpleClass()])
def test_simple_class(dut) -> None:
    res = weave(dut)
    dict_res = res.as_dict()
    roundtrip_res = read_json_dict(dict_res)
    _ = json.dumps(dict_res)
    roundtrip = unweave(roundtrip_res)
    assert dut == roundtrip


@pytest.mark.parametrize("dut", [ClassWithArtefact()])
def test_with_artefact(dut) -> None:
    res = weave(dut)
    dict_res = res.as_dict()
    roundtrip_res = read_json_dict(dict_res)
    _ = json.dumps(dict_res)
    roundtrip = unweave(roundtrip_res)
    assert dut == roundtrip
