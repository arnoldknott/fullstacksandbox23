from typing import Literal, Optional

from pydantic import FiniteFloat
from pydantic_extra_types.language_code import LanguageAlpha2

from core.types import KebabCase, ResourceType
from models.base import Attribute, Relationship, RelationshipHierarchyType, create_model


def _relationships(resource: Literal["text", "number"]):
    return [
        Relationship(
            name="presentations",
            related_entity=ResourceType.presentation,
            hierarchy_type=RelationshipHierarchyType.child,
            back_populates=f"{resource}s",
        ),
        Relationship(
            name="text_parents",
            related_entity=ResourceType.text,
            hierarchy_type=RelationshipHierarchyType.child,
            back_populates=f"{resource}s",
        ),
        Relationship(
            name="number_parents",
            related_entity=ResourceType.number,
            hierarchy_type=RelationshipHierarchyType.child,
            back_populates=f"{resource}s",
        ),
        Relationship(
            name="texts",
            related_entity=ResourceType.text,
            hierarchy_type=RelationshipHierarchyType.parent,
            back_populates=f"{resource}_parents",
        ),
        Relationship(
            name="numbers",
            related_entity=ResourceType.number,
            hierarchy_type=RelationshipHierarchyType.parent,
            back_populates=f"{resource}_parents",
        ),
    ]


Text = create_model(
    name="Text",
    attributes=[
        Attribute(name="content", type=str),
        Attribute(name="category", type=Optional[KebabCase]),
        Attribute(name="language", type=Optional[LanguageAlpha2]),
        Attribute(name="confidential", type=Optional[str], encrypt=True),
    ],
    relationships=_relationships("text"),
)

Number = create_model(
    name="Number",
    attributes=[
        Attribute(name="value", type=FiniteFloat),
        Attribute(name="category", type=Optional[KebabCase]),
    ],
    relationships=_relationships("number"),
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
