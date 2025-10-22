"""
Orchestrator
- Looks up route(s) for (event, resource_type)
- Emits lightweight dispatch records (IDs only) to service domains

"""

import logging
from dataclasses import dataclass, field
from enum import Enum
from core.types import CurrentUserData
from typing import Any, Dict, List, Mapping, Optional, Tuple

logger = logging.getLogger(__name__)


# TBD: consider removing?
class Event(str, Enum):
    AFTER_CREATE = "after_create"
    AFTER_UPDATE = "after_update"
    AFTER_DELETE = "after_delete"


@dataclass(frozen=True)
class EventContext:
    event: Event
    identity_type: str
    object_id: str
    current_user: CurrentUserData



@dataclass(frozen=True)
class Route:
    """A declarative route describing what dispatchers to trigger."""

    service: str  # e.g., "ai", "compiler", "housekeeping"
    version: str = "1"  # bump when behavior changes materially
    params: Dict[str, Any] = field(default_factory=dict)


class Orchestrator:
    """Links created/updated/deleted resources to service actions."""

    def __init__(
        self,
    ) -> None:
        self._routes: Dict[Tuple[str, str], List[Route]] = {
            Mapping(
                (Event.AFTER_CREATE.value, "TextDocument"),
                [
                    Route(
                        service="ai",
                        action="vectorize",
                        part_key="content",
                        version="1",
                    ),
                ],
            ),
            Mapping(
                (Event.AFTER_UPDATE.value, "PdfDocument"),
                [
                    Route(
                        service="ai",
                        action="vectorize",
                        part_key="pages[*]",
                        version="1",
                        params={"preprocessor": "ocr"},
                    ),
                ],
            ),
            Mapping(
                (Event.AFTER_UPDATE.value, "CodeSnippet"),
                [
                    Route(
                        service="compiler",
                        action="compile",
                        part_key="source",
                        version="1",
                    ),
                ],
            ),
        }

    def dispatch(self, event: Event | str, resource_type: str) -> List[Route]:
        # Simple exact match. Add wildcard logic later if needed.
        return list(self._routes.get((str(event), resource_type), []))

    # entry point for CRUD: call this method after database interactions and before returning
    def handle(self, event_context: EventContext) -> None:
        """Handle an event by looking up and emitting planned dispatches."""
        try:
            routes = self.dispatch(event_context.event, event_context.resource_type)
            if not routes:
                logger.debug(
                    f"orchestrator: no routes for event={event_context.event} resource_type={event_context.resource_type}"
                )
                return

            for route in routes:
                # last chance to check user rights / ai_enabled, and so on.
                # after dispatchers it's user independent,
                # so that dispatchers can turn into independent packages / modules / jobs.
                print("== Orchestrator dispatch - event context ===")
                print(event_context)
                print("== Orchestrator dispatch - planned route ===")
                print(route)

                # Placeholder for future: call a dispatcher, e.g.:
                # self._dispatchers[r.service].dispatch(r, ctx)

        except Exception as exception:
            # Don't break the main flow; just log the error.
            logger.error(f"orchestrator: error while handling event: {exception}")
