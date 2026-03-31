from enum import Enum
from typing import List
from uuid import UUID, uuid4

from sqlalchemy import ForeignKey
from sqlmodel import Field, Relationship, SQLModel

from src.utilities.utilities import timestamp_now

# TODO correct UserRoleChoices Enum class for role field


class ChatroomType(str, Enum):
    private = "private"
    public = "public"
    personal = "personal"


class UserChatroomLink(SQLModel, table=True):
    user_uid: UUID = Field(
        primary_key=True, sa_column_args=[ForeignKey("user.uid", ondelete="CASCADE")]
    )
    chatroom_uid: UUID = Field(
        primary_key=True,
        sa_column_args=[ForeignKey("chatroom.uid", ondelete="CASCADE")],
    )
    created_at: float | None = Field(default_factory=timestamp_now)


class UserChatroomModeratorsLink(SQLModel, table=True):
    user_uid: UUID = Field(
        primary_key=True, sa_column_args=[ForeignKey("user.uid", ondelete="CASCADE")]
    )
    chatroom_uid: UUID = Field(
        primary_key=True,
        sa_column_args=[ForeignKey("chatroom.uid", ondelete="CASCADE")],
    )
    created_at: float | None = Field(default_factory=timestamp_now)


class UserChatroomBannedLink(SQLModel, table=True):
    user_uid: UUID = Field(
        primary_key=True, sa_column_args=[ForeignKey("user.uid", ondelete="CASCADE")]
    )
    chatroom_uid: UUID = Field(
        primary_key=True,
        sa_column_args=[ForeignKey("chatroom.uid", ondelete="CASCADE")],
    )
    created_at: float | None = Field(default_factory=timestamp_now)


class UserFriendship(SQLModel, table=True):
    user_uid: UUID = Field(
        primary_key=True,
        foreign_key="user.uid",
        sa_column_args=[ForeignKey("user.uid", ondelete="CASCADE")],
    )
    friend_uid: UUID = Field(
        primary_key=True,
        foreign_key="user.uid",
        sa_column_args=[ForeignKey("user.uid", ondelete="CASCADE")],
    )
    created_at: float | None = Field(default_factory=timestamp_now)

    # __table_args__ = [
    #     (SQLModel.metadata.tables["UserFriendship"].c.user_uid != SQLModel.metadata.tables["UserFriendship"].c.friend_uid),
    # ]


class UserFriendshipRequest(SQLModel, table=True):
    user_uid: UUID = Field(primary_key=True, foreign_key="user.uid")
    request_friend_uid: UUID = Field(primary_key=True, foreign_key="user.uid")
    created_at: float | None = Field(default_factory=timestamp_now)

    # __table_args__ = [
    #     (SQLModel.metadata.tables["UserFriendshipRequest"].c.user_uid != SQLModel.metadata.tables["UserFriendshipRequest"].c.request_friend_uid),
    # ]


class User(SQLModel, table=True):
    __tablename__ = "user"

    uid: UUID | None = Field(default_factory=uuid4, nullable=False, primary_key=True)
    google_oauth2_id: str | None = Field(default=None, index=True)
    first_name: str = Field(min_length=2, nullable=False)
    last_name: str = Field(min_length=2, nullable=False)
    username: str = Field(unique=True, min_length=2, nullable=False, max_length=25)
    email: str = Field(unique=True, index=True, nullable=False)
    bio: str | None = Field(default="doing something on the web", max_length=255)
    active: bool = Field(default=True)
    password: str
    role: str | None = Field(default="user")
    created_at: float | None = Field(default_factory=timestamp_now)
    modified_at: float | None = Field(default_factory=timestamp_now)

    last_seen: float | None = Field(default_factory=timestamp_now)

    is_hidden: bool | None = Field(default=False)
    is_two_factor_authenticated: bool | None = Field(default=False)

    friends: List["User"] = Relationship(
        link_model=UserFriendship,
        sa_relationship_kwargs={
            "primaryjoin": "User.uid==UserFriendship.user_uid",
            "secondaryjoin": "User.uid==UserFriendship.friend_uid",
        },
    )
    friend_requests: List["User"] = Relationship(
        link_model=UserFriendshipRequest,
        sa_relationship_kwargs={
            "order_by": "UserFriendshipRequest.created_at",
            "primaryjoin": "User.uid==UserFriendshipRequest.user_uid",
            "secondaryjoin": "User.uid==UserFriendshipRequest.request_friend_uid",
        },
    )

    chatrooms: List["Chatroom"] = Relationship(
        back_populates="members",
        link_model=UserChatroomLink,
        sa_relationship_kwargs={
            "order_by": "UserChatroomLink.created_at",
        },
    )
    moderated_chatrooms: List["Chatroom"] = Relationship(
        back_populates="moderators",
        link_model=UserChatroomModeratorsLink,
        sa_relationship_kwargs={
            "order_by": "UserChatroomModeratorsLink.created_at",
        },
    )
    restricted_chatrooms: List["Chatroom"] = Relationship(
        back_populates="banned_users",
        link_model=UserChatroomBannedLink,
        sa_relationship_kwargs={
            "order_by": "UserChatroomBannedLink.created_at",
        },
    )
    created_chatrooms: List["Chatroom"] = Relationship(
        back_populates="creator",
        sa_relationship_kwargs={
            "foreign_keys": "[Chatroom.creator_uid]",
            "order_by": "Chatroom.created_at",
        },
    )
    trusteed_chatrooms: List["Chatroom"] = Relationship(
        back_populates="creator_successor",
        sa_relationship_kwargs={
            "foreign_keys": "[Chatroom.creator_successor_uid]",
            "order_by": "Chatroom.created_at",
        },
    )

    def __repr__(self) -> str:
        return f"<User>: {self.username}"


