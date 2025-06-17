from datetime import datetime
from typing import List, Optional

from pydantic import BaseModel

from core.types import Action
from models.access import AccessPolicyRead

# Model mixins - combine with the SQLModel-based models in src/models/*.py
# to extend the models with meta data,
# like user_rights, access_policies, created_at, updated_at


class UserRightsMixin(BaseModel):
    """Mixin for user rights on a resource"""

    user_right: Optional[Action] = None


class AccessPolicyMixin(BaseModel):
    """Mixin for access policies on a resource"""

    access_policies: Optional[List[AccessPolicyRead]] = None


class CreatedAtMixin(BaseModel):
    """Mixin for created at timestamp"""

    creation_date: Optional[datetime] = None


class UpdatedAtMixin(BaseModel):
    """Mixin for updated at timestamp"""

    last_modified_date: Optional[datetime] = None
