from models.presentation import (
    PresentationCreate,
    PresentationRead,
    PresentationUpdate,
    Presentation,
)

from .base import BaseCRUD


class PresentationCRUD(
    BaseCRUD[
        Presentation,
        PresentationCreate,
        PresentationRead,
        PresentationUpdate,
    ]
):
    def __init__(self):
        super().__init__(Presentation, allow_standalone=True)
