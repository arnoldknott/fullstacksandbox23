""" All models are imported here.
Database migrations - alemic - gets the connection to all used models here.
The folder also contains schemas, where schemas aren't explicit,
due to using sqlmodel."""
from .category import Category  # noqa F401
from .demo_resource import DemoResource  # noqa F401
from .demo_resource_tag_link import DemoResourceTagLink  # noqa F401
from .tag import Tag  # noqa F401
