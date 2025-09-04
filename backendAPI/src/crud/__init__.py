"""CRUD: Create, Read, Update, Delete -
Utility functions to interact with the database using models
from /model and database configuration dependencies/databases.py."""

# Matches a BaseModel to a CRUD class:
# Format: <Model_class.__name__>: <CRUD_class>
registry_CRUD = {}