import logging
from contextlib import asynccontextmanager
from functools import wraps
from inspect import signature

from sqlalchemy import text
from sqlalchemy.exc import DBAPIError
from fastapi import HTTPException

logger = logging.getLogger(__name__)

# Stable keys shared by every process, ordered resource before identity.
HIERARCHY_LOCKS = {"ResourceHierarchy": 70101, "IdentityHierarchy": 70102}


async def finish_write(session):
    """Nested writes flush; the hierarchy operation owns the commit."""
    if session.info.get("hierarchy_locks"):
        await session.flush()
    else:
        await session.commit()


@asynccontextmanager
async def hierarchy_transaction(session, *hierarchies):
    held = session.info.setdefault("hierarchy_locks", set())
    outermost = not held
    try:
        await session.exec(text("SET LOCAL lock_timeout = '5s'"))
        await session.exec(text("SET LOCAL statement_timeout = '30s'"))
        await session.exec(
            text("SET LOCAL idle_in_transaction_session_timeout = '30s'")
        )
        for key in sorted(HIERARCHY_LOCKS[model.__name__] for model in hierarchies):
            if key not in held:
                if held and key < max(held):
                    raise RuntimeError(
                        "Hierarchy locks must be acquired in global order."
                    )
                await session.exec(
                    text("SELECT pg_advisory_xact_lock(:key)").bindparams(key=key)
                )
                held.add(key)
        yield
        if outermost:
            await session.commit()
    except BaseException as error:
        await session.rollback()
        logger.exception("Hierarchy transaction failed.")
        if isinstance(error, DBAPIError) and getattr(error.orig, "sqlstate", None) in (
            "55P03",
            "57014",
        ):
            raise HTTPException(
                status_code=503, detail="Hierarchy operation timed out."
            ) from error
        raise
    finally:
        if outermost:
            session.info.pop("hierarchy_locks", None)


def hierarchy_write(function):
    """Give shared hierarchy writers one atomic, serialized transaction."""
    parameters = signature(function)

    @wraps(function)
    async def wrapped(self, *args, **kwargs):
        try:
            bound = parameters.bind(self, *args, **kwargs)
        except TypeError as error:
            raise TypeError(f"{function.__qualname__}() {error}") from error
        bound.apply_defaults()
        if function.__name__ == "create" and hasattr(self, "allow_standalone"):
            if bound.arguments.get("parent_id") is None:
                return await function(self, *args, **kwargs)
        async with hierarchy_transaction(self.session, self.hierarchy):
            return await function(self, *args, **kwargs)

    return wrapped
