import logging

from typing import Optional, Union
from core.types import CurrentUserData, Action, ResourceType, IdentityType
from fastapi import HTTPException
from models.access import AccessPolicy

from sqlmodel import or_

# if TYPE_CHECKING:
#     from core.types import CurrentUserData, Action


logger = logging.getLogger(__name__)


class AccessControl:
    """Class for access control"""

    def __init__(self, policy_crud) -> None:
        self.policy_crud = policy_crud

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
        resource_id: int,  # TBD: for identities, this is a UUID!!
        resource_type: Union[ResourceType, IdentityType],
        action: "Action",
        user: Optional["CurrentUserData"] = None,
    ) -> bool:
        """Checks if the user has permission including inheritance to perform the action on the resource"""
        # TBD: move the logging to the BaseCrud? Or keep it here together with the Access Control?
        # loggingCRUD = AccessLoggingCRUD()
        # TBD: get all policies for the resource, where any of the hierarchical identities and hierarchical resources match
        # Don't include the identity in the query, as public resources are not assigned to any identity!
        # TBD: implement "public" override: check if the resource is public for requested action and return True if it is!
        # Admin override:
        # user = CurrentUserData(user)
        # print("=== core.access - AccessControl - user ===")
        # print(user)
        # print("=== core.access - AccessControl - user.roles ===")
        # print(user.roles)
        # print("=== core.access - AccessControl - user['roles'] ===")
        # print(user["roles"])
        # Admin override:
        # if user["roles"] and "Admin" in user["roles"]:

        # check for public override:
        if not user:
            # async with self.policy_crud as policy_crud:
            policy_crud = self.policy_crud
            # add join with inheritance table
            policies = await policy_crud.read(
                resource_id=resource_id, resource_type=resource_type, action=action
            )
            for policy in policies:
                if policy.public:
                    return True
                else:
                    logger.error("Error accessing resource without user information.")
                    raise HTTPException(status_code=403, detail="Access denied")
        # check for admin override:
        elif user.roles and "Admin" in user.roles:
            return True
        # TBD: implement the comparison of policies and request.
        else:
            policy_crud = self.policy_crud
            # async with self.policy_crud as policy_crud:
            # add join with inheritance table for both resource and identity
            policies = await policy_crud.read(
                resource_id=resource_id,
                resource_type=resource_type,
                action=action,
                identity_id=user.user_id,
            )
            if policies is not None:
                return True
            else:
                logger.error("Error accessing resource.")
                raise HTTPException(status_code=403, detail="Access denied")

    def filters_allowed(
        self,
        resource_type: Union[ResourceType, IdentityType],
        action: "Action",
        user: Optional["CurrentUserData"] = None,
    ):
        """Finds all resources of a certain type and action that the user has permission to access"""
        # TBD: implement this
        # ✔︎ find all public resources of the given type and action
        # ✔︎ find all resources of the given type and action that the user has permission to access
        # - find all resources of the given type and action that the user has permission to access through resource inheritance
        # - find all resources of the given type and action that the user has permission to access through group membership (identity inheritance)
        # - find all resources of the given type and action that the user has permission to access through group membership (identity inheritance) and resource inheritance
        # - find all resources of the given type and action that the user has permission to access through group membership (identity inheritance) and resource inheritance and public access
        # - find all resources of the given type and action that the user has permission to access through group membership (identity inheritance) and resource inheritance and public access and admin override

        # Permisssion overrides:
        # own includes write and read
        # write includes read
        if action == Action.read:
            action = ["own", "write", "read"]
        elif action == Action.write:
            action = ["own", "write"]
        elif action == Action.own:
            action = ["own"]

        conditions = []
        if not user:
            conditions.append(AccessPolicy.resource_type == resource_type)
            conditions.append(AccessPolicy.action.in_(action))
            conditions.append(AccessPolicy.public)
        elif "Admin" in user.roles:
            pass
            # conditions.append(AccessPolicy.resource_type == resource_type)
            # conditions.append(AccessPolicy.action.in_(action))
        else:
            conditions.append(AccessPolicy.resource_type == resource_type)
            conditions.append(AccessPolicy.action.in_(action))
            conditions.append(
                or_(AccessPolicy.identity_id == user.user_id, AccessPolicy.public)
            )  # add the self-join from identity inheritance table

        return conditions

        # user_policies = []
        # # Get the IDs of the objects that the user has access to
        # accessible_object_ids = [policy.resource_id for policy in user_policies]
        # return accessible_object_ids
        # pass
