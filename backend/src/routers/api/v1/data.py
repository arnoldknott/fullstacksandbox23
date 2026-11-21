from typing import Annotated
from uuid import UUID

from fastapi import APIRouter, Depends, Query, Response

from core.security import (
    AllowAnonymous,
    Guards,
    LinkedInGuard,
    MicrosoftGuard,
    check_token_against_guards,
    provide_http_token_payload,
)
from core.types import (
    Action,
    CollectionInclude,
    CollectionSort,
    GuardTypes,
    KebabCase,
    SortDirection,
)
from crud.data import NumberCRUD, TextCRUD
from models.data import (
    NumberCreate,
    NumberExtended,
    NumberRead,
    NumberUpdate,
    TextCreate,
    TextExtended,
    TextRead,
    TextUpdate,
)
from routers.api.v1.base import BaseView

router = APIRouter()
text_view = BaseView(TextCRUD)
number_view = BaseView(NumberCRUD)

read_guards = Guards(
    MicrosoftGuard(scopes=["api.read"]), LinkedInGuard(), AllowAnonymous()
)
write_guards = Guards(
    MicrosoftGuard(scopes=["api.read", "api.write"], roles=["User"]),
    LinkedInGuard(),
    AllowAnonymous(),
)
owner_guards = Guards(
    MicrosoftGuard(scopes=["api.read", "api.write"], roles=["User"]), LinkedInGuard()
)
Token = Annotated[dict | None, Depends(provide_http_token_payload)]
Parent = Annotated[UUID | None, Query(alias="parent-id")]
Label = Annotated[KebabCase | None, Query()]
Includes = Annotated[list[CollectionInclude] | None, Query()]


async def _collection(view, response, token_payload, guards, parent_id, label):
    current_user = await check_token_against_guards(token_payload, guards)
    async with view.crud() as crud, view.entity_response(crud, response):
        return await crud.read_labeled(current_user, parent_id, label)


@router.get("/text", response_model=list[TextRead])
async def get_texts(
    response: Response,
    parent_id: Parent = None,
    label: Label = None,
    token_payload: Token = None,
    guards: GuardTypes = Depends(read_guards),
):
    return await _collection(
        text_view, response, token_payload, guards, parent_id, label
    )


@router.get("/number", response_model=list[NumberRead])
async def get_numbers(
    response: Response,
    parent_id: Parent = None,
    label: Label = None,
    token_payload: Token = None,
    guards: GuardTypes = Depends(read_guards),
):
    return await _collection(
        number_view, response, token_payload, guards, parent_id, label
    )


@router.get("/text/snapshot", response_model=list[TextExtended])
async def get_text_snapshot(
    response: Response,
    parent_id: Parent = None,
    include: Includes = None,
    sort: CollectionSort | None = None,
    direction: SortDirection = SortDirection.ascending,
    token_payload: Token = None,
    guards: GuardTypes = Depends(read_guards),
):
    snapshot = await text_view.get_entity_snapshot(
        token_payload, guards, include, sort, direction, parent_id, response=response
    )
    return snapshot.items


@router.get("/number/snapshot", response_model=list[NumberExtended])
async def get_number_snapshot(
    response: Response,
    parent_id: Parent = None,
    include: Includes = None,
    sort: CollectionSort | None = None,
    direction: SortDirection = SortDirection.ascending,
    token_payload: Token = None,
    guards: GuardTypes = Depends(read_guards),
):
    snapshot = await number_view.get_entity_snapshot(
        token_payload, guards, include, sort, direction, parent_id, response=response
    )
    return snapshot.items


@router.get("/text/{resource_id}", response_model=TextRead)
async def get_text(
    resource_id: UUID,
    response: Response,
    token_payload: Token = None,
    guards: GuardTypes = Depends(read_guards),
):
    return await text_view.get_by_id(
        resource_id, token_payload, guards, response=response
    )


@router.get("/number/{resource_id}", response_model=NumberRead)
async def get_number(
    resource_id: UUID,
    response: Response,
    token_payload: Token = None,
    guards: GuardTypes = Depends(read_guards),
):
    return await number_view.get_by_id(
        resource_id, token_payload, guards, response=response
    )


@router.post("/text", status_code=201, response_model=TextRead)
async def post_text(
    content: TextCreate,
    parent_id: Parent = None,
    label: Label = None,
    inherit: bool = False,
    public: bool = False,
    public_action: Annotated[Action | None, Query(alias="public-action")] = None,
    token_payload: Token = None,
    guards: GuardTypes = Depends(write_guards),
):
    return await text_view.post(
        content,
        token_payload,
        guards,
        parent_id,
        inherit,
        public,
        public_action,
        label,
    )


@router.post("/number", status_code=201, response_model=NumberRead)
async def post_number(
    content: NumberCreate,
    parent_id: Parent = None,
    label: Label = None,
    inherit: bool = False,
    public: bool = False,
    public_action: Annotated[Action | None, Query(alias="public-action")] = None,
    token_payload: Token = None,
    guards: GuardTypes = Depends(write_guards),
):
    return await number_view.post(
        content,
        token_payload,
        guards,
        parent_id,
        inherit,
        public,
        public_action,
        label,
    )


@router.put("/text/{resource_id}", response_model=TextRead)
async def put_text(
    resource_id: UUID,
    content: TextUpdate,
    token_payload: Token = None,
    guards: GuardTypes = Depends(write_guards),
):
    return await text_view.put(resource_id, content, token_payload, guards)


@router.put("/number/{resource_id}", response_model=NumberRead)
async def put_number(
    resource_id: UUID,
    content: NumberUpdate,
    token_payload: Token = None,
    guards: GuardTypes = Depends(write_guards),
):
    return await number_view.put(resource_id, content, token_payload, guards)


@router.delete("/text/{resource_id}")
async def delete_text(
    resource_id: UUID,
    token_payload: Token = None,
    guards: GuardTypes = Depends(owner_guards),
):
    return await text_view.delete(resource_id, token_payload, guards)


@router.delete("/number/{resource_id}")
async def delete_number(
    resource_id: UUID,
    token_payload: Token = None,
    guards: GuardTypes = Depends(owner_guards),
):
    return await number_view.delete(resource_id, token_payload, guards)
