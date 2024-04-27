""" All models are imported here.
Database migrations - alembic - gets the connection to all used models here.
The folder also contains schemas, where schemas aren't explicit,
due to using sqlmodel."""

from .access import (
    IdentifierTypeLink,
    AccessPolicy,
    AccessLog,
    ResourceHierarchy,
)  # noqa F401

from .category import Category  # noqa F401
from .demo_resource import DemoResource  # noqa F401
from .demo_resource_tag_link import DemoResourceTagLink  # noqa F401
from .tag import Tag  # noqa F401
from .identity import (
    User,  # noqa F401
    AzureGroupUserLink,  # noqa F401
    AzureGroup,  # noqa F401
    IdentityHierarchy,  # noqa F401
)
from .protected_resource import ProtectedResource  # noqa F401
from .public_resource import PublicResource  # noqa F401
