from typing import Annotated, Optional

from pydantic import FiniteFloat, StringConstraints
from pydantic_extra_types.language_code import LanguageAlpha2

from core.types import ResourceType
from models.base import Attribute, Relationship, RelationshipHierarchyType, create_model

Category = Annotated[str, StringConstraints(pattern=r"^[a-z0-9-]+$")]


def _relationships():
    return [
        Relationship(
            name="presentations",
            related_entity=ResourceType.presentation,
            hierarchy_type=RelationshipHierarchyType.child,
            back_populates="texts",
        ),
        Relationship(
            name="text_parents",
            related_entity=ResourceType.text,
            hierarchy_type=RelationshipHierarchyType.child,
            back_populates="texts",
        ),
        Relationship(
            name="number_parents",
            related_entity=ResourceType.number,
            hierarchy_type=RelationshipHierarchyType.child,
            back_populates="texts",
        ),
        Relationship(
            name="texts",
            related_entity=ResourceType.text,
            hierarchy_type=RelationshipHierarchyType.parent,
            back_populates="text_parents",
        ),
        Relationship(
            name="numbers",
            related_entity=ResourceType.number,
            hierarchy_type=RelationshipHierarchyType.parent,
            back_populates="text_parents",
        ),
    ]


Text = create_model(
    name="Text",
    attributes=[
        Attribute(name="content", type=str),
        Attribute(name="category", type=Optional[Category]),
        Attribute(name="language", type=Optional[LanguageAlpha2]),
        Attribute(name="confidential", type=Optional[str], encrypt=True),
    ],
    relationships=_relationships(),
)

number_relationships = _relationships()
for relationship in number_relationships:
    if relationship.hierarchy_type == RelationshipHierarchyType.child:
        relationship.back_populates = "numbers"
    else:
        relationship.back_populates = "number_parents"

Number = create_model(
    name="Number",
    attributes=[
        Attribute(name="value", type=FiniteFloat),
        Attribute(name="category", type=Optional[Category]),
    ],
    relationships=number_relationships,
)


class TextCreate(Text.Create):
    model_config = Text.Create.model_config.copy()
    model_config["extra"] = "forbid"


class TextUpdate(Text.Update):
    model_config = Text.Update.model_config.copy()
    model_config["extra"] = "forbid"


class NumberCreate(Number.Create):
    model_config = Number.Create.model_config.copy()
    model_config["extra"] = "forbid"


class NumberUpdate(Number.Update):
    model_config = Number.Update.model_config.copy()
    model_config["extra"] = "forbid"


Text.Create, Text.Update = TextCreate, TextUpdate
Number.Create, Number.Update = NumberCreate, NumberUpdate
TextRead, TextExtended = Text.Read, Text.Extended
NumberRead, NumberExtended = Number.Read, Number.Extended
