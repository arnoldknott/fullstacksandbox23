import pytest

from core.types import CollectionInclude, CollectionSort
from main import fastapi_app


@pytest.mark.anyio
async def test_first_party_query_parameter_names_use_kebab_case():
    query_parameter_names = {
        parameter["name"]
        for path in fastapi_app.openapi()["paths"].values()
        for operation in path.values()
        if isinstance(operation, dict)
        for parameter in operation.get("parameters", [])
        if parameter.get("in") == "query"
    }

    assert not {name for name in query_parameter_names if "_" in name}


@pytest.mark.anyio
async def test_collection_query_values_use_kebab_case():
    query_values = {
        *(member.value for member in CollectionInclude),
        *(member.value for member in CollectionSort),
    }

    assert not {value for value in query_values if "_" in value}
