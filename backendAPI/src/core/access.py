import logging

from uuid import UUID

from core.types import CurrentUserData, Action


# if TYPE_CHECKING:
#     from core.types import CurrentUserData, Action


logger = logging.getLogger(__name__)


class AccessControl:
    """Class for access control"""

    def __init__(self) -> None:
        pass

    async def allows(
        self,
        user: "CurrentUserData",
        resource_id: int,
        # resource_type: ResourceType,# TBD: add resource type - needs to come from the CRUD, that inherits from BaseCRUD
        action: "Action",
    ) -> bool:
        """Checks if the user has permission to perform the action on the resource"""
        # loggingCRUD = AccessLogging()
        # TBD: get all policies for the resource, where any of the hierarchical identities and hierarchical resources match
        # Admin override:
        # print("=== core.access - AccessControl - user ===")
        # print(user)
        # print("=== core.access - AccessControl - user.roles ===")
        # print(user.roles)
        # print("=== core.access - AccessControl - user['roles'] ===")
        # print(user["roles"])
        # if user.roles and "Admin" in user.roles:
        # TBD: this is not the correct place for the logging: resource type is not known here.
        # access_log = AccessLog(
        #     identity_id=user.azure_user_id,  # TBD: change to user_id
        #     identity_type="admin",
        #     resource_id=resource_id,
        #     resource_type="protected_resource",
        #     action=action,
        #     time=datetime.now(),
        #     status_code=200,  # TBD: could be 201 if a new resource is created
        # )
        # await loggingCRUD.log_access(access_log)
        # return True

        # policyCRUD = AccessPolicyCRUD()
        pass
        # policy = await policyCRUD.read(
        #     resource_id=resource_id, action=action, identity_id=user.azure_user_id
        # )
        # print("=== core.access - AccessControl - policy ===")
        # print(policy)

        # # TBD: implement the comparison of policies and request.
        # if 1 == 1:
        #     return True
        # else:
        #     raise HTTPException(status_code=403, detail="Access denied")

    async def adds_grant(
        identity: "CurrentUserData", resource_id: UUID, action: "Action"
    ) -> bool:
        """Grants a new permission to for a resource"""
        pass

    async def removes_grant(
        identity: "CurrentUserData", resource_id: UUID, action: "Action"
    ) -> bool:
        """Removes a permission for a resource"""
        pass


# class AccessLogging:
#     """Class for access logging"""

#     def __init__(self) -> None:
#         pass