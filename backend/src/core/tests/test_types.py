import pytest

from core.types import CollectionInclude, CollectionSort, SortDirection


@pytest.mark.parametrize(
    ("enum_type", "value"),
    [
        (CollectionInclude, "creation-date"),
        (CollectionInclude, "last-modified-date"),
        (CollectionInclude, "access-right"),
        (CollectionSort, "creation-date"),
        (SortDirection, "asc"),
        (SortDirection, "desc"),
    ],
)
@pytest.mark.anyio
async def test_collection_options_accept_supported_values(enum_type, value):
    assert enum_type(value).value == value


@pytest.mark.parametrize(
    ("enum_type", "value"),
    [
        (CollectionInclude, "access-policies"),
        (CollectionSort, "last-accessed-date"),
        (SortDirection, "newest"),
    ],
)
@pytest.mark.anyio
async def test_collection_options_reject_unsupported_values(enum_type, value):
    with pytest.raises(ValueError):
        enum_type(value)
