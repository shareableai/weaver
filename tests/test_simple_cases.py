import pytest

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
    roundtrip = unweave(res)
    assert dut == roundtrip


@pytest.mark.parametrize("dut", [ClassWithArtefact()])
def test_with_artefact(dut) -> None:
    res = weave(dut)
    roundtrip = unweave(res)
    assert dut == roundtrip
