import logging
from typing import Annotated, List
from uuid import UUID

from fastapi import APIRouter, Depends, File, Form, UploadFile
from fastapi.responses import FileResponse

from core.security import Guards, get_access_token_payload
from core.types import GuardTypes
from crud.demo_file import DemoFileCRUD
from models.demo_file import DemoFile, DemoFileUpdate

from .base import BaseView

logger = logging.getLogger(__name__)
router = APIRouter()

demo_file_view = BaseView(DemoFileCRUD, DemoFile)
# roles = ["User"] is required for the whole router in main.py!


@router.post("/files/", status_code=201)
async def post_demo_file(
    files: List[UploadFile] = File(...),
    token_payload=Depends(get_access_token_payload),
    guards: GuardTypes = Depends(Guards(scopes=["api.write"])),
) -> List[DemoFile]:
    """Creates a new demo file."""
    files_metadata = []
    for file in files:
        files_metadata.append(
            await demo_file_view.post_file(file, token_payload, guards)
        )
    return files_metadata


@router.get("/file/{file_id}", status_code=200)
async def get_demo_file_by_id(
    file_id: UUID,
    token_payload=Depends(get_access_token_payload),
    guards: GuardTypes = Depends(Guards(scopes=["api.read"])),
) -> FileResponse:
    """Retrieves a demo file by ID."""
    return await demo_file_view.get_file_by_id(file_id, token_payload, guards)


# TBD: get all files - need to be zipped in CRUD:
# @router.get("/files/", status_code=200)
# async def get_all_demo_files(
#     file_ids: List[UUID] = None,
#     token_payload=Depends(get_access_token_payload),
#     guards: GuardTypes = Depends(Guards(scopes=["api.read"])),
# ) -> List[DemoFile]:
#     """Returns all demo files."""
#     return await demo_file_view.get_files(token_payload, guards)


@router.put("/file/{file_id}", status_code=200)
async def put_demo_file_by_id(
    file_id: UUID,
    files: Annotated[UploadFile | None, File()] = None,
    demo_file_metadata: Annotated[DemoFileUpdate | None, Form()] = None,
    token_payload=Depends(get_access_token_payload),
    guards: GuardTypes = Depends(Guards(scopes=["api.write"])),
) -> DemoFile:
    """Updates a demo file by ID."""
    print("=== API - v1 - demo_file - put_demo_file_by_id ===")
    return await demo_file_view.put_file(
        file_id, files, demo_file_metadata, token_payload, guards
    )


# TBD: rename a file:
# @router.put("/file/rename/{file_id}", status_code=200)
# async def put_demo_file_rename(
#     file_id: UUID,
#     demo_file: DemoFileUpdate,
#     token_payload=Depends(get_access_token_payload),
#     guards: GuardTypes = Depends(Guards(scopes=["api.write"])),
# ) -> DemoFile:
#     """Updates a demo file by ID."""
#     return await demo_file_view.put_rename_file(
#         file_id, demo_file, token_payload, guards
#     )


# TBD: delete a file:
# @router.delete("/file/{file_id}", status_code=200)
# async def delete_demo_file_by_id(
#     file_id: UUID,
#     token_payload=Depends(get_access_token_payload),
#     guards: GuardTypes = Depends(Guards(scopes=["api.write"])),
# ) -> DemoFile:
#     """Deletes a demo file by ID."""
#     return await demo_file_view.delete_file_by_id(file_id, token_payload, guards)
