from .base import BaseCRUD

from models.presentation import (
    Presentation,
    PresentationCreate,
    PresentationRead,
    PresentationUpdate,
)


class PresentationCRUD(
    BaseCRUD[
        Presentation,
        PresentationCreate,
        PresentationRead,
        PresentationUpdate,
    ]
):
    def __init__(self):
        super().__init__(Presentation)