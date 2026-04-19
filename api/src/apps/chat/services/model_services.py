from sqlalchemy.ext.asyncio.session import AsyncSession
from sqlmodel import select
from sqlalchemy import delete, exists, func

import redis.asyncio as redis

from src.caching.services.redis_chatroom_caching import set_chatroom_cache
from src.db.models import (
    Chatroom,
    User,
    UserChatroomBannedLink,
    UserChatroomLink,
    UserChatroomModeratorsLink,
)

from logging import getLogger

logger = getLogger(__name__)


async def check_chatroom_user_member_rel(
    user: User, chatroom: Chatroom, db: AsyncSession
) -> bool:
    """
    Returns boolean result after checking if member relationship exists between `User` and `Chatroom`.
    """
    query = select(
        exists().where(
            UserChatroomLink.chatroom_uid == chatroom.uid,
            UserChatroomLink.user_uid == user.uid,
        )
    )
    executed_query = await db.execute(query)
    relationship_exists = executed_query.scalar_one()
    return relationship_exists


async def check_chatroom_user_moderator_rel(
    user: User, chatroom: Chatroom, db: AsyncSession
) -> bool:
    """
    Returns boolean result after checking if moderator relationship exists between `User` and `Chatroom`.
    """
    query = select(
        exists().where(
            UserChatroomModeratorsLink.chatroom_uid == chatroom.uid,
            UserChatroomModeratorsLink.user_uid == user.uid,
        )
    )
    executed_query = await db.execute(query)
    relationship_exists = executed_query.scalar_one()
    return relationship_exists


async def check_chatroom_user_banned_rel(
    user: User, chatroom: Chatroom, db: AsyncSession
) -> bool:
    """
    Returns boolean result after checking if banned relationship exists between `User` and `Chatroom`.
    """
    query = select(
        exists().where(
            UserChatroomBannedLink.chatroom_uid == chatroom.uid,
            UserChatroomBannedLink.user_uid == user.uid,
        )
    )
    executed_query = await db.execute(query)
    relationship_exists = executed_query.scalar_one()
    return relationship_exists


async def get_chatroom_member_user_count(chatroom: Chatroom, db: AsyncSession) -> int:
    """
    Returns count of `Chatroom` members.
    """
    executed_query = await db.execute(
        (
            select(func.count())
            .select_from(User)
            .join(UserChatroomLink)
            .where(UserChatroomLink.chatroom_uid == chatroom.uid)
        )
    )
    result = executed_query.scalar_one()
    return result


async def get_chatroom_moderator_user_count(
    chatroom: Chatroom, db: AsyncSession
) -> int:
    """
    Get count of `Chatroom` moderator users.
    """
    executed_query = await db.execute(
        select(func.count())
        .select_from(User)
        .join(UserChatroomModeratorsLink)
        .where(UserChatroomModeratorsLink.chatroom_uid == chatroom.uid)
    )
    result = executed_query.scalar_one()
    return result


async def get_chatroom_banned_user_count(chatroom: Chatroom, db: AsyncSession) -> int:
    """
    Get count of `Chatroom` banned users.
    """

    executed_query = await db.execute(
        (
            select(func.count())
            .select_from(User)
            .join(UserChatroomBannedLink)
            .where(UserChatroomBannedLink.chatroom_uid == chatroom.uid)
        )
    )
    result = executed_query.scalar_one()
    return result


async def add_chatroom_user_member_rel(
    user: User, chatroom: Chatroom, db: AsyncSession, r_client: redis.Redis
):
    """
    Creates `User`/`Chatroom` member relationship.
    """
    new_rel = UserChatroomLink(user_uid=user.uid, chatroom_uid=chatroom.uid)
    db.add(new_rel)
    chatroom.members_count += 1
    db.add(chatroom)

    await db.commit()
    await set_chatroom_cache(chatroom=chatroom, r_client=r_client)
    logger.info(
        f"successfully added user: {user.uid} to members chatroom {chatroom.uid}"
    )


async def remove_chatroom_user_member_rel(
    user: User, chatroom: Chatroom, db: AsyncSession, r_client: redis.Redis
):
    """
    Delete `User`/`Chatroom` member relationship.
    """
    await db.execute(
        delete(UserChatroomLink).where(
            UserChatroomLink.user_uid == user.uid,
            UserChatroomLink.chatroom_uid == chatroom.uid,
        )
    )
    chatroom.members_count -= 1
    db.add(chatroom)
    await db.commit()
    await db.refresh(chatroom)
    await set_chatroom_cache(chatroom=chatroom, r_client=r_client)
    logger.info(
        f"successfully removed user: {user.uid} from members for chatroom {chatroom.uid}"
    )


async def add_chatroom_user_moderator_rel(
    user: User, chatroom: Chatroom, db: AsyncSession
):
    """
    Creates `User`/`Chatroom` moderator relationship.
    """
    new_rel = UserChatroomModeratorsLink(user_uid=user.uid, chatroom_uid=chatroom.uid)
    db.add(new_rel)
    await db.commit()
    logger.info(
        f"successfully added user: {user.uid} to moderators for chatroom {chatroom.uid}"
    )


async def remove_chatroom_user_moderator_rel(
    user: User, chatroom: Chatroom, db: AsyncSession
):
    """
    Removes `User`/`Chatroom` moderator relationship.
    """
    await db.execute(
        delete(UserChatroomModeratorsLink).where(
            UserChatroomModeratorsLink.user_uid == user.uid,
            UserChatroomModeratorsLink.chatroom_uid == chatroom.uid,
        )
    )
    await db.commit()
    logger.info(
        f"successfully removed user: {user.uid} from moderators for chatroom {chatroom.uid}"
    )


async def add_chatroom_user_banned_rel(
    user: User, chatroom: Chatroom, db: AsyncSession
):
    """
    Creates `User`/`Chatroom` banned relationship .
    """
    new_rel = UserChatroomBannedLink(user_uid=user.uid, chatroom_uid=chatroom.uid)
    db.add(new_rel)
    await db.commit()
    logger.info(
        f"successfully added user: {user.uid} to banned for chatroom {chatroom.uid}"
    )


async def remove_chatroom_user_banned_rel(
    user: User, chatroom: Chatroom, db: AsyncSession
):
    """
    Deletes `User`/`Chatroom` banned relationship.
    """
    await db.execute(
        delete(UserChatroomBannedLink).where(
            UserChatroomBannedLink.user_uid == user.uid,
            UserChatroomBannedLink.chatroom_uid == chatroom.uid,
        )
    )
    await db.commit()
    logger.info(
        f"successfully removed user: {user.uid} from banned for chatroom {chatroom.uid}"
    )
