from typing import Optional

from sqlmodel import Field, SQLModel


class DemoResourceCreate(SQLModel):
    name: str
    description: Optional[str] = None
    language: Optional[str] = None
    timezone: Optional[str] = None


class DemoResource(DemoResourceCreate, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)


class DemoResourceUpdate(DemoResourceCreate):
    name: Optional[str] = None
    # description: Optional[str] = None
    # language: Optional[str] = None
    # timezone: Optional[str] = None

    # Lots and lots of inspiration here:
    # TBD: url: str
    # TBD: add tags
    # TBD: add owner
    # TBD: add created_at
    # TBD: add updated_at
    # TBD: add deleted_at
    # TBD: add is_deleted
    # TBD: add is_active
    # TBD: add is_public
    # TBD: add is_private
    # TBD: add is_protected
    # TBD: add is_hidden
    # TBD: add is_secret
    # TBD: add is_internal
    # TBD: add is_external
    # TBD: add is_confidential
    # TBD: add is_publicly_readable
    # TBD: add is_publicly_writable
    # TBD: add is_publicly_deletable
    # TBD: add is_publicly_modifiable
    # TBD: add is_publicly_accessible
    # TBD: add is_publicly_visible
    # TBD: add is_publicly_hidden
    # TBD: add is_publicly_secret
    # TBD: add is_publicly_internal
    # TBD: add is_publicly_external
    # TBD: add is_publicly_confidential
    # TBD: add is_publicly_readable_by_owner
    # TBD: add is_publicly_writable_by_owner
    # TBD: add is_publicly_deletable_by_owner
    # TBD: add is_publicly_modifiable_by_owner
    # TBD: add is_publicly_accessible_by_owner
    # TBD: add is_publicly_visible_by_owner
    # TBD: add is_publicly_hidden_by_owner
    # TBD: add is_publicly_secret_by_owner
    # TBD: add is_publicly_internal_by_owner
    # TBD: add is_publicly_external_by_owner
    # TBD: add is_publicly_confidential_by_owner
    # TBD: add is_publicly_readable_by_group
    # TBD: add is_publicly_writable_by_group
    # TBD: add is_publicly_deletable_by_group
    # TBD: add is_publicly_modifiable_by_group
    # TBD: add is_publicly_accessible_by_group
    # TBD: add is_publicly_visible_by_group
    # TBD: add is_publicly_hidden_by_group
