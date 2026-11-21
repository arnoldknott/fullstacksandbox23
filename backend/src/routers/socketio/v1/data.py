from core.security import AllowAnonymous, Guards, LinkedInGuard, MicrosoftGuard
from core.types import EventGuard
from crud.data import NumberCRUD, TextCRUD
from models.data import Number, Text
from routers.socketio.v1.base import BaseNamespace


def _guards():
    public = Guards(
        MicrosoftGuard(scopes=["socketio", "api.write"], roles=["User"]),
        LinkedInGuard(),
        AllowAnonymous(),
    )
    owner = Guards(
        MicrosoftGuard(scopes=["socketio", "api.write"], roles=["User"]),
        LinkedInGuard(),
    )
    return [
        EventGuard(
            event="connect",
            guards=Guards(MicrosoftGuard(), LinkedInGuard(), AllowAnonymous())(),
        ),
        EventGuard(event="submit:create", guards=public()),
        EventGuard(event="submit:update", guards=public()),
        EventGuard(event="delete", guards=owner()),
        EventGuard(event="share", guards=owner()),
    ]


class TextNamespace(BaseNamespace):
    def __init__(self, *args, **kwargs):
        super().__init__(
            namespace="/text",
            event_guards=_guards(),
            crud=TextCRUD,
            create_model=Text.Create,
            read_model=Text.Read,
            read_extended_model=Text.Extended,
            update_model=Text.Update,
            *args,
            **kwargs,
        )


class NumberNamespace(BaseNamespace):
    def __init__(self, *args, **kwargs):
        super().__init__(
            namespace="/number",
            event_guards=_guards(),
            crud=NumberCRUD,
            create_model=Number.Create,
            read_model=Number.Read,
            read_extended_model=Number.Extended,
            update_model=Number.Update,
            *args,
            **kwargs,
        )
