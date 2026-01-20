import logging

from fastapi import HTTPException

from core.security import check_token_against_guards  # CurrentAccessToken
from core.types import GuardTypes
from crud import register_crud

logger = logging.getLogger(__name__)


# TBD: implement rate limiting
# TBD: implement pagination
# TBD: implement sorting
# TBD: implement filtering
# TBD: implement searching
# TBD: implement caching


class BaseView:
    """Base class for all views"""

    def __init__(self, crud):
        self.crud = crud
        register_crud(crud())

    # TBD: In a similar manner
    # - implement rate limiting
    # - implement pagination
    # - implement sorting

    async def post(self, object, token_payload, guards, parent_id=None, inherit=False):
        logger.info("POST view calls create CRUD")
        current_user = await check_token_against_guards(token_payload, guards)
        async with self.crud() as crud:
            created_object = await crud.create(object, current_user, parent_id, inherit)
            # if parent_id is not None:
            #     created_object = await crud.create(object, current_user, parent_id)
            # else:
            #     created_object = await crud.create(object, current_user)
        return created_object

    async def post_with_public_access(
        self,
        object,
        token_payload,
        guards: GuardTypes,
        parent_id=None,
        inherit=False,
    ):
        logger.info("POST view for public access calls create_public CRUD")
        current_user = await check_token_against_guards(token_payload, guards)
        async with self.crud() as crud:
            created_object = await crud.create_public(
                object, current_user, parent_id, inherit
            )
        return created_object

    async def post_add_child_to_parent(
        self,
        child_id,
        parent_id,
        token_payload=None,
        guards=None,
        inherit=False,
    ):
        logger.info("POST view to add child to parent calls add_child_to_parent CRUD")
        # user in child router for consistency
        current_user = await check_token_against_guards(token_payload, guards)
        async with self.crud() as crud:
            created_hierarchy = await crud.add_child_to_parent(
                child_id, parent_id, current_user, inherit
            )
        return created_hierarchy

    async def post_reorder_children(
        self,
        parent_id,
        child_id,
        position,
        other_child_id,
        token_payload=None,
        guards=None,
    ):
        logger.info("POST reorder children view calls reorder_children CRUD")
        current_user = await check_token_against_guards(token_payload, guards)
        if position not in ["start", "end"]:
            if not other_child_id:
                raise HTTPException(status_code=400, detail="Bad request.")
            elif position not in ["before", "after"]:
                raise HTTPException(status_code=400, detail="Bad request.")
        else:
            raise HTTPException(status_code=400, detail="Bad request.")
        async with self.crud() as crud:
            await crud.reorder_children(
                parent_id, child_id, position, other_child_id, current_user
            )

    async def post_file(
        self,
        file,
        token_payload,
        guards: GuardTypes,
        parent_id=None,
        inherit=False,
    ):
        logger.info("POST view to upload files")
        current_user = await check_token_against_guards(token_payload, guards)
        async with self.crud() as crud:
            uploaded_files_metadata = await crud.create_file(
                file, current_user, parent_id, inherit
            )
        return uploaded_files_metadata

    async def get(
        self,
        # get operation does not need a token_payload, if the resource is public
        token_payload=None,
        guards=None,
    ):
        logger.info("GET view to retrieve all objects from read CRUD")
        current_user = None
        if guards:
            current_user = await check_token_against_guards(token_payload, guards)
        elif token_payload:
            current_user = await check_token_against_guards(token_payload, None)
        async with self.crud() as crud:
            objects = await crud.read(current_user)

        return objects

    async def get_by_id(
        self,
        id,
        token_payload=None,
        guards=None,
    ):
        logger.info("GET by id view to retrieve specific object from read CRUD")
        current_user = None
        if guards:
            current_user = await check_token_against_guards(token_payload, guards)
        elif token_payload:
            current_user = await check_token_against_guards(token_payload, None)
        async with self.crud() as crud:
            object = await crud.read_by_id(id, current_user)
        return object

    async def get_file_by_id(
        self,
        id,
        token_payload=None,
        guards=None,
    ):
        logger.info(
            "GET file by id view to retrieve specific file from disk through read CRUD"
        )
        current_user = None
        if guards:
            current_user = await check_token_against_guards(token_payload, guards)
        elif token_payload:
            current_user = await check_token_against_guards(token_payload, None)
        async with self.crud() as crud:
            return await crud.read_file_by_id(id, current_user)

    async def put(
        self,
        id,
        object,
        token_payload,
        guards,
    ):
        logger.info("PUT updates a specific object through update CRUD")
        current_user = await check_token_against_guards(token_payload, guards)
        async with self.crud() as crud:
            updated_object = await crud.update(current_user, id, object)
        return updated_object

    async def put_file(
        self,
        id,
        file,
        token_payload,
        guards,
    ):
        logger.info("PUT updates a specific file through update CRUD")
        current_user = await check_token_against_guards(token_payload, guards)
        async with self.crud() as crud:
            updated_file = await crud.update_file(id, current_user, file)
        return updated_file

    async def put_file_metadata(
        self,
        id,
        file_metadata,
        token_payload,
        guards,
    ):
        logger.info(
            "PUT updates a specific file metadata including renaming through update CRUD"
        )
        current_user = await check_token_against_guards(token_payload, guards)
        async with self.crud() as crud:
            updated_file_metadata = await crud.update_file_metadata(
                id, current_user, file_metadata
            )
        return updated_file_metadata

    async def delete(
        self,
        id,
        token_payload,
        guards,
    ):
        logger.info("DELETE removes a specific object through delete CRUD")
        current_user = await check_token_against_guards(token_payload, guards)
        async with self.crud() as crud:
            deleted_object = await crud.delete(current_user, id)
        return deleted_object

    async def remove_child_from_parent(
        self,
        child_id,
        parent_id,
        token_payload,
        guards,
    ):
        logger.info(
            "DELETE removes a child from a parent through delete_child_from_parent CRUD"
        )
        current_user = await check_token_against_guards(token_payload, guards)
        async with self.crud() as crud:
            await crud.remove_child_from_parent(child_id, parent_id, current_user)
        return None

    async def delete_file(
        self,
        id,
        token_payload,
        guards,
    ):
        logger.info("DELETE removes a specific file through delete CRUD")
        current_user = await check_token_against_guards(token_payload, guards)
        async with self.crud() as crud:
            deleted_file = await crud.delete_file(id, current_user)
        return deleted_file
