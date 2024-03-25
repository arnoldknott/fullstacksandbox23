# import logging

# from fastapi import APIRouter

# logger = logging.getLogger(__name__)
# router = APIRouter()


# implement protected routes for:
# AccessPolicies:
# - create (share with identity, i.e. user, group)
# - create (public share)
# - make a generic for the above two!
# - read (check who has access)
# - delete (unshare)
# - hierarchy (inheritance)?
# AccessLogs:
# - read (check who accessed what)
# - read first "own": corresponds to create
# - read last access
# - read access count
