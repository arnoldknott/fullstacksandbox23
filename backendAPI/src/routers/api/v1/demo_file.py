import logging
from typing import List
from uuid import UUID

from fastapi import APIRouter, Depends, File, UploadFile
from fastapi.responses import FileResponse

from core.security import Guards, get_access_token_payload
from core.types import GuardTypes
from crud.demo_file import DemoFileCRUD
from models.demo_file import DemoFile

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
