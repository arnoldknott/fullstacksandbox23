import uuid
from datetime import datetime
from typing import Any
from types import SimpleNamespace
from unittest.mock import AsyncMock, Mock

import pytest

from core.types import CollectionInclude, CollectionSort, SortDirection
from crud.base import BaseCRUD
from models.presentation import Presentation, PresentationRead


@pytest.mark.anyio
async def test_read_entity_snapshot_enriches_and_orders_entities():
    resource_id = uuid.uuid4()
    creation_date = datetime(2026, 9, 1, 10, 0)
    last_modified_date = datetime(2026, 9, 2, 11, 0)
    resource = PresentationRead.model_validate(  # type: ignore[attr-defined]
        {"id": resource_id, "source": "intern:", "path": None}
    )
    crud: Any = BaseCRUD(Presentation, allow_standalone=True)  # type: ignore[misc]
    read_mock = AsyncMock(return_value=[resource])
    crud.read = read_mock
    crud.logging_crud.read_cursor = AsyncMock(return_value=42)
    crud.logging_crud.read_entity_metadata = AsyncMock(
        return_value={
            resource_id: {
                "creation_date": creation_date,
                "last_modified_date": last_modified_date,
            }
        }
    )
    crud.policy_crud.read_access_rights = AsyncMock(return_value={resource_id: "write"})

    snapshot = await crud.read_entity_snapshot(
        includes={
            CollectionInclude.creation_date,
            CollectionInclude.last_modified_date,
            CollectionInclude.access_right,
        },
        sort=CollectionSort.creation_date,
        direction=SortDirection.descending,
    )

    assert snapshot.cursor == 42
    assert len(snapshot.items) == 1
    assert snapshot.items[0].creation_date == creation_date
    assert snapshot.items[0].last_modified_date == last_modified_date
    assert snapshot.items[0].access_right == "write"
    assert read_mock.await_args is not None
    order_by = read_mock.await_args.kwargs["order_by"]
    assert len(order_by) == 2
    assert "DESC NULLS LAST" in str(order_by[0])
    crud.logging_crud.read_entity_metadata.assert_awaited_once_with([resource_id])
    crud.policy_crud.read_access_rights.assert_awaited_once()


@pytest.mark.anyio
async def test_read_entity_snapshot_skips_unrequested_metadata():
    resource = PresentationRead.model_validate(  # type: ignore[attr-defined]
        {"id": uuid.uuid4(), "source": "intern:", "path": None}
    )
    crud: Any = BaseCRUD(Presentation, allow_standalone=True)  # type: ignore[misc]
    crud.read = AsyncMock(return_value=[resource])
    crud.logging_crud.read_cursor = AsyncMock(return_value=0)
    crud.logging_crud.read_entity_metadata = AsyncMock()
    crud.policy_crud.read_access_rights = AsyncMock()

    snapshot = await crud.read_entity_snapshot()

    assert snapshot.cursor == 0
    assert len(snapshot.items) == 1
    assert snapshot.items[0].creation_date is None
    assert snapshot.items[0].last_modified_date is None
    assert snapshot.items[0].access_right is None
    crud.logging_crud.read_entity_metadata.assert_not_awaited()
    crud.policy_crud.read_access_rights.assert_not_awaited()


@pytest.mark.anyio
async def test_read_entity_snapshot_filters_by_authorized_parent_children():
    parent_id = uuid.uuid4()
    child_id = uuid.uuid4()
    crud: Any = BaseCRUD(Presentation, allow_standalone=True)  # type: ignore[misc]
    crud.read = AsyncMock(return_value=[])
    crud.logging_crud.read_cursor = AsyncMock(return_value=0)
    hierarchy_crud = SimpleNamespace(
        read=AsyncMock(return_value=[SimpleNamespace(child_id=child_id)])
    )
    crud.hierarchy_CRUD = Mock(return_value=hierarchy_crud)

    await crud.read_entity_snapshot(parent_id=parent_id)

    hierarchy_crud.read.assert_awaited_once_with(current_user=None, parent_id=parent_id)
    filters = crud.read.await_args.kwargs["filters"]
    assert len(filters) == 1
    assert child_id.hex in str(
        filters[0].compile(compile_kwargs={"literal_binds": True})
    )
