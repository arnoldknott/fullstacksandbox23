from .base import BaseCRUD

from models.presentation import (
    Presentation,
    # PresentationCreate,
    # PresentationRead,
    # PresentationUpdate,
)


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
