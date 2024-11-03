import pytest
from os import path, remove
from fastapi import FastAPI
from httpx import AsyncClient


from models.demo_file import DemoFile
from tests.utils import (
    token_admin_read_write,
    token_user1_read_write,
)


@pytest.mark.anyio
@pytest.mark.parametrize(
    "mocked_get_azure_token_payload",
    [token_admin_read_write, token_user1_read_write],
    indirect=True,
)
async def test_post_protected_resource_with_logs_and_policies(
    async_client: AsyncClient,
    app_override_get_azure_payload_dependency: FastAPI,
    current_test_user,
):
    """Tests the post_user endpoint of the API."""
    app_override_get_azure_payload_dependency

    demo_file_names = ["demo_file_01.txt", "demo_file_02.txt"]
    appdata_path = "/data/appdata/demo_files"

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
    # before_time = datetime.now()
    response = await async_client.post("/api/v1/demo/files/", files=files)
    # after_time = datetime.now()

    assert response.status_code == 201
    created_files_metadata = [DemoFile(**file) for file in response.json()]
    for created_file_metadata in created_files_metadata:
        assert created_file_metadata.name in demo_file_names
        assert path.exists(f"{appdata_path}/{created_file_metadata.name}")
        print(created_file_metadata)

    for demo_file_name in demo_file_names:
        if path.exists(f"{appdata_path}/{demo_file_name}"):
            remove(f"{appdata_path}/{demo_file_name}")
