import logging

from models.user import UserRead

logger = logging.getLogger(__name__)


class BaseView:
    """Base class for all views"""

    def __init__(self, guards, crud):
        self.crud = crud
        # using private attribute to avoid direct access
        # note Python is not strict on that with _BaseView__update_last_access
        # this variable can still be accessed from the outside
        # thsi should move to either a class guard or class access control
        self.__update_last_access = True

    # TBD: Replace the owner_id with the model from access control table
    # TBD: this functionality should be moved to the security module
    # TBD: and accessed in the CRUD!
    def updates_last_access(
        self, admin: bool, current_user: UserRead, owner_id: str
    ) -> None:
        logger.info("POST updated_last_access")
        if (admin is True) and (str(current_user.user_id) != str(owner_id)):
            self.__update_last_access = False
        return self.__update_last_access


# consider implementing state and/or strategy pattern with extends and implements (if available in Python)?
class BasePOST(BaseView):
    """Base class for POST views"""

    def __init__(self, crud):
        # makes the attributes of the BaseView class available:
        super().__init__(crud)

    # depends on the __updates_last_access attribute of the BaseView class
    async def create(self, object):
        logger.info("POST calls create")
        async with self.crud() as crud:
            created_object = await crud.create(object, self.__update_last_access)
        return created_object
