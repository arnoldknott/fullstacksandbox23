import logging

from .base import BaseNamespace

logger = logging.getLogger(__name__)


class InteractiveDocumentation(BaseNamespace):
    def __init__(self):
        super().__init__(namespace="/interactive-documentation")
