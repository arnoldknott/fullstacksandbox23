from os import path, remove

import pytest
from fastapi import FastAPI
from httpx import AsyncClient

from models.demo_file import DemoFile
from tests.utils import token_admin_read_write, token_user1_read_write


@pytest.mark.anyio
@pytest.mark.parametrize(
    "mocked_get_azure_token_payload",
    [token_admin_read_write, token_user1_read_write],
    indirect=True,
)
async def test_post_demo_files(
    async_client: AsyncClient,
    app_override_get_azure_payload_dependency: FastAPI,
):
    """Tests the post_user endpoint of the API."""
    app_override_get_azure_payload_dependency

    demo_file_names = ["demo_file_01.txt", "demo_file_02.txt"]
    appdata_path = "/data/appdata/demo_files"

    # Make sure the demo files do not exist before the test on disk:
    for demo_file_name in demo_file_names:
        if path.exists(f"{appdata_path}/{demo_file_name}"):
            remove(f"{appdata_path}/{demo_file_name}")

    files = [
        (
            "files",
            (
                demo_file_names[0],
                open(f"src/tests/{demo_file_names[0]}", "rb"),
                "text/plain",
            ),
        ),
        (
            "files",
            (
                demo_file_names[1],
                open(f"src/tests/{demo_file_names[1]}", "rb"),
                "text/plain",
            ),
        ),
    ]

    # Make a POST request to upload the demo file
    response = await async_client.post("/api/v1/demo/files/", files=files)

    assert response.status_code == 201
    created_files_metadata = [DemoFile(**file) for file in response.json()]
    for created_file_metadata in created_files_metadata:
        assert created_file_metadata.name in demo_file_names
        assert path.exists(f"{appdata_path}/{created_file_metadata.name}")
        print(created_file_metadata)

    # Remove demo files from disk after the test:
    for demo_file_name in demo_file_names:
        if path.exists(f"{appdata_path}/{demo_file_name}"):
            remove(f"{appdata_path}/{demo_file_name}")


@pytest.mark.anyio
@pytest.mark.parametrize(
    "mocked_get_azure_token_payload",
    [token_admin_read_write, token_user1_read_write],
    indirect=True,
)
async def test_post_demo_files_uniqueness(
    async_client: AsyncClient,
    app_override_get_azure_payload_dependency: FastAPI,
):
    """Tests the post_user endpoint of the API."""
    app_override_get_azure_payload_dependency

    demo_file_name = "demo_file_01.txt"
    appdata_path = "/data/appdata/demo_files"

    # Make sure the demo files do not exist before the test on disk:
    if path.exists(f"{appdata_path}/{demo_file_name}"):
        remove(f"{appdata_path}/{demo_file_name}")

    files = [
        (
            "files",
            (
                demo_file_name,
                open(f"src/tests/{demo_file_name}", "rb"),
                "text/plain",
            ),
        ),
        (
            "files",
            (
                demo_file_name,
                open(f"src/tests/{demo_file_name}", "rb"),
                "text/plain",
            ),
        ),
    ]

    # Make a POST request to upload the demo file
    response = await async_client.post("/api/v1/demo/files/", files=files)

    assert response.status_code == 403
    assert response.json() == {"detail": "DemoFile - Forbidden."}
    # the first file is still written to disk:
    assert path.exists(f"{appdata_path}/{demo_file_name}")

    # Remove demo file from disk after the test:
    remove(f"{appdata_path}/{demo_file_name}")
