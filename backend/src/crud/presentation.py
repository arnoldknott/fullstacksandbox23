from models.presentation import (
    Presentation,
    PresentationCreate,
    PresentationRead,
    PresentationUpdate,
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
