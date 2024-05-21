from models.protected_resource import (
    ProtectedResource,
    ProtectedResourceCreate,
    ProtectedResourceRead,
    ProtectedResourceUpdate,
    ProtectedChild,
    ProtectedChildCreate,
    ProtectedChildRead,
    ProtectedChildUpdate,
    ProtectedGrandChild,
    ProtectedGrandChildCreate,
    ProtectedGrandChildRead,
    ProtectedGrandChildUpdate,
)

from .base import BaseCRUD


class ProtectedResourceCRUD(
    BaseCRUD[
        ProtectedResource,
        ProtectedResourceCreate,
        ProtectedResourceRead,
        ProtectedResourceUpdate,
    ]
):
    def __init__(self):
        super().__init__(ProtectedResource)


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
