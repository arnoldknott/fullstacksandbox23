from os import path, remove
from uuid import uuid4

import pytest
from fastapi import FastAPI
from httpx import AsyncClient

from models.demo_file import DemoFile
from models.demo_resource import DemoResource
from tests.utils import (
    token_admin_read,
    token_admin_read_write,
    token_user1_read,
    token_user1_read_write,
    token_user2_read_write,
)


@pytest.mark.anyio
@pytest.mark.parametrize(
    "mocked_provide_http_token_payload",
    [token_admin_read_write, token_user1_read_write],
    indirect=True,
)
async def test_post_demo_files(
    async_client: AsyncClient,
    app_override_provide_http_token_payload: FastAPI,
    mocked_provide_http_token_payload,
    access_to_one_parent,
):
    """Tests the post_user endpoint of the API."""
    app_override_provide_http_token_payload

    demo_file_names = ["demo_file_00.txt", "demo_file_01.txt"]
    appdata_path = "/data/appdata/demo_files"

    parent_id = await access_to_one_parent(DemoResource)

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
    response = await async_client.post(
        f"/api/v1/demo/resource/{str(parent_id)}/files", files=demo_files
    )

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
    "mocked_provide_http_token_payload",
    [token_user1_read_write, token_user2_read_write],
    indirect=True,
)
async def test_post_demo_files_without_access_to_parent(
    async_client: AsyncClient,
    app_override_provide_http_token_payload: FastAPI,
    register_one_resource,
):
    """Tests the post_user endpoint of the API."""
    app_override_provide_http_token_payload

    demo_file_names = ["demo_file_00.txt", "demo_file_01.txt"]
    appdata_path = "/data/appdata/demo_files"

    parent_id = uuid4()
    await register_one_resource(parent_id, DemoResource)

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
    response = await async_client.post(
        f"/api/v1/demo/resource/{str(parent_id)}/files", files=demo_files
    )

    assert response.status_code == 403
    assert response.json() == {"detail": "DemoFile - Forbidden."}


@pytest.mark.anyio
@pytest.mark.parametrize(
    "mocked_provide_http_token_payload",
    [token_admin_read_write, token_user1_read_write, token_user2_read_write],
    indirect=True,
)
async def test_post_demo_files_without_existing_parent(
    async_client: AsyncClient,
    app_override_provide_http_token_payload: FastAPI,
    mocked_provide_http_token_payload,
    register_one_resource,
):
    """Tests the post_user endpoint of the API."""
    app_override_provide_http_token_payload

    demo_file_names = ["demo_file_00.txt", "demo_file_01.txt"]
    appdata_path = "/data/appdata/demo_files"

    parent_id = uuid4()

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
    response = await async_client.post(
        f"/api/v1/demo/resource/{str(parent_id)}/files", files=demo_files
    )

    assert response.status_code == 403
    assert response.json() == {"detail": "DemoFile - Forbidden."}


@pytest.mark.anyio
@pytest.mark.parametrize(
    "mocked_provide_http_token_payload",
    [token_admin_read_write, token_user1_read_write],
    indirect=True,
)
async def test_post_demo_files_uniqueness(
    async_client: AsyncClient,
    app_override_provide_http_token_payload: FastAPI,
    access_to_one_parent,
    mocked_provide_http_token_payload,
):
    """Tests the post_user endpoint of the API."""
    app_override_provide_http_token_payload

    demo_file_name = "demo_file_00.txt"
    appdata_path = "/data/appdata/demo_files"

    # Make sure the demo files do not exist before the test on disk:
    if path.exists(f"{appdata_path}/{demo_file_name}"):
        remove(f"{appdata_path}/{demo_file_name}")

    parent_id = await access_to_one_parent(DemoResource)

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
    response = await async_client.post(
        f"/api/v1/demo/resource/{str(parent_id)}/files", files=demo_files
    )

    assert response.status_code == 403
    assert response.json() == {"detail": "DemoFile - Forbidden."}
    # the first file is still written to disk:
    assert path.exists(f"{appdata_path}/{demo_file_name}")

    # Remove demo file from disk after the test:
    remove(f"{appdata_path}/{demo_file_name}")


@pytest.mark.anyio
@pytest.mark.parametrize(
    "mocked_provide_http_token_payload",
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
    app_override_provide_http_token_payload: FastAPI,
    mocked_provide_http_token_payload,
):
    """Tests GET a demo file."""
    app_override_provide_http_token_payload
    files_metadata = await add_many_test_demo_files(mocked_provide_http_token_payload)
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
        # from get response:
        assert response.content == test_file_content
        # on disk:
        with open(
            f"/data/appdata/demo_files/{files_metadata[1].name}", "rb"
        ) as app_data_file:
            app_data_file_content = app_data_file.read()
            assert test_file_content == app_data_file_content


