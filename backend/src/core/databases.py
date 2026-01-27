from sqlalchemy.ext.asyncio import async_sessionmaker, create_async_engine
from sqlmodel.ext.asyncio.session import AsyncSession

from core.config import config

# from sqlmodel import SQLmodel  # noqa: F401

postgres_async_engine = create_async_engine(
    config.POSTGRES_URL.unicode_string(),
    # TBD: nested context managers require architectural fix!
    # Pass session as optional argument from calling CRUD to nested CRUDs
    # for example from DemoResourceCRUD to BaseCrud to AccessPolicyCRUD
    # to avoid exhausting the connection pool with multiple sessions
    # instead of creating new sessions in each CRUD.
    pool_size=40,  # Increased due to nested session pattern (3-5 connections per request) - default 5
    max_overflow=50,  # Emergency overflow for burst traffic (total: 120 max) - default: 10
    # total (default) max of database is 100 - leaves 10 for pgadmin connections.
    pool_timeout=90,  # Increased timeout to handle queue waits - default 30 (seconds)
    pool_pre_ping=True,  # Test connections health
    pool_recycle=3600,  # Recycle connections after 1 hour
)  # TBD: remove echo=True


async def get_async_session() -> AsyncSession:
    """Returns a database session."""
    async_session = async_sessionmaker(
        bind=postgres_async_engine, class_=AsyncSession, expire_on_commit=False
    )
    return async_session()


# Run extraordinary migrations:
# Comment when propagated all the way into production!
async def run_migrations():
    pass
    # Did not work in production!
    # session = await get_async_session()
    # # async with get_async_session() as session:
    # response = await session.exec(select(User))
    # users = response.unique().fetchall()
    # for user in users:
    #     # # The settings in user account and user profile cannot be changed, before the user is created.
    #     try:
    #         query = select(UserAccount, UserProfile).where(
    #             UserAccount.user_id == user.id, UserProfile.user_id == user.id
    #         )
    #         response = await session.exec(query)
    #         existing_account_and_profile = response.unique().fetchall()
    #         print("=== existing_account_and_profile ===")
    #         print(existing_account_and_profile)
    #         if not existing_account_and_profile:
    #             print("== no account or profile found - trying to generate it ===")
    #             user_account = UserAccount(user_id=user.id)
    #             user_profile = UserProfile(user_id=user.id)
    #             account_type_link = IdentifierTypeLink(
    #                 id=user_account.id, type=IdentityType.user_account
    #             )
    #             profile_type_link = IdentifierTypeLink(
    #                 id=user_profile.id, type=IdentityType.user_profile
    #             )
    #             user_account = UserAccount.model_validate(user_account)
    #             user_profile = UserProfile.model_validate(user_profile)
    #             user.user_account_id = user_account.id
    #             user.user_profile_id = user_profile.id

    #             session.add(user_account)
    #             session.add(user_profile)
    #             session.add(account_type_link)
    #             session.add(profile_type_link)
    #             session.add(user)
    #             await session.commit()
    #             await session.refresh(user_account)
    #             await session.refresh(user_profile)
    #             await session.refresh(account_type_link)
    #             await session.refresh(profile_type_link)
    #             await session.refresh(user)
    #     except Exception as error:
    #         print("Error in run_migrations:")
    #         print(error)
    #         await session.rollback()
    # await session.close()


# engine = create_engine(config.POSTGRES_URL.unicode_string())
# SynchronSession = sessionmaker(autocommit=False, autoflush=False, bind=engine)

# # This is handled by __aenter__ and __aexit__ in BaseCRUD
# # in case a session is required elsewhere, use this function!
# async def use_async_session() -> AsyncSession:
#     """Yields a database session."""
#     async_session = get_async_session()
#     async with async_session() as session:
#         yield session
#     # session.close()
