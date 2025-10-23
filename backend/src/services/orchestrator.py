"""
Orchestrator uses the event and resource_type to identify which dispatcher to call.
Mapping of (event, resource_type) to dispatcher functions with hard coded partial arguments like "version".
The content to work with is identified by object_id and resource type.
The called services retrieve the data based on this information as needed.
Optionally passing the current user to check before processing, if current_user allows this kind of processing,
for example:
- if artificial intelligence processing is enabled,
- if user has the required account (Discord, Github, Google, Brightspace) linked or 

"""

import logging
from dataclasses import dataclass, field
from functools import partial
from enum import Enum
from core.types import CurrentUserData, EntityType
from typing import Any, Mapping, Dict, List, Optional, Callable, Tuple

logger = logging.getLogger(__name__)


# TBD: consider moving to core.types?
class Event(str, Enum):
    AFTER_CREATE = "after_create"
    AFTER_UPDATE = "after_update"
    AFTER_DELETE = "after_delete"



# TBD: import those from other services and
# make sure they are the linking the right Celery flow.
def vectorize(
    object_id: str, current_user: Optional[CurrentUserData], version: int
) -> None:
    """Placeholder function for vectorization logic."""
    print(f"=== Vectorizing with {object_id} and {current_user} (version: {version}) ===")


# TBD: one for each language?
def compile_code(
    object_id: str, language: str, current_user: Optional[CurrentUserData], version: int
) -> None:
    """Placeholder function for code compilation logic."""
    print(f"=== Compiling {language} code from object {object_id} (version: {version}) ===")
    print(f"=== Orchestrator - compile code dummy - Current user: {current_user} ===")

def translate(
    object_id: str, target_language: str, version: int
) -> None:
    """Placeholder function for translation texts, for example via deeple or google translate."""
    print(f"=== Translating object {object_id} to {target_language} (version: {version}) ===")

# TBD: replace the strings with EntityType enums
event_dispatcher_map: Mapping[Tuple[Event, EntityType], List[Callable]] = {
    (Event.AFTER_CREATE, EntityType.TEXT_DOCUMENT): [partial(vectorize, version=1)],
    (Event.AFTER_UPDATE, EntityType.PDF_DOCUMENT): [
        partial(vectorize, version=1, preprocessor="ocr")
    ],
    (Event.AFTER_UPDATE, EntityType.CODE_SNIPPET): [
        partial(compile_code, version=1, language="python"),
    ],
}


class Orchestrator:
    """Links created/updated/deleted resources to service actions."""

    def __init__(
        self,
    ) -> None:
        # TBD: Decide where to extract the part of the resource, that needs processing
        self._event_dispatcher_map = event_dispatcher_map

    # entry point for CRUD: call this method after database interactions and before returning
    def handle(
        self,
        event: Event,
        entity_type: EntityType,
        object_id: str,
        current_user: Optional[CurrentUserData] = None,
    ) -> None:
        """Handle an event by looking up and emitting planned dispatches."""
        try:
            dispatchers = list(self._event_dispatcher_map.get((event, entity_type), []))
            if not dispatchers:
                logger.info(
                    f"orchestrator: no dispatchers for event={event} resource_type={entity_type}"
                )
                return

            for dispatcher in dispatchers:
                # check inside relevant dispatchers
                # for ai_enabled, linked accounts, and so on.
                print("=== Orchestrator dispatch - event  ===")
                print(event)
                print("=== Orchestrator dispatch - entity type ===")
                print(entity_type)
                print("=== Orchestrator dispatch - object id ===")
                print(object_id)
                if current_user:
                    print("=== Orchestrator dispatch - current user ===")
                    print(current_user)
                print("=== Orchestrator dispatch - planned dispatcher ===")
                print(dispatcher)

        except Exception as exception:
            # Don't break the main flow; just log the error.
            logger.error(
                f"orchestrator: error while handling event {event} with object_id {object_id}: {exception}"
            )
