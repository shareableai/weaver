import pytest

from weaver.registry import WeaverRegistry
from weaver.unweave import unweave
from weaver.weave import weave


@pytest.mark.parametrize("dut", [(), (1,), b"123"])
def test_builtins_detection(dut):
    reg = WeaverRegistry.defaults()
    assert reg.try_get_serializer(dut) is not None
    woven_reg = weave(dut, reg)
    assert reg.try_get_deserializer(woven_reg) is not None


@pytest.mark.parametrize("dut", [(), (1,), b"123", [1, 2, 3]])
def test_builtins(dut) -> None:
    res = weave(dut)
    roundtrip = unweave(res)
    assert dut == roundtrip
