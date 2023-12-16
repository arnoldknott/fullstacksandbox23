import pytest
from models.demo_resource import DemoResource
from sqlmodel.ext.asyncio.session import AsyncSession
from utils import demo_resource_test_inputs


@pytest.fixture(scope="function")
async def add_test_demo_resources(get_async_test_session: AsyncSession):
    """Adds a demo resource to the database."""
    session = get_async_test_session

    database_resources = demo_resource_test_inputs
    demo_resource_instances = []
    # print("=== database_resources before database write ===")
    # print(database_resources)
    for resource in database_resources:
        demo_resource_instance = DemoResource(**resource)
        # print("=== demoe_resource_instance ===")
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
