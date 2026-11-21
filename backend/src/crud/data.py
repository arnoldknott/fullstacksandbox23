import logging
from uuid import UUID

from fastapi import HTTPException
from sqlmodel import col

from core.types import CurrentUserData
from crud.base import BaseCRUD
from crud.access import ResourceHierarchyCRUD
from models.data import Number, Text

logger = logging.getLogger(__name__)


class DataCRUD(BaseCRUD):
    async def update(self, current_user, object_id, new):
        changes = new.model_dump(exclude_unset=True)
        if "id" in changes and changes["id"] != object_id:
            logger.warning(
                "Resource identifiers cannot be changed through content updates."
            )
            raise HTTPException(
                status_code=422, detail="Resource identifiers cannot be changed."
            )
        required = "content" if self.model is Text else "value"
        if required in changes and changes[required] is None:
            logger.warning("Required resource content cannot be null.")
            raise HTTPException(status_code=422, detail=f"{required} cannot be null.")
        return await super().update(current_user, object_id, new)

    async def read_labeled(
        self,
        current_user: CurrentUserData | None,
        parent_id: UUID | None,
        label: str | None,
    ):
        if label is not None and parent_id is None:
            logger.warning("Label lookup requires a parent.")
            raise HTTPException(status_code=422, detail="A label requires parent-id.")
        filters = None
        if parent_id is not None:
            edges = await ResourceHierarchyCRUD(session=self.session).read(
                current_user, parent_id=parent_id
            )
            ids = [
                edge.child_id for edge in edges if label is None or edge.label == label
            ]
            filters = [col(self.model.id).in_(ids)]
        return await self.read(current_user=current_user, filters=filters)


class TextCRUD(DataCRUD):
    def __init__(self):
        super().__init__(Text, allow_standalone=True, allow_public_create=True)


class NumberCRUD(DataCRUD):
    def __init__(self):
        super().__init__(Number, allow_standalone=True, allow_public_create=True)
