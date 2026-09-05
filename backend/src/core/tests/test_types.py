import pytest

from core.types import CollectionInclude, CollectionSort, SortDirection


@pytest.mark.parametrize(
    ("enum_type", "value"),
    [
        (CollectionInclude, "creation_date"),
        (CollectionInclude, "last_modified_date"),
        (CollectionInclude, "access_right"),
        (CollectionSort, "creation_date"),
        (SortDirection, "asc"),
        (SortDirection, "desc"),
    ],
)
def test_collection_options_accept_supported_values(enum_type, value):
    assert enum_type(value).value == value


@pytest.mark.parametrize(
    ("enum_type", "value"),
    [
        (CollectionInclude, "access_policies"),
        (CollectionSort, "last_accessed_date"),
        (SortDirection, "newest"),
    ],
)
def test_collection_options_reject_unsupported_values(enum_type, value):
    with pytest.raises(ValueError):
        enum_type(value)
