# import logging

# from uuid import UUID
# from typing import Optional, Union
# from core.types import CurrentUserData, Action, ResourceType, IdentityType
# from fastapi import HTTPException
# from models.access import AccessPolicy, IdentifierTypeLink

# from sqlmodel import select, or_, SQLModel

# # if TYPE_CHECKING:
# #     from core.types import CurrentUserData, Action


# logger = logging.getLogger(__name__)


# TBD: remove the entire file and implement everything in AccessCRUD!


# class AccessControl:
#     """Class for access control"""

#     def __init__(self, policy_crud) -> None:
#         self.policy_crud = policy_crud

#     async def __check_resource_inheritance(self):
#         """Checks if the resource inherits permissions from a parent resource"""
#         # TBD: check the inheritance flag in the resource hierarchy table and stop, if not inherited!
#         pass

#     async def __check_identity_inheritance(self):
#         """Checks if the resource inherits permissions from a parent resource"""
#         # TBD: check if the identity inherits permissions from a parent identity (aka group)
#         pass
#
# def filters_allowed(
#     self,
#     statement: select,
#     model: SQLModel,
#     action: "Action",
#     current_user: Optional["CurrentUserData"] = None,
# ):
#     """Finds all resources of a certain type and action that the user has permission to access"""
#     # TBD: implement this
#     # ✔︎ find all public resources of the given type and action
#     # ✔︎ find all resources of the given type and action that the user has permission to access
#     # - find all resources of the given type and action that the user has permission to access through resource inheritance
#     # - find all resources of the given type and action that the user has permission to access through group membership (identity inheritance)
#     # - find all resources of the given type and action that the user has permission to access through group membership (identity inheritance) and resource inheritance
#     # - find all resources of the given type and action that the user has permission to access through group membership (identity inheritance) and resource inheritance and public access
#     # - find all resources of the given type and action that the user has permission to access through group membership (identity inheritance) and resource inheritance and public access and admin override

#     # Permission overrides:
#     # own includes write and read
#     # write includes read
#     if action == Action.read:
#         action = ["own", "write", "read"]
#     elif action == Action.write:
#         action = ["own", "write"]
#     elif action == Action.own:
#         action = ["own"]

#     # print("=== core.access - AccessControl - filters_allowed - action ===")
#     # print(action)

#     if not current_user:
#         if model != AccessPolicy:
#             statement = statement.join(
#                 AccessPolicy, model.id == AccessPolicy.resource_id
#             )
#             statement = statement.where(AccessPolicy.resource_id == model.id)
#         statement = statement.where(AccessPolicy.action.in_(action))
#         statement = statement.where(AccessPolicy.public)
#     elif "Admin" in current_user.roles:
#         pass
#     else:
#         if model != AccessPolicy:
#             statement = statement.join(
#                 AccessPolicy, model.id == AccessPolicy.resource_id
#             )
#             statement = statement.where(AccessPolicy.resource_id == model.id)
#         statement = statement.where(AccessPolicy.action.in_(action))
#         statement = statement.where(
#             or_(
#                 AccessPolicy.identity_id == current_user.user_id,
#                 AccessPolicy.public,
#             )
#         )

#     # print("=== core.access - AccessControl - statement ===")
#     # print(statement)

#     return statement

# async def allows(
#     self,
#     resource_id: UUID,
#     action: "Action",
#     current_user: Optional["CurrentUserData"] = None,
# ) -> bool:
#     """Checks if the user has permission including inheritance to perform the action on the resource"""
#     # TBD: move the logging to the BaseCrud? Or keep it here together with the Access Control?
#     # loggingCRUD = AccessLoggingCRUD()
#     # TBD: get all policies for the resource, where any of the hierarchical identities and hierarchical resources match
#     # Don't include the identity in the query, as public resources are not assigned to any identity!
#     # TBD: implement "public" override: check if the resource is public for requested action and return True if it is!

#     # TBD: call the filters_allowed method and execute the statement here.
#     # check for public override:
#     if not current_user:
#         # async with self.policy_crud as policy_crud:
#         policy_crud = self.policy_crud
#         # add join with inheritance table
#         # policies = await policy_crud.read(
#         #     resource_id=resource_id, resource_type=resource_type, action=action
#         # )
#         policies = await policy_crud.read(resource_id=resource_id, action=action)
#         for policy in policies:
#             if policy.public:
#                 return True
#             else:
#                 logger.error("Error accessing resource without user information.")
#                 raise HTTPException(status_code=403, detail="Access denied")
#     # check for admin override:
#     elif current_user.roles and "Admin" in current_user.roles:
#         return True
#     # TBD: implement the comparison of policies and request.
#     else:
#         policy_crud = self.policy_crud
#         # async with self.policy_crud as policy_crud:
#         # add join with inheritance table for both resource and identity
#         policies = await policy_crud.read(
#             resource_id=resource_id,
#             action=action,
#             identity_id=current_user.user_id,
#         )
#         if policies is not None:
#             return True
#         else:
#             logger.error("Error accessing resource.")
#             raise HTTPException(status_code=403, detail="Access denied")

#     query = select(AccessPolicy).where(
#         AccessPolicy.resource_id == resource_id,
#     )

#     query = self.filters_allowed(
#         query, AccessPolicy, action, current_user=current_user
#     )


#     return False


# USED AS SCRATCH:


# @pytest.fixture(scope="function")
# async def register_one_resource():
#     """Registers a resource id and its type in the database."""

#     async def _register_one_resource(
#         resource_id: str, model: ResourceType = ProtectedResource
#     ):
#         """Registers a resource id and its type in the database."""
#         await register_resource_to_resource_link_table(resource_id, model)
#         return resource_id

#         # async with BaseCRUD(model) as crud:
#         #     crud._add_resource_type_link_to_session(resource_id)
#         #     await crud.session.commit()
#         #     # resource_link = await crud.session.get(
#         #     #     IdentityTypeLink, resource_id
#         #     # )
#         #     # print("=== conftest - register_one_resource - resource_link ===")
#         #     # pprint(resource_link)
#         # return resource_id

#     yield _register_one_resource


# @pytest.fixture(scope="function")
# async def register_many_protected_resources():
#     """Registers many resources with id and its type in the database."""

#     for resource_id in many_resource_ids:
#         await register_resource_to_resource_link_table(resource_id, ProtectedResource)

#     yield many_resource_ids

#     # async def _register_many_resources(model: ResourceType = ProtectedResource):
#     #     for resource_id in many_resource_ids:
#     #         await register_resource_to_resource_link_table(resource_id, model)
#     #     # for resource in resource_id:
#     #     #     await register_resource_to_resource_link_table(resource, model)
#     #     print("=== conftest - register_many_resources - resource_id ===")
#     #     pprint(resource_id)
#     #     return resource_id

#     #     # async with BaseCRUD(model) as crud:

#     #     #     crud._add_resource_type_link_to_session(resource_id)
#     #     #     await crud.session.commit()
#     #     #     # resource_link = await crud.session.get(
#     #     #     #     IdentityTypeLink, resource_id
#     #     #     # )
#     #     #     # print("=== conftest - register_one_resource - resource_link ===")
#     #     #     # pprint(resource_link)
#     #     # return resource_id

#     # yield _register_many_resources
