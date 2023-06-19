from __future__ import annotations

__all__ = ["Resource"]

import hashlib
import pathlib
import tempfile
from io import BytesIO
from typing import Optional, SupportsBytes, Union

from artefact_link import PyArtefact


class Resource:
    inner: bytes
    inner_hash: Optional[int]

    def __init__(self, bytes_like: Union[bytes, SupportsBytes, BytesIO], tag: str):
        if isinstance(bytes_like, SupportsBytes):
            self.inner = self.write_tag(tag) + bytes_like.__bytes__()
        elif isinstance(bytes_like, BytesIO):
            bytes_like.seek(0)
            self.inner = self.write_tag(tag) + bytes_like.getvalue()
        else:
            self.inner = self.write_tag(tag) + bytes_like
        self.inner_hash = None

    @staticmethod
    def write_tag(tag: str) -> bytes:
        encoded_tag = tag.encode("utf-8")
        padding_bytes = Resource.tag_length_bytes() - len(encoded_tag)
        if padding_bytes > 0:
            return encoded_tag + b"\0" * padding_bytes
        elif padding_bytes < 0:
            raise RuntimeError("Tag exceeded maximum tag length")
        else:
            return encoded_tag

    @staticmethod
    def read_tag(tag_bytes: bytes) -> str:
        return tag_bytes.rstrip(b"\0").decode("utf-8")

    @staticmethod
    def tag_length_chars() -> int:
        """Maximum number of characters allowed within a tag.

        Max byte size is 512 bytes, which permits up to 512/4 = 128 characters.
        """
        return 128

    @staticmethod
    def tag_length_bytes() -> int:
        """Maximum number of characters allowed within a tag.

        Max byte size is 512 bytes, which permits up to 512/4 = 128 characters.
        """
        return 512

    def tag(self) -> str:
        return self.read_tag(self.inner[: self.tag_length_bytes()])

    def __bytes__(self) -> bytes:
        return self.inner[self.tag_length_bytes() :]

    def __hash__(self) -> int:
        """Not the same as the Artefact ID, which is calculated internally."""
        if self.inner_hash is None:
            self.inner_hash = int(hashlib.sha3_256(self.inner).hexdigest(), base=16)
        return self.inner_hash

    # TODO: From Artefact is the moment where the Artefact is downloaded and saved
    #   and therefore should be performed async.
    @staticmethod
    def from_artefact(artefact: PyArtefact) -> Resource:
        with tempfile.TemporaryDirectory() as t:
            data = bytearray(open(artefact.path(pathlib.Path(t)), "rb").read())
            tag = data[: Resource.tag_length_bytes()]
            del data[: Resource.tag_length_bytes()]
            return Resource(data, Resource.read_tag(tag))

    @staticmethod
    def from_weaver_artefact(data: bytes) -> Resource:
        data = bytearray(data)
        tag = data[: Resource.tag_length_bytes()]
        del data[: Resource.tag_length_bytes()]
        return Resource(data, Resource.read_tag(tag))
