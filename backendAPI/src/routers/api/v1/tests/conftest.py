import pytest
from models.category import Category
from models.demo_resource import DemoResource
from models.tag import Tag
from sqlmodel.ext.asyncio.session import AsyncSession
from utils import (
    categories_test_inputs,
    demo_resource_test_inputs,
    demo_resource_test_inputs_with_category,
    tag_test_inputs,
)


@pytest.fixture(scope="function")
async def add_test_demo_resources(get_async_test_session: AsyncSession):
    """Adds a demo resource to the database."""
    session = get_async_test_session

    demo_resource_instances = []
    for resource in demo_resource_test_inputs:
        demo_resource_instance = DemoResource(**resource)
        session.add(demo_resource_instance)
        await session.commit()
        await session.refresh(demo_resource_instance)
        demo_resource_instances.append(demo_resource_instance)

    yield demo_resource_instances


@pytest.fixture(scope="function")
async def add_test_categories(get_async_test_session: AsyncSession):
    """Adds a category to the database."""
    session = get_async_test_session
    category_instances = []
    for category in categories_test_inputs:
        category_instance = Category(**category)
        session.add(category_instance)
        await session.commit()
        await session.refresh(category_instance)
        category_instances.append(category_instance)

    yield category_instances


@pytest.fixture(scope="function")
async def add_test_demo_resources_with_category(
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
        #     category = await session.get(Category, resource["category_id"])
        #     resource["category"] = category
        #     del resource["category_id"]
        demo_resource_instance = DemoResource(**resource)
        session.add(demo_resource_instance)
        await session.commit()
        await session.refresh(demo_resource_instance)
        demo_resource_instances.append(demo_resource_instance)

    yield demo_resource_instances


@pytest.fixture(scope="function")
async def add_test_tags(get_async_test_session: AsyncSession):
    """Adds a tags to the database."""
    session = get_async_test_session
    tag_instances = []
    for tag in tag_test_inputs:
        tag_instance = Tag(**tag)
        session.add(tag_instance)
        await session.commit()
        await session.refresh(tag_instance)
        tag_instances.append(tag_instance)

    yield tag_instances
