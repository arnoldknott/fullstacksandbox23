from models.protected_resource import (
    ProtectedChild,
    ProtectedChildCreate,
    ProtectedChildRead,
    ProtectedChildUpdate,
    ProtectedGrandChild,
    ProtectedGrandChildCreate,
    ProtectedGrandChildRead,
    ProtectedGrandChildUpdate,
    ProtectedResource,
    ProtectedResourceCreate,
    ProtectedResourceRead,
    ProtectedResourceUpdate,
)

from .base import BaseCRUD

# CRUD's for family of protected resources with parent-child relationships in three generations:
# - protected resource
#   - protected child
#     - protected grand child


class ProtectedResourceCRUD(
    BaseCRUD[
        ProtectedResource,
        ProtectedResourceCreate,
        ProtectedResourceRead,
        ProtectedResourceUpdate,
    ]
):
    def __init__(self):
        super().__init__(ProtectedResource, allow_everyone=["create"])


class ProtectedChildCRUD(
    BaseCRUD[
        ProtectedChild,
        ProtectedChildCreate,
        ProtectedChildRead,
        ProtectedChildUpdate,
    ]
):
    def __init__(self):
        super().__init__(ProtectedChild)


class ProtectedGrandChildCRUD(
    BaseCRUD[
        ProtectedGrandChild,
        ProtectedGrandChildCreate,
        ProtectedGrandChildRead,
        ProtectedGrandChildUpdate,
    ]
):
    def __init__(self):
        super().__init__(ProtectedGrandChild)
