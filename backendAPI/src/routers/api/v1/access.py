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
# - read by resource - use filter
# - read by identity - use filter
# - change access Action (own, write, read) -> use delete and create
# - delete (unshare)
# - hierarchy (inheritance)?
# AccessLogs:
# - read (check who accessed what)
# - read first "own": corresponds to create
# - read last access - use order_by
# - read access count - use func.count
# - read access by identity - use filter
# - read access by resource - use filter
