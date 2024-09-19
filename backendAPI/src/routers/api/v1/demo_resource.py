import logging
from typing import Annotated, List
from uuid import UUID

from fastapi import APIRouter, Depends, Query

from core.security import (
    Guards,
    get_access_token_payload,
    optional_get_access_token_payload,
)
from core.types import GuardTypes
from crud.demo_resource import DemoResourceCRUD
from crud.tag import TagCRUD
from models.demo_resource import (
    DemoResource,
    DemoResourceCreate,
    DemoResourceRead,
    DemoResourceUpdate,
)

from .base import BaseView

logger = logging.getLogger(__name__)
router = APIRouter()


demo_resource_view = BaseView(DemoResourceCRUD, DemoResource)


# Post requires a user!
@router.post("/", status_code=201)
async def post_demo_resource(
    demo_resource: DemoResourceCreate,
    token_payload=Depends(get_access_token_payload),
    guards: GuardTypes = Depends(Guards(scopes=["api.write"], roles=["User"])),
) -> DemoResourceRead:
    """Creates a new demo resource."""
    return await demo_resource_view.post(demo_resource, token_payload, guards)


# The get functions are totally public
# TBD: still a policy is needed for the fine grained access control to make the resource public!
# The default create only grants "own" access to the user, how creates it!
@router.get("/", status_code=200)
async def get_all_demo_resources(
    # token_payload=Depends(get_access_token_payload),
    token_payload=Depends(optional_get_access_token_payload),
) -> list[DemoResourceRead]:
    """Returns all demo resources resources."""
    return await demo_resource_view.get(token_payload)


@router.get("/{demo_resource_id}", status_code=200)
async def get_demo_resource_by_id(
    demo_resource_id: UUID,
    # note: optional allows public access to those resources
    # where a public access policy is set
    # Fine grained access control handles this in the CRUD.
    token_payload=Depends(optional_get_access_token_payload),
) -> DemoResourceRead:
    """Returns a demo resource by id."""
    return await demo_resource_view.get_by_id(demo_resource_id, token_payload)


@router.put("/{demo_resource_id}", status_code=200)
async def put_category(
    demo_resource_id: UUID,
    demo_resource: DemoResourceUpdate,
    token_payload=Depends(get_access_token_payload),
    guards: GuardTypes = Depends(Guards(scopes=["api.write"], roles=["User"])),
) -> DemoResource:
    """Updates a category."""
    return await demo_resource_view.put(
        demo_resource_id, demo_resource, token_payload, guards
    )


@router.delete("/{demo_resource_id}", status_code=200)
async def delete_demo_resource(
    demo_resource_id: UUID,
    token_payload=Depends(get_access_token_payload),
    guards: GuardTypes = Depends(Guards(scopes=["api.write"], roles=["User"])),
) -> None:  # DemoResource:
    """Deletes a protected resource."""
    return await demo_resource_view.delete(demo_resource_id, token_payload, guards)


@router.post("/{resource_id}/tag/")
async def add_tag_to_demo_resource(
    resource_id: UUID,
    tag_ids: Annotated[List[UUID], Query()],
    token_payload=Depends(get_access_token_payload),
    guards: GuardTypes = Depends(Guards(scopes=["api.write"], roles=["User"])),
) -> DemoResourceRead:
    """Adds a tag to a demo resource."""
    # token = CurrentAccessToken(token_payload)
    # current_user = await token.provides_current_user()
    current_user = await demo_resource_view._check_token_against_guards(
        token_payload, guards
    )
    print("=== resource_id ===")
    print(resource_id)
    async with TagCRUD() as crud:
        for tag_id in tag_ids:
            print("=== tag_id ===")
            print(tag_id)
            await crud.add_child_to_parent(
                parent_id=resource_id,
                child_id=tag_id,
                current_user=current_user,
                inherit=True,
            )
    async with demo_resource_view.crud() as crud:
        return await crud.read_by_id(resource_id, current_user)
        # return await crud.add_tag(resource_id, tag_ids)


@router.get("/category/{category_id}")
async def get_all_in_category(
    category_id: UUID,
    token_payload=Depends(get_access_token_payload),
    guards: GuardTypes = Depends(Guards(roles=["User"])),
) -> list[DemoResource]:
    """Gets all demo resources that belong to specific category."""
    current_user = await demo_resource_view._check_token_against_guards(
        token_payload, guards
    )
    async with demo_resource_view.crud() as crud:
        return await crud.read_by_category_id(current_user, category_id)


@router.get("/tag/{tag_id}")
async def get_all_with_tag(
    tag_id: UUID,
    token_payload=Depends(get_access_token_payload),
    guards: GuardTypes = Depends(Guards(roles=["User"])),
) -> list[DemoResourceRead]:
    """Gets all demo resources that belong to specific tag."""
    current_user = await demo_resource_view._check_token_against_guards(
        token_payload, guards
    )
    async with demo_resource_view.crud() as crud:
        return await crud.read_by_tag_id(current_user, tag_id)
