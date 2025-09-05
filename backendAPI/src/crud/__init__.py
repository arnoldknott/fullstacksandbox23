"""CRUD: Create, Read, Update, Delete -
Utility functions to interact with the database using models
from /model and database configuration dependencies/databases.py."""

# Matches a BaseModel to a CRUD class:
# Format: <Model_class.__name__>: <CRUD_class>
registry_CRUDs = {}


def register_crud(crud_instance):
    if (
        hasattr(crud_instance, "model")
        and crud_instance.model.__name__ not in registry_CRUDs
    ):
        registry_CRUDs[crud_instance.model.__name__] = crud_instance
