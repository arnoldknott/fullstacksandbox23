from os import path, remove

import pytest
from fastapi import FastAPI
from httpx import AsyncClient

from models.demo_file import DemoFile
from tests.utils import (
    token_admin_read,
    token_admin_read_write,
    token_user1_read,
    token_user1_read_write,
)


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

    demo_files = [
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
    response = await async_client.post("/api/v1/demo/files/", files=demo_files)

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

    demo_files = [
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
    response = await async_client.post("/api/v1/demo/files/", files=demo_files)

    assert response.status_code == 403
    assert response.json() == {"detail": "DemoFile - Forbidden."}
    # the first file is still written to disk:
    assert path.exists(f"{appdata_path}/{demo_file_name}")

    # Remove demo file from disk after the test:
    remove(f"{appdata_path}/{demo_file_name}")


@pytest.mark.anyio
@pytest.mark.parametrize(
    "mocked_get_azure_token_payload",
    [
        token_admin_read,
        token_admin_read_write,
        token_user1_read,
        token_user1_read_write,
    ],
    indirect=True,
)
async def test_get_demo_file(
    async_client: AsyncClient,
    add_many_test_demo_files: list[DemoFile],
    app_override_get_azure_payload_dependency: FastAPI,
    mocked_get_azure_token_payload,
):
    """Tests GET a demo file."""
    app_override_get_azure_payload_dependency
    files_metadata = await add_many_test_demo_files(mocked_get_azure_token_payload)
    response = await async_client.get(f"/api/v1/demo/file/{files_metadata[1].id}")

    assert response.status_code == 200

    # Check for Content-Disposition header
    assert (
        response.headers["Content-Disposition"]
        == f'attachment; filename="{files_metadata[1].name}"'
    )

    # Read the test file content
    with open(f"src/tests/{files_metadata[1].name}", "rb") as test_file:
        test_file_content = test_file.read()

    assert response.content == test_file_content


@pytest.mark.anyio
@pytest.mark.parametrize(
    "mocked_get_azure_token_payload",
    [
        token_admin_read_write,
        token_user1_read_write,
    ],
    indirect=True,
)
async def test_put_demo_file(
    async_client: AsyncClient,
    add_many_test_demo_files: list[DemoFile],
    app_override_get_azure_payload_dependency: FastAPI,
    mocked_get_azure_token_payload,
):
    """Test PUT a demo file."""
    app_override_get_azure_payload_dependency
    files_metadata = await add_many_test_demo_files(mocked_get_azure_token_payload)
    with open(f"src/tests/{files_metadata[1].name}", "rb") as old_file:
        with open(
            f"/data/appdata/demo_files/{files_metadata[1].name}", "rb"
        ) as app_data_file:
            assert old_file.read() == app_data_file.read()

    # Replacing the content of the second demo_file with the content of the first demo_file
    new_demo_file = [
        (
            "files",
            (
                files_metadata[1].name,
                open(f"src/tests/{str(files_metadata[1].name)}", "rb"),
                "text/plain",
            ),
        )
    ]
    update_response = await async_client.put(
        f"/api/v1/demo/file/{str(files_metadata[1].id)}", files=new_demo_file
    )
    # with open(f"src/tests/{files_metadata[0].name}", "rb") as new_file:
    #     update_response = await async_client.put(
    #         f"/api/v1/demo/file/{files_metadata[1].id}",
    #         files=("files", (files_metadata[1].name, new_file, "text/plain")),
    #     )

    assert update_response.status_code == 200
    demo_file_metadata = DemoFile(**update_response.json())
    assert demo_file_metadata.id == files_metadata[1].id
    assert demo_file_metadata.name == files_metadata[1].name

    get_response = await async_client.get(f"/api/v1/demo/file/{files_metadata[1].id}")
    assert get_response.status_code == 200

    # Read the updated demo_file content
    with open(f"src/tests/{files_metadata[0].name}", "rb") as test_file:
        assert get_response.content == test_file.read()
