from models.presentation import (  # PresentationCreate,; PresentationRead,; PresentationUpdate,
    Presentation,
)

from .base import BaseCRUD


class PresentationCRUD(
    BaseCRUD[
        Presentation,
        Presentation.Create,
        Presentation.Read,
        Presentation.Update,
    ]
):
    def __init__(self):
        super().__init__(Presentation, allow_standalone=True)
