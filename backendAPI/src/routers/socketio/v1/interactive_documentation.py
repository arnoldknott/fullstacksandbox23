import logging

from .base import BaseNamespace

logger = logging.getLogger(__name__)


class InteractiveDocumentation(BaseNamespace):
    def __init__(self):
        super().__init__(
            namespace="/interactive-documentation",
            callback_on_connect=self.initial_data_transfer,
        )
        self.average = {
            "Repository": 0.0,
            "Infrastructure": 0.0,
            "Architecture": 0.0,
            "Security": 0.0,
            "Backend": 0.0,
            "Frontend": 0.0,
        }
        self.count = {
            "Repository": 0,
            "Infrastructure": 0,
            "Architecture": 0,
            "Security": 0,
            "Backend": 0,
            "Frontend": 0,
        }
        self.comments = []

    # async def on_connect(self, sid, environ, auth=None):
    #     """Executes on connect for the interactive documentation namespace."""
    #     print("=== interactive_documentation - on_connect ===")
    #     print(sid, flush=True)
    #     # return await super().on_connect(sid, environ, auth)

    async def initial_data_transfer(self, sid):
        """Executes transferring the initial data on connect."""
        for topic in self.average:
            await self.server.emit(
                "averages",
                {
                    "topic": topic,
                    "average": self.average[topic],
                    "count": self.count[topic],
                },
                to=sid,
                namespace=self.namespace,
            )
        for comment in self.comments:
            await self.server.emit(
                "server_comments",
                {"topic": comment["topic"], "comment": comment["comment"]},
                to=sid,
                namespace=self.namespace,
            )
        return "initial_data_transfer"

    async def on_comments(self, sid, data):
        """Presentation interests for socket.io."""
        logger.info(f"Received comment in interactive documentation from client {sid}.")

        self.comments.append({"topic": data["topic"], "comment": data["comment"]})
        await self.emit(
            "server_comments", {"topic": data["topic"], "comment": data["comment"]}
        )

        old_average = self.average[data["topic"]]
        old_count = self.count[data["topic"]]

        new_average = (old_average * old_count + data["value"]) / (old_count + 1)
        self.count[data["topic"]] += 1
        new_count = self.count[data["topic"]]
        self.average[data["topic"]] = new_average

        await self.emit(
            "averages",
            {"topic": data["topic"], "average": new_average, "count": new_count},
        )


interactive_documentation_router = InteractiveDocumentation()
