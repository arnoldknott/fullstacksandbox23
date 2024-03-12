from models.protected_resource import (
    ProtectedResource,
    ProtectedResourceCreate,
    ProtectedResourceRead,
    ProtectedResourceUpdate,
)
from core.types import ResourceType
from .base import BaseCRUD

# # if TYPE_CHECKING:
# #     from core.security import CurrentUserData
# from core.security import CurrentUserData


class ProtectedResourceCRUD(
    BaseCRUD[
        ProtectedResource,
        ProtectedResourceCreate,
        ProtectedResourceRead,
        ProtectedResourceUpdate,
    ]
):
    # def __init__(self, current_user):
    # def __init__(self, current_user: "CurrentUserData"):
    #     super().__init__(ProtectedResource, current_user)
    def __init__(self):
        super().__init__(ProtectedResource, ResourceType.protected_resource)
