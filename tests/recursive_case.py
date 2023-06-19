from weaver import weave, unweave

"""
The complex case is 

A: 
    'b':  B

B:
    'a': A

When saving, we hold onto memory addresses for the items already saved within the parents. This causes

Cache: [0x1]
Saving A
Saving children of A
Saving 'b' of A - B [0x2]
Cache: [0x1, 0x2]
Saving children of B
Saving 'a': 
'a' already in cache - save marker to 'a'. 

Result;
{
    '__ptr__': 0x1
    'b': {
        '__ptr__': 0x2,
        'a': 0x1
    }
}

When loaded back in, keep references to all items. Ignore pointers on first sweep, but return references.
"""


def test_recursive() -> None:
    recursive_item = {}
    dut = {"a": recursive_item}
    dut["a"]["b"] = dut
    res = weave(dut)
    roundtrip = unweave(res)
    assert res == roundtrip
