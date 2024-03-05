import logging

from models.access import AccessPolicy, AccessLogging
from .base import BaseCRUD

logger = logging.getLogger(__name__)


class AccessPolicyCRUD(
    BaseCRUD[AccessPolicy, AccessPolicy, AccessPolicy, AccessPolicy]
):
    """CRUD for access control policies"""

    def __init__(self):
        """Initializes the CRUD for access control policies."""
        super().__init__(AccessPolicy)


class AccessLoggingCRUD(
    BaseCRUD[AccessLogging, AccessLogging, AccessLogging, AccessLogging]
):
    """CRUD for access attempts logging."""

    def __init__(self):
        super().__init__(AccessLogging)

    def update(self):
        """Preventing update for access logging."""
        pass

    def delete(self):
        """Preventing delete for access logging."""
        pass
