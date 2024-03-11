import logging


from core.types import CurrentUserData, Action
from fastapi import HTTPException


# if TYPE_CHECKING:
#     from core.types import CurrentUserData, Action


logger = logging.getLogger(__name__)


class AccessControl:
    """Class for access control"""

    def __init__(self) -> None:
        pass

    async def __check_resource_inheritance(self):
        """Checks if the resource inherits permissions from a parent resource"""
        # TBD: check the inheritance flag in the resource hierarchy table and stop, if not inherited!
        pass

    async def __check_identity_inheritance(self):
        """Checks if the resource inherits permissions from a parent resource"""
        # TBD: check if the identity inherits permissions from a parent identity (aka group)
        pass

    async def allows(
        self,
        user: "CurrentUserData",
        resource_id: int,
        # resource_type: ResourceType,# TBD: add resource type - needs to come from the CRUD, that inherits from BaseCRUD
        action: "Action",
    ) -> bool:
        """Checks if the user has permission to perform the action on the resource"""
        # TBD: move the logging to the BaseCrud? Or keep it here together with the Access Control?
        # loggingCRUD = AccessLoggingCRUD()
        # TBD: get all policies for the resource, where any of the hierarchical identities and hierarchical resources match
        # Admin override:
        print("=== core.access - AccessControl - user ===")
        print(user)
        # print("=== core.access - AccessControl - user.roles ===")
        # print(user.roles)
        print("=== core.access - AccessControl - user['roles'] ===")
        print(user["roles"])
        # Admin override:
        if user["roles"] and "Admin" in user["roles"]:
            # TBD: this is not the correct place for the logging: resource type is not known here.
            # access_log = AccessLogCreate(
            #     identity_id=user.user_id,
            #     identity_type="Admin",
            #     resource_id=resource_id,
            #     resource_type="protected_resource",
            #     action=action,
            #     time=datetime.now(),
            #     status_code=200,  # TBD: could be 201 if a new resource is created
            # )
            # await loggingCRUD.log_access(access_log)
            return True

        # policyCRUD = AccessPolicyCRUD()

        # pass

        # policy = await policyCRUD.read(
        #     resource_id=resource_id, action=action, identity_id=user.user_id
        # )
        # print("=== core.access - AccessControl - policy ===")
        # print(policy)

        # TBD: implement the comparison of policies and request.
        if 1 == 1:
            return True
        else:
            raise HTTPException(status_code=403, detail="Access denied")

    # async def adds_grant(
    #     identity: "CurrentUserData", resource_id: UUID, action: "Action"
    # ) -> bool:
    #     """Grants a new permission to for a resource"""
    #     # TBD: this could go directly to the CRUD - just make sure it's also protected, as the accessCRUD is not using the BaseCrud (yet)!
    #     pass

    # async def removes_grant(
    #     identity: "CurrentUserData", resource_id: UUID, action: "Action"
    # ) -> bool:
    #     """Removes a permission for a resource"""
    #     # TBD: this could go directly to the CRUD - just make sure it's also protected, as the accessCRUD is not using the BaseCrud (yet)!
    #     pass


# class AccessLogging:
#     """Class for access logging"""

#     def __init__(self) -> None:
#         pass
