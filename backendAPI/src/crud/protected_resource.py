from models.protected_resource import (
    ProtectedResource,
    ProtectedResourceCreate,
    ProtectedResourceRead,
    ProtectedResourceUpdate,
)

from .base import BaseCRUD

from core.security import CurrentUserData


class ProtectedResourceCRUD(
    BaseCRUD[
        ProtectedResource,
        ProtectedResourceCreate,
        ProtectedResourceRead,
        ProtectedResourceUpdate,
    ]
):
    def __init__(self, current_user: "CurrentUserData"):
        super().__init__(ProtectedResource, current_user)
