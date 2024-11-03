from models.demo_file import (
    DemoFile,
    DemoFileCreate,
    DemoFileRead,
    DemoFileUpdate,
)

from .base import BaseCRUD


class DemoFileCRUD(
    BaseCRUD[
        DemoFile,
        DemoFileCreate,
        DemoFileRead,
        DemoFileUpdate,
    ]
):
    def __init__(self):
        super().__init__(DemoFile, "demo_files")
