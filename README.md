# NOKNOW

## ABOUT

NoKnow is a realtime chat web app for users to (openly or anonymously) join discussions
whether public, password protected, or one-on-one chats with friends.
No signup is required for basic functionality.

## FEATURES

### Users, Authentication, and Authorization

User is either a guest (unauthenticated), or signed in (authenticated).

Authenticated users are of 3 categories; user, admin, and superuser,
with `admin`s and `superuser`s possessing admin privileges over database, which can be accessed via admin CMS panel.

Signed in users can choose to stay `hidden` and use anonymous usernames (like guest users) when engaging in chats.
On signup, user must provide a valid email which will be confirmed via OTP verification.
User can activate two factor authentication for more protected future logins.

#### Guest user

- Create and engage public chatrooms only.
- Switch anonymous username.

#### Authenticated user

- Create and engage public chatrooms, as well as private chatrooms.
- Switch anonymous username at will.
- Send, recieve, accept, and reject friend requests.
- View sent friend requests.
- Update bio information, email, username, and password.
- Recover account via email if password is forgotten.
- Choose stay hidden like a guest.
- In `hidden` status, all messages sent in private and public chatrooms will use set anonymous
  username except for friend chats.
- In `hidden` status, user cannot be seen by fellow chatroom members except for moderators and
  chatroom creator.
- In `hidden` status , user cannot be found by other users in search.

### Chatrooms

There are three type of chats namely; Public chatroom, private chatroom, and personal chatroom.

- `Public chatroom`s can be created and engaged with no signup required.
- `Private chatrooom`s require user to be signed. To engaged a private chatroom, user must first join by providing the correct password for the chatroom.
- `Friend chat`s require user to be signed in. user can only engage another user in personal
  chat if they are already friends.
- All users, anonymous and signed in, can create only 3 chatrooms per hour.
- Message broadcasts are sent to chat on certain events e.g user leaves chatroom, user becomes a moderator.

#### Public chatroom

- Standard messaging.
- No login required to create and engage.
- Members and non members can engage
- Join and leave chatroom if signed in.
- Free for all. users cannot be added or removed.
- Creator cannot assign moderators.
- if logged in, user who creates chatroom automatically becomes creator and member.

#### Private chatroom

- Standard messaging
- Login required to create and engaged.
- Only members can engaged.
- Password required to join and create.
- User who creates chatroom automatically becomes creator and member.
- Messages recording can be turned off (secret mode) to stop messages being saved in the database for extra privacy.
- Messages sent when in secret mode can only be viewed by users currently in chat.
- Messages recieved in secret mode are not stored in database and are cleared when tab is closed.
- Secret mode is turned off automatically after the last active user in chatroom disconnects.
- Unlimited number of members allowed to join and engage.
- Creator can make members into moderators.
- Only creator can remove moderators. a moderator cannot remove a moderator.
- Creator and moderators can add their friends to members.
- Creator and moderators can remove members.
- Chatroom can have a maximum of nine (9) moderators, plus creator (10 in total).
- Removing a member automatically bans them from re-entering chatroom even with password
  provided until they are re-added/unbanned by a moderator or creator.
- Removed users are banned and restricted from joining chatroom unless re-added by a
  moderator or creator.
- Creator cannot leave chatroom without assigning a successor first
  only a moderator can be made into a successor.
- Unlike the creator, the successor is allowed to leave the chatroom. on leaving, they
  forfeit the role of successor.
- If a successor is demoted from moderator to regular member, they automatically lose
  the title of successor.
- When creator leaves chatroom, the successor automatically gets assigned the role of
  creator along with all privileges attached.
- In chatroom member can view all fellow members except for except for users with `hidden` active,
  only chatroom moderators can see members with `hidden` status active.
- Hidden members can only be viewed by moderators and creator.

#### Personal chatroom

- Standard messaging.
- Login required to engage.
- Second-party user must be a friend to be engaged.
- Messages recording can be turned off (secret mode) to stop messages being saved in the database for extra privacy.
- Nessages sent when in secret mode can only be viewed by users currently in chat.
- Secret mode is turned off automatically after the last active user in chatroom
  disconnects.
- Only 2 members can engage. user and friend.
- Chat history can be deleted for both parties.

## TECH STACK

### Back-end

- Python
- FastAPI
- Postgresql
- Redis
- Celery
- JWT
- Oauth 2.0
- Alembic
- Pydantic
- UV
- Uvicorn
- SqlAlchemy
- SqlModel
- Pytest

### Front-end

- Typescript
- React
- HTML & CSS
- Zod
- Tanstack query
- Framer motion
- Vite

## ENVIRONMENT VARIABLES

- `DEBUG`

- `SECRET_KEY`
- `HASHING_ALGORITHM`

- `DOCKER_FRONTEND_IMAGE`
- `DOCKER_FRONTEND_IMAGE_TAG`
- `DOCKER_BACKEND_IMAGE`
- `DOCKER_BACKEND_IMAGE_TAG`

- `ACCESS_TOKEN_EXPIRY_MINUTES`
- `REFRESH_TOKEN_EXPIRY_DAYS`

- `POSTGRES_USER`
- `POSTGRES_PASSWORD`
- `POSTGRES_DB`
- `POSTGRES_HOST`
- `POSTGRES_PORT`
- `REDIS_URL`

- `GOOGLE_REDIRECT_URI`
- `GOOGLE_CLIENT_ID`
- `GOOGLE_CLIENT_SECRET`

- `MAIL_USERNAME`
- `MAIL_FROM`
- `MAIL_PASSWORD`
- `MAIL_SERVER`

- `ACCOUNT_SUSPENDED_ERROR_CODE`
- `NOT_ADMIN_ERROR`

## DOCS

- Back-end: [backend/README.md](./api/README.md)
- Front-end: [frontend/README.md](./frontend/README.md)
