from sqlalchemy import delete, exists, func, or_
from sqlalchemy.ext.asyncio.session import AsyncSession
from sqlmodel import select

from src.db.models import (
    User,
    UserFriendship,
    UserFriendshipRequest,
)

from logging import getLogger

logger = getLogger(__name__)


async def get_user_friend_count(user: User, db: AsyncSession) -> int:
    executed_query = await db.execute(
        (
            select(func.count())
            .select_from(UserFriendship)
            .where(UserFriendship.user_uid == user.uid)
        )
    )
    result = executed_query.scalar_one()
    return result


async def check_friend_rel(user: User, to_check: User, db: AsyncSession) -> bool:
    """
    Checks if two provided `User`s are friends.
    Returns `True` if both `User`s are friends, `False` if not.

    Args:
        user: Logged in `User` instance
        to_check: Second `User instance to check if friend
        db: Asynchronous database connection instance
    """
    query = select(
        exists().where(
            UserFriendship.user_uid == user.uid,
            UserFriendship.friend_uid == to_check.uid,
        )
    )
    executed_query = await db.execute(query)
    relationship_exists = executed_query.scalar_one()
    return relationship_exists


async def check_friend_request_rel(
    from_user: User, to_user: User, db: AsyncSession
) -> bool:
    """
    Checks if friend request has been sent between `User`s.
    Returns `True` if relationship exists, `False` if not.

    Args:
        from_user: `User` instance to check if is the sender of the friend request
        to_user: `User` instance to check if is the reciever of the friend request
        db: Asynchronous database connection instance
    """
    query = select(
        exists().where(
            UserFriendshipRequest.user_uid == to_user.uid,
            UserFriendshipRequest.request_friend_uid == from_user.uid,
        )
    )
    executed_query = await db.execute(query)
    relationship_exists = executed_query.scalar_one()
    return relationship_exists


async def add_friend_request_rel(from_user: User, to_user: User, db: AsyncSession):
    """
    Sends friend request from one `User` to another by creating relationship in database.

    Args:
        from_user: `User` instance to sending the friend request
        to_user: `User` instance to receiving the friend request
        db: Asynchronous database connection instance
    """
    friend_request = UserFriendshipRequest(
        user_uid=to_user.uid, request_friend_uid=from_user.uid
    )
    db.add(friend_request)
    await db.commit()
    logger.info(
        f"user: {from_user.uid} successfully sent friend request to for user: {to_user.uid}"
    )


async def remove_friend_request_rel(from_user: User, to_user: User, db: AsyncSession):
    """
    Unsends friend request from one `User` to another by deleting relationship in database.

    Args:
        from_user: `User` instance to cancelling the friend request
        to_user: `User` instance that received the friend request
        db: Asynchronous database connection instance
    """
    await db.execute(
        delete(UserFriendshipRequest).where(
            UserFriendshipRequest.user_uid == to_user.uid,
            UserFriendshipRequest.request_friend_uid == from_user.uid,
        )
    )
    await db.commit()
    logger.info(
        f"user: {from_user.uid} successfully removed friend request to user: {to_user.uid}"
    )


async def add_friend_rel(user: User, candidate: User, db: AsyncSession):
    """
    Adds one `User` to the friend list of another by creating relationship in database.

    Args:
        user: Logged in `User` instance adding friend
        candidate: `User` instance to be added to friend list
        db: Asynchronous database connection instance
    """
    friendship = UserFriendship(user_uid=user.uid, friend_uid=candidate.uid)
    db.add(friendship)
    await db.commit()
    logger.info(
        f"successfully added user: {candidate.uid} to friends for user: {user.uid}"
    )


async def remove_friend_rel(user: User, candidate: User, db: AsyncSession):
    """
    Removes one `User` from another's friend list by deleting relationship in database.

    Args:
        user: Logged in `User` instance removing friend
        candidate: `User` instance being removed from friend list
        db: Asynchronous database connection instance
    """
    await db.execute(
        delete(UserFriendship).where(
            UserFriendship.user_uid == user.uid,
            UserFriendship.friend_uid == candidate.uid,
        )
    )
    await db.commit()
    logger.info(f"successfully removed friend: {candidate.uid} for user: {user.uid}")
