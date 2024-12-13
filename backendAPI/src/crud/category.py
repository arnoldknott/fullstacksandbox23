from models.category import Category, CategoryCreate, CategoryRead, CategoryUpdate

from .base import BaseCRUD


class CategoryCRUD(BaseCRUD[Category, CategoryCreate, CategoryRead, CategoryUpdate]):
    def __init__(self):
        super().__init__(Category, allow_everyone=["create"])

    # Moved to DemoResourceCRUD
    # # TBD: add access control and access logging for this - use self.read()!
    # # Move to DemoResourceCRUD?
    # async def read_all_demo_resources(
    #     self,
    #     # current_user: CurrentUserData,
    #     category_id: UUID,
    # ) -> List[DemoResource]:
    #     """Returns all demo resources within category."""

    #     # print("=== category_id ===")
    #     # print(category_id)

    #     # Generic read method is not that generic after all? Note the return type is not a list of CategoryRead with select_args!

    #     # async def read(
    #     #     self,
    #     #     current_user: Optional["CurrentUserData"] = None,
    #     #     select_args: Optional[List] = None,
    #     #     filters: Optional[List] = None,
    #     #     joins: Optional[List] = None,
    #     #     order_by: Optional[List] = None,
    #     #     group_by: Optional[List] = None,
    #     #     having: Optional[List] = None,
    #     #     limit: Optional[int] = None,
    #     #     offset: Optional[int] = None,
    #     # ) -> list[BaseSchemaTypeRead]:

    #     # return await self.read(
    #     #     current_user,
    #     #     select_args=[Category, DemoResource],
    #     #     joins=[DemoResource],
    #     #     filters=[DemoResource.category_id == category_id],
    #     # )

    #     # response = await self.read(
    #     #     current_user,
    #     #     select_args=[DemoResource],
    #     #     joins=[Category],
    #     #     filters=[DemoResource.category_id == category_id],
    #     # )
    #     # print("=== response ===")
    #     # print(response)
    #     # demo_resources = response.demo_resources

    #     # print("=== demo_resources ===")
    #     # print(demo_resources)

    #     session = self.session
    #     statement = select(DemoResource).where(DemoResource.category_id == category_id)
    #     response = await session.exec(statement)
    #     demo_resources = response.all()

    #     if not demo_resources:
    #         raise HTTPException(status_code=404, detail="No demo resources found")
    #     return demo_resources
