import uuid
from typing import TYPE_CHECKING, List, Optional

from sqlmodel import Field, Relationship, SQLModel

# from models.access import IdentifierTypeLink


# from .demo_resource import DemoResource

if TYPE_CHECKING:
    from .demo_resource import DemoResource


class CategoryCreate(SQLModel):
    name: str = Field(max_length=12)
    description: Optional[str] = None


class Category(CategoryCreate, table=True):
    # id: Optional[uuid.UUID] = Field(default_factory=uuid.uuid4, primary_key=True)
    # id: Optional[uuid.UUID] = Field(
    #     default=None, foreign_key="identifiertypelink.id", primary_key=True
    # )
    id: Optional[uuid.UUID] = Field(
        default_factory=uuid.uuid4,
        foreign_key="identifiertypelink.id",
        primary_key=True,
    )

    demo_resources: List["DemoResource"] = Relationship(
        back_populates="category", sa_relationship_kwargs={"lazy": "selectin"}
    )


class CategoryUpdate(CategoryCreate):
    name: Optional[str] = None


class CategoryRead(CategoryCreate):
    id: uuid.UUID


# class CategoryReadWithDemoResources(Category):
#     demo_resources: List[DemoResource] = []


# suggestion from co-pilot on how to join the access policies with category and demo_resource:class Category(Base):
#     __tablename__ = 'category'
#     id = Column(Integer, primary_key=True)
#     demo_resources = relationship(
#         "DemoResource",
#         secondary="demo_resource_category_link",
#         back_populates="categories",
#     )

# class DemoResource(Base):
#     __tablename__ = 'demo_resource'
#     id = Column(Integer, primary_key=True)
#     categories = relationship(
#         "Category",
#         secondary="demo_resource_category_link",
#         back_populates="demo_resources",
#     )

# class AccessPolicy(Base):
#     __tablename__ = 'access_policy'
#     id = Column(Integer, primary_key=True)
#     user_id = Column(Integer, ForeignKey('user.id'))
#     demo_resource_category_link_id = Column(Integer, ForeignKey('demo_resource_category_link.id'))
#     demo_resource_category_link = relationship("DemoResourceCategoryLink", back_populates="access_policies")

# class DemoResourceCategoryLink(Base):
#     __tablename__ = 'demo_resource_category_link'
#     id = Column(Integer, primary_key=True)
#     demo_resource_id = Column(Integer, ForeignKey('demo_resource.id'))
#     category_id = Column(Integer, ForeignKey('category.id'))
#     access_policies = relationship("AccessPolicy", back_populates="demo_resource_category_link")
#
#
# OR THIS:
#
# class Hierarchy(Base):
#     __tablename__ = 'hierarchy'
#     id = Column(Integer, primary_key=True)
#     parent_id = Column(Integer)
#     child_id = Column(Integer)
#     type = Column(String)

# class AccessPolicy(Base):
#     __tablename__ = 'access_policy'
#     id = Column(Integer, primary_key=True)
#     user_id = Column(Integer, ForeignKey('user.id'))
#     hierarchy_id = Column(Integer, ForeignKey('hierarchy.id'))
#     hierarchy = relationship("Hierarchy")

# class Category(Base):
#     __tablename__ = 'category'
#     id = Column(Integer, primary_key=True)
#     hierarchies = relationship(
#         "Hierarchy",
#         primaryjoin="and_(Hierarchy.parent_id==Category.id, Hierarchy.type=='demo_resource-category')",
#         backref='category_parent'
#     )
#     demo_resources = relationship(
#         "DemoResource",
#         secondary="hierarchy",
#         primaryjoin="and_(Hierarchy.parent_id==Category.id, Hierarchy.type=='demo_resource-category')",
#         secondaryjoin="Hierarchy.child_id==DemoResource.id",
#         backref='categories'
#     )

# class DemoResource(Base):
#     __tablename__ = 'demo_resource'
#     id = Column(Integer, primary_key=True)
#     hierarchies = relationship(
#         "Hierarchy",
#         primaryjoin="and_(Hierarchy.child_id==DemoResource.id, Hierarchy.type=='demo_resource-category')",
#         backref='demo_resource_child'
#     )
