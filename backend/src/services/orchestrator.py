"""
Orchestrator
- Looks up route(s) for (event, resource_type)
- Emits lightweight dispatch records (IDs only) to service domains

"""

import logging
from dataclasses import dataclass, field
from enum import Enum
from core.types import CurrentUserData, EntityType
from typing import Any, Mapping, Dict, List, Optional, Callable, Tuple

logger = logging.getLogger(__name__)


# TBD: consider moving to core.types?
class Event(str, Enum):
    AFTER_CREATE = "after_create"
    AFTER_UPDATE = "after_update"
    AFTER_DELETE = "after_delete"


@dataclass(frozen=True)
class Route:
    """A declarative route describing what dispatchers to trigger."""

    service: str  # e.g., "ai", "compiler", "housekeeping"
    # TBD: rename "action" into "pipeline_step" or "handler"?
    action: Optional[Callable] = (
        None  # e.g., "vectorize", "compile", optional if handler provided
    )
    # TBD: how to seperate different versions of the actions?
    # Maybe just put them into the name of the action?
    version: str = "1"  # bump when behavior changes materially
    params: Dict[str, Any] = field(default_factory=dict)


# TBD: import those from other services and
# make sure they are the linking the right Celery flow.
# TBD: basically these are the entry points for a pipeline
def vectorize(parameter1: str, parameter2: int) -> None:
    """Placeholder function for vectorization logic."""
    print(f"Vectorizing with {parameter1} and {parameter2}")


# TBD: one for each language?
def compile_code(code: str, language: str) -> None:
    """Placeholder function for code compilation logic."""
    print(f"Compiling {language} code: {code}")


# TBD: replace the strings with EntityType enums
event_route_map: Mapping[Tuple[Event, EntityType], List[Route]] = {
    (Event.AFTER_CREATE, EntityType.TEXT_DOCUMENT): [
        Route(service="ai", action=vectorize, version="1"),
    ],
    (Event.AFTER_UPDATE, EntityType.PDF_DOCUMENT): [
        Route(
            service="ai", action=vectorize, version="1", params={"preprocessor": "ocr"}
        ),
    ],
    (Event.AFTER_UPDATE, EntityType.CODE_SNIPPET): [
        Route(service="compiler", action=compile_code, version="1"),
    ],
}


class Orchestrator:
    """Links created/updated/deleted resources to service actions."""

    def __init__(
        self,
    ) -> None:
        # TBD: move mappings of events and routes to top of file
        # TBD: Decide where to extract the part of the resource, that needs processing
        self._event_route_map = event_route_map

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
            routes = list(self._event_route_map.get((event, entity_type), []))
            if not routes:
                logger.info(
                    f"orchestrator: no routes for event={event} resource_type={entity_type}"
                )
                return

            for route in routes:
                # check inside relevant dispatchers
                # for ai_enabled, linked accounts, and so on.
                print("== Orchestrator dispatch - event  ===")
                print(event)
                print("== Orchestrator dispatch - entity type ===")
                print(entity_type)
                print("== Orchestrator dispatch - object id ===")
                print(object_id)
                if current_user:
                    print("== Orchestrator dispatch - current user ===")
                    print(current_user)
                print("== Orchestrator dispatch - planned route ===")
                print(route)
                # TBD: consider using partial from functools:
                # from functools import partial
                # Route(service="ai", action=partial(vectorize, preprocessor="ocr"))
                # Then here, only the real arguments need to be passed:
                # route.action(entity_type, object_id, current_user)
                # Or for now just like this:
                # if route.action is not None:
                #     route.action(entity_type, object_id, current_user, **route.params)

                # Placeholder for future: call a dispatcher, e.g.:
                # self._dispatchers[r.service].dispatch(r, ctx)

        except Exception as exception:
            # Don't break the main flow; just log the error.
            logger.error(f"orchestrator: error while handling event: {exception}")