class Chatroom(SQLModel, table=True):
    __tablename__ = "chatroom"

    uid: UUID | None = Field(default_factory=uuid4, primary_key=True)
    name: str | None = Field(default=None, max_length=64)
    about: str | None = Field(default="join the conversation", max_length=255)
    password: str | None
    original_creator_username: str | None
    members_count: int | None = Field(default=0)
    room_type: ChatroomType | None = ChatroomType.public

    created_at: float | None = Field(default_factory=timestamp_now)
    modified_at: float | None = Field(default_factory=timestamp_now)

    messages: List["Message"] = Relationship(
        back_populates="chatroom",
        sa_relationship_kwargs={"passive_deletes": True},
        cascade_delete=True,
    )
    members: List[User] = Relationship(
        back_populates="chatrooms",
        link_model=UserChatroomLink,
        sa_relationship_kwargs={
            "order_by": "UserChatroomLink.created_at",
        },
    )
    moderators: List[User] = Relationship(
        back_populates="moderated_chatrooms",
        link_model=UserChatroomModeratorsLink,
        sa_relationship_kwargs={
            "order_by": "UserChatroomModeratorsLink.created_at",
        },
    )
    banned_users: List[User] = Relationship(
        back_populates="restricted_chatrooms",
        link_model=UserChatroomBannedLink,
        sa_relationship_kwargs={
            "order_by": "UserChatroomBannedLink.created_at",
        },
    )

    creator_uid: UUID | None = Field(
        default=None, sa_column_args=[ForeignKey("user.uid", ondelete="CASCADE")]
    )
    creator_successor_uid: UUID | None = Field(
        default=None, sa_column_args=[ForeignKey("user.uid", ondelete="CASCADE")]
    )

    creator: User | None = Relationship(
        back_populates="created_chatrooms",
        sa_relationship_kwargs={"foreign_keys": "Chatroom.creator_uid"},
    )
    creator_successor: User | None = Relationship(
        back_populates="trusteed_chatrooms",
        sa_relationship_kwargs={"foreign_keys": "Chatroom.creator_successor_uid"},
    )

    def __repr__(self) -> str:
        return f"<chatroom_uid: {self.uid}>"


class Message(SQLModel, table=True):
    __tablename__ = "message"

    id: int = Field(default=None, primary_key=True)
    created_at: float | None = Field(default_factory=timestamp_now)
    sender_username: str | None = Field(default=None)
    sender_uid: UUID | None = Field(default=None)
    type: str | None
    content: str
    content_type: str

    chatroom: Chatroom | None = Relationship(back_populates="messages")
    chatroom_uid: UUID = Field(
        nullable=False, sa_column_args=[ForeignKey("chatroom.uid", ondelete="CASCADE")]
    )

    def __repr__(self) -> str:
        return f"<Message {self.id}"


class BlacklistedToken(SQLModel, table=True):
    __tablename__ = "blacklisted_token"

    id: int = Field(default=None, primary_key=True)
    jti: UUID = Field(index=True)
    exp: float
    created_at: float | None = Field(default_factory=timestamp_now)


class BlacklistedEmail(SQLModel, table=True):
    __tablename__ = "blacklisted_email"

    id: int = Field(default=None, primary_key=True)
    sub: str = Field(unique=True, index=True, nullable=False)
    created_at: float | None = Field(default_factory=timestamp_now)

    def __repr__(self) -> str:
        return f"<Blacklisted_Email {self.id}>"