@pytest.mark.anyio
@pytest.mark.parametrize(
    "mocked_provide_http_token_payload",
    [
        token_admin_read_write,
        token_user1_read_write,
    ],
    indirect=True,
)
async def test_put_demo_file(
    async_client: AsyncClient,
    add_many_test_demo_files: list[DemoFile],
    app_override_provide_http_token_payload: FastAPI,
    mocked_provide_http_token_payload,
):
    """Test PUT a demo file."""
    app_override_provide_http_token_payload
    files_metadata = await add_many_test_demo_files(mocked_provide_http_token_payload)
    with open(f"src/tests/{files_metadata[0].name}", "rb") as old_file:
        with open(
            f"/data/appdata/demo_files/{files_metadata[0].name}", "rb"
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
    # note: the content of demo_file[1] is written in the place of demo_file[0] keeping the id from demo_file[0]:
    update_response = await async_client.put(
        f"/api/v1/demo/file/{str(files_metadata[0].id)}", files=new_demo_file
    )
    # with open(f"src/tests/{files_metadata[0].name}", "rb") as new_file:
    #     update_response = await async_client.put(
    #         f"/api/v1/demo/file/{files_metadata[1].id}",
    #         files=("files", (files_metadata[1].name, new_file, "text/plain")),
    #     )

    assert update_response.status_code == 200
    demo_file_metadata = DemoFile(**update_response.json())
    assert demo_file_metadata.id == str(files_metadata[0].id)
    assert demo_file_metadata.name == files_metadata[0].name

    get_response = await async_client.get(f"/api/v1/demo/file/{files_metadata[0].id}")
    assert get_response.status_code == 200

    # Read the updated demo_file content:
    with open(f"src/tests/{files_metadata[1].name}", "rb") as new_file:
        new_file_content = new_file.read()
        # from get response:
        assert get_response.content == new_file_content
        # on disk:
        with open(
            f"/data/appdata/demo_files/{files_metadata[0].name}", "rb"
        ) as app_data_file:
            app_data_file_content = app_data_file.read()
            assert app_data_file_content == new_file_content


@pytest.mark.anyio
@pytest.mark.parametrize(
    "mocked_provide_http_token_payload",
    [
        token_admin_read_write,
        token_user1_read_write,
    ],
    indirect=True,
)
async def test_rename_file(
    async_client: AsyncClient,
    add_many_test_demo_files: list[DemoFile],
    app_override_provide_http_token_payload: FastAPI,
    mocked_provide_http_token_payload,
):
    """Test PUT a demo file."""
    app_override_provide_http_token_payload
    files_metadata = await add_many_test_demo_files(mocked_provide_http_token_payload)
    with open(f"src/tests/{files_metadata[1].name}", "rb") as old_file:
        with open(
            f"/data/appdata/demo_files/{files_metadata[1].name}", "rb"
        ) as app_data_file:
            assert old_file.read() == app_data_file.read()

    new_file_name = "demo_file_new_name.txt"

    # note: the content of demo_file[1] is written in the place of demo_file[0] keeping the id from demo_file[0]:
    update_response = await async_client.put(
        f"/api/v1/demo/file/rename/{str(files_metadata[1].id)}",
        json={"name": new_file_name},
    )

    assert update_response.status_code == 200
    demo_file_metadata = DemoFile(**update_response.json())
    assert demo_file_metadata.id == str(files_metadata[1].id)
    assert demo_file_metadata.name == new_file_name

    get_response = await async_client.get(f"/api/v1/demo/file/{files_metadata[1].id}")
    assert get_response.status_code == 200

    # Read the updated demo_file content
    with open(f"src/tests/{files_metadata[1].name}", "rb") as file:
        file_content = file.read()
        assert get_response.content == file_content
        # on disk:
        with open(f"/data/appdata/demo_files/{new_file_name}", "rb") as app_data_file:
            app_data_file_content = app_data_file.read()
            assert app_data_file_content == file_content

    # Check that the old file is removed from disk:
    assert not path.exists(f"/data/appdata/demo_files/{files_metadata[1].name}")


@pytest.mark.anyio
@pytest.mark.parametrize(
    "mocked_provide_http_token_payload",
    [
        token_admin_read_write,
        token_user1_read_write,
    ],
    indirect=True,
)
async def test_delete_demo_file(
    async_client: AsyncClient,
    add_many_test_demo_files: list[DemoFile],
    app_override_provide_http_token_payload: FastAPI,
    mocked_provide_http_token_payload,
):
    """Test DELETE a demo file."""
    app_override_provide_http_token_payload
    files_metadata = await add_many_test_demo_files(mocked_provide_http_token_payload)
    with open(f"src/tests/{files_metadata[1].name}", "rb") as old_file:
        with open(
            f"/data/appdata/demo_files/{files_metadata[1].name}", "rb"
        ) as app_data_file:
            assert old_file.read() == app_data_file.read()

    # Delete the demo file
    delete_response = await async_client.delete(
        f"/api/v1/demo/file/{str(files_metadata[1].id)}"
    )

    assert delete_response.status_code == 200
    assert delete_response.json() is None

    # Check that the file is removed from disk:
    assert not path.exists(f"/data/appdata/demo_files/{files_metadata[1].name}")

    # Check that the file is removed from the database:
    get_response = await async_client.get(f"/api/v1/demo/file/{files_metadata[1].id}")
    assert get_response.status_code == 404
    assert get_response.json() == {"detail": "DemoFile not found."}

    other_file_get_response = await async_client.get(
        f"/api/v1/demo/file/{files_metadata[0].id}"
    )
    assert other_file_get_response.status_code == 200
    # Read the other test file:
    with open(f"src/tests/{files_metadata[0].name}", "rb") as test_file:
        test_file_content = test_file.read()
        # from get response:
        assert other_file_get_response.content == test_file_content
        # on disk:
        with open(
            f"/data/appdata/demo_files/{files_metadata[0].name}", "rb"
        ) as app_data_file:
            app_data_file_content = app_data_file.read()
            assert test_file_content == app_data_file_content
