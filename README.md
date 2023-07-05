# Weaver - Read and Write Python Objects

Weaver writes Python objects to a JSON format, storing the larger items as binary blobs on the local filesystem. 

## Why?

I wanted a way of saving Python objects that could still be examined in a common, human-readable, format, while still containing all the original data.
Also it's nice to be able to load and save from different versions of a library for breaking changes.

## How?
Same things as Pickle really. Save all the object state to a dictionary, throw it into JSON. When it comes to load, 
create a new object via `__new__` and add the state back in. Then do that recursively both ways. 

## What are the requirements for loading them back?
You need the same libraries loaded. Maybe not the same versions of those libraries though. If you have a data format 
that you need to save in one version, and load in the other, you can implement serializers for it;

Let's write a serializer for a class that looks like `set` from base python.

```python
from weaver.registry import WeaverSerializer, WeaverRegistry
from weaver.data import WovenClass, ItemMetadataWithVersion
from weaver.version import Version
from my_package import MySet
from typing import Any, Callable

class WeaverSetSerializer(WeaverSerializer[set]):
    _metadata = ItemMetadataWithVersion(
        module=tuple(["MyLibrary"]), name="MySet", version=Version(0, 1, 1)
    )

    @classmethod
    def weave(
            cls,
            item: MySet,
            registry: WeaverRegistry,
            cache: dict[int, Any],
            weave_fn: Callable,
    ) -> WovenClass:
        return WovenClass(
            pointer=id(item),
            metadata=cls._metadata,
            artefacts=set(),
            documentation={cls._metadata: MySet.__doc__},
            method_source={},
            json={"__inner__": [weave_fn(i) for i in item]},
        )
```


And a deserializer on the other side for our custom class that looks a lot like `set`.
```python
from weaver.registry import WeaverDeserializer, WeaverRegistry
from weaver.data import WovenClass, ItemMetadataWithVersion
from weaver.version import Version
from my_package import MySet
from typing import Any, Callable

class WeaverSetDeserializer(WeaverDeserializer[MySet]):
    _metadata = ItemMetadataWithVersion(
        module=tuple(["MyLibrary"]), name="MySet", version=Version(0, 1, 1)
    )

    @classmethod
    def unweave(
            cls,
            item: WovenClass,
            registry: WeaverRegistry,
            cache: dict[int, Any],
            unweave_fn: Callable,
    ) -> MySet:
        return MySet({unweave_fn(i) for i in item.json["__inner__"]})
```

So we can read from Version 0.1.1 and write to Version 0.1.1. We can also specify that we can read from 'AllVersions', although 
more complex constraints don't exist yet.

### Isn't this [Camel](https://github.com/eevee/camel), but for JSON?
Yes, but with tweaks. We fall back to Pickle, they had a clear philosophy against it. 