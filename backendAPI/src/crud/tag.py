from models.tag import Tag, TagCreate, TagRead, TagUpdate

from .base import BaseCRUD


class TagCRUD(BaseCRUD[Tag, TagCreate, TagRead, TagUpdate]):
    def __init__(self):
        super().__init__(Tag, allow_standalone=True)
