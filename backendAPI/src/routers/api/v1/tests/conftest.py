import pytest
from httpx import AsyncClient
from models.category import Category
from models.demo_resource import DemoResource
from sqlmodel.ext.asyncio.session import AsyncSession
from utils import (
    demo_categories_test_inputs,
    demo_resource_test_inputs,
    demo_resource_test_inputs_with_category,
)


@pytest.fixture(scope="function")
async def add_test_demo_resources(get_async_test_session: AsyncSession):
    """Adds a demo resource to the database."""
    session = get_async_test_session

    demo_resource_instances = []
    # print("=== database_resources before database write ===")
    # print(database_resources)
    for resource in demo_resource_test_inputs:
        demo_resource_instance = DemoResource(**resource)
        # print("=== demo_resource_instance ===")
        # print(demo_resource_instance)
        session.add(demo_resource_instance)
        await session.commit()
        await session.refresh(demo_resource_instance)
        demo_resource_instances.append(demo_resource_instance)

    # print("=== database_resources after writing to database ===")
    # print(database_resources)
    # print("=== demo_resource_instances after writing to database ===")
    # print(demo_resource_instances)
    yield demo_resource_instances

    # should not be necessary -a s the migrations run after each test function
    # for demo_resource_instance in demo_resource_instances:
    #     await session.delete(demo_resource_instance)
    # await session.commit()
    # await session.close()

    # database_resources = demo_resource_test_inputs
    # for resource in database_resources:
    #     resource = DemoResource(**resource)
    #     session.delete(resource)
    #     await session.commit()


@pytest.fixture(scope="function")
async def add_test_categories(get_async_test_session: AsyncSession):
    """Adds a category to the database."""
    session = get_async_test_session

    # # Delete all Category instances before the test
    # await session.execute(delete(Category))
    # await session.commit()

    category_instances = []
    for category in demo_categories_test_inputs:
        category_instance = Category(**category)
        session.add(category_instance)
        await session.commit()
        await session.refresh(category_instance)
        category_instances.append(category_instance)

    yield category_instances

    # for category_instance in category_instances:
    #     if session.is_active and session.is_modified(category_instance):
    #         await session.delete(category_instance)
    # await session.commit()
    # should not be necessary -a s the migrations run after each test function
    # for category_instance in category_instances:
    #     await session.delete(category_instance)
    # await session.commit()
    # await session.close()


@pytest.fixture(scope="function")
async def add_test_demo_resources_with_category(
    async_client: AsyncClient,
    get_async_test_session: AsyncSession,
    add_test_categories: list[Category],
):
    """Adds a demo resource to the database."""
    print("=== add_test_demo_resources_with_category started ===")
    session = get_async_test_session
    add_test_categories
    print("=== add_test_demo_resources_with_category after add_test_categories ===")

    demo_resource_instances = []
    for resource in demo_resource_test_inputs_with_category:
        print("=== resource ===")
        print(resource)
        # if "category_id" in resource:
        #     # if resource["category_id"]:
        #     category = await session.get(Category, resource["category_id"])
        #     # response = await async_client.get(
        #     #     f"/api/v1/categories/{resource['category_id']}"
        #     # )
        #     # category = Category(**response.json())
        #     resource["category"] = category
        #     del resource["category_id"]
        demo_resource_instance = DemoResource(**resource)
        print("=== demo_resource_instance to be added ===")
        print(session.is_active)
        print(session.is_modified(demo_resource_instance))
        # New instances that have been added to the session but not yet persisted to the database
        print("=== New ===")
        print(session.new)
        # Instances that have been modified but not yet persisted to the database
        print("=== Dirty ===")
        print(session.dirty)
        # Instances that have been marked for deletion but not yet deleted from the database
        print("=== Deleted ===")
        print(session.deleted)
        print("=== demo_resource_instance ===")
        print(demo_resource_instance)
        session.add(demo_resource_instance)
        print("=== before session.commit() ===")
        await session.commit()
        print("=== after session.commit() ===")
        await session.refresh(demo_resource_instance)
        # print("=================================")
        # print("====== NEW DEMO RESOURCE =======")
        # print("=================================")
        # print("=== demo_resource_instance ===")
        # print(demo_resource_instance)
        # print("=== demo_resource_instance.category ===")
        # print(demo_resource_instance.category)
        # print((type(demo_resource_instance.category)))
        # print("=== category ===")
        # print(category)
        # print("=== category.demo_resources ===")
        # print(category.demo_resources)
        # print((type(category.demo_resources)))
        demo_resource_instances.append(demo_resource_instance)

    yield demo_resource_instances
