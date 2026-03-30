# NOKNOW

## ABOUT

NoKnow is a realtime chat web app for users to (openly or anonymously) join discussions
whether public, password protected, or one-on-one chats with friends.
No signup is required for basic functionality.

## FEATURES

### Users, Authentication, and Authorization

User is either a guest (`unknown`), or signed in (`known`).

Authenticated users are of 3 categories; user, admin, and superuser,
with `admin`s and `superuser`s possessing admin privileges over database, which can be accessed via admin CMS panel.
JWT Tokens are used for authorization.

Signed in users can choose to stay `hidden` and use anonymous usernames (like guest users) when engaging in chats.
On signup, user must provide a valid email which will be confirmed via OTP verification.
User can activate two factor authentication for more protected future logins.

Admin users and superusers have access to Admin CMS panel, however, they would have to log in through the admin route as normal login would provide JWT and Refresh tokens without the necessary authorization payloads.

Admin users, superusers, and users with their `hidden` status active cannot be found by other users in search.

#### Guest user

- Create and engage public chatrooms only.
- Switch anonymous username.

#### Authenticated user

- Create and engage public chatrooms, as well as private chatrooms.
- Switch anonymous username.
- Send, recieve, accept, and reject friend requests.
- View sent friend requests.
- Update bio information, email, username, and password.
- Recover account via email if password is forgotten.
- Choose stay hidden like a guest.
- In `hidden` status, all messages sent in private and public chatrooms will use set anonymous
  username except for friend chats.
- In `hidden` status, user cannot be seen by fellow chatroom members except for moderators and
  chatroom creator.

### Chatrooms

There are three type of chats namely; Public chatroom, private chatroom, and personal chatroom(for friends).

- Public chatrooms can be created and engaged with no signup required.
- Private chatroooms require user to be signed. To engaged a private chatroom, user must first join by providing the correct password for the chatroom.
- Friend/Personal chatrooms require user to be signed in. user can only engage another user in personal
  chat if they are already friends.
- All users, anonymous and signed in, can create only 3 chatrooms per hour.
- Message broadcasts are sent to chat on certain events e.g user leaves chatroom, user becomes a moderator, etc.

#### Public chatroom

- Standard messaging.
- No login required to create and engage.
- Members and non members can engage. Free for all.
- Join and leave chatroom if signed in.
- Users cannot be added or removed.
- The chatroom creator cannot assign moderators.
- if logged in, user who creates chatroom automatically becomes creator and member.

#### Private chatroom

- Standard messaging
- Login required to create and engaged.
- Only members can engaged.
- Password required to join and create.
- User who creates chatroom automatically becomes creator and member.
- Messages recording can be turned off (`secret mode`) to stop messages being saved in the database for extra privacy.
- `Secret mode` is turned off automatically after the last active user in chatroom disconnects.
- The chatroom creator can make members into moderators.
- Only the chatroom creator can remove moderators. a moderator cannot remove a moderator.
- The chatroom creator and moderators can add their friends to members.
- The chatroom creator and moderators can remove members.
- Chatroom can have a maximum of nine (9) moderators, plus creator (10 in total).
- Removing a member automatically bans them from re-entering chatroom even with password
  provided until they are re-added/unbanned by a moderator or creator.
- Removed users are banned and restricted from joining chatroom unless re-added by a
  moderator or creator.
- The chatroom creator cannot leave chatroom without assigning a successor first
  only a moderator can be made into a successor.
- Unlike the creator, the successor is allowed to leave the chatroom. on leaving, they
  forfeit the role of successor.
- If a successor is demoted from moderator to regular member, they automatically lose
  the title of successor.
- When creator leaves chatroom, the successor automatically gets assigned the role of
  creator along with all privileges attached.
- Chatroom members can view fellow members except for those with their `hidden` status active.
- Members with `hidden` status active can be viewed only by moderators and creator.

#### Personal chatroom

- Standard messaging.
- Login required to engage.
- Only 2 members can engage. user and friend.
- Second-party user must currently be a friend to be engaged.
- Messages recording can be turned off (secret mode) to stop messages being saved in the database for extra privacy.
- Secret mode is turned off automatically after the last active user in chatroom
  disconnects.
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
- `NOT_ADMIN_ERROR_CODE`

## INSTALLATION

- Create a ".env" file and set all listed environment variables. Feel free to fill dummy values for the `MAIL` related environment variables, but bear in mind that this will disable email features needed for email otp verification tasks. You can tweak OTP services to print OTP codes in your terminal during development, but remember to disable that tweak when pushing to prod.

- Setup docker if you do not already have it set up on your device. Click and follow the official guide for your setting up Docker on your [Linux device](https://docs.docker.com/desktop/setup/install/linux), [Windows device](https://docs.docker.com/desktop/setup/install/windows-install), and [Mac device](https://docs.docker.com/desktop/setup/install/mac-install)

- Inside this root directory with the docker-compose.yaml file, run:
```bash
  docker compose up --build
```

## DOCS

- Back-end: [backend/README.md](./api/README.md)
- Front-end: [frontend/README.md](./frontend/README.md)

## Authors

- [LinkedIn@victorsunny](https://www.linkedin.com/in/victor-sunny-6b06ba220)

- [Github@victorsunny](https://www.github.com/victorsunny/)

- [Discord](https://discordapp.com/users/1296969973155102761)

- [Portfolio](https://victorsunny.github.io)

## About Me

Hello there, [Victor](https://www.linkedin.com/in/victor-sunny-6b06ba220) here.

I'm a full-stack web developer with strong back-end expertise, and i believe every problem can be fixed with enough effort.

I am highly proficient in web/app developement using Python, Javascript, Typescript, HTML, CSS, Django, FastAPI, React, and other related technologies. Readily adopting and adapting to new/required technologies.

## Screenshots

![noknow-1](https://github.com/user-attachments/assets/401a1623-4812-439a-9299-d91f87ad1437)
![noknow-mobile-1](https://github.com/user-attachments/assets/1a4276e4-ea2f-4734-b6eb-fd1f93ce88ba)
![noknow-2](https://github.com/user-attachments/assets/88324d46-fa7f-43e1-8fea-c30055d9b6ff)
![noknow-mobile-2](https://github.com/user-attachments/assets/64835d61-3003-48e8-bf63-72f7e3abf91f)
![noknow-3](https://github.com/user-attachments/assets/4841a1d2-6bd6-4daf-aa7f-e60321f1ef33)
![noknow-mobile-3](https://github.com/user-attachments/assets/5550ea10-cd16-435c-a9fc-2a1aa286c789)
![noknow-4](https://github.com/user-attachments/assets/b59af432-6145-424a-a94f-747f17a66d07)
![noknow-mobile-4](https://github.com/user-attachments/assets/8adb5f24-e30d-4edc-8354-b27b1bdc1e41)
![noknow-5](https://github.com/user-attachments/assets/5ea436eb-3cb9-4ffe-ba2b-aff03cc97cb6)
![noknow-mobile-5](https://github.com/user-attachments/assets/777ac704-e06a-432d-a333-4b6ac6d8648a)
![noknow-6](https://github.com/user-attachments/assets/7dfabb4b-3d84-4e8a-9064-e5dfb2ba399e)
![noknow-mobile-6](https://github.com/user-attachments/assets/86202c3f-1ae5-414e-8242-32c240d09db2)
![noknow-7](https://github.com/user-attachments/assets/e8ffc4f9-f747-4624-b4ea-f4527b1eb406)
![noknow-mobile-7](https://github.com/user-attachments/assets/78f16761-1cb1-4fc6-b827-91a320b2dbfe)
![noknow-8](https://github.com/user-attachments/assets/c1334633-8a3a-4664-9040-cf6826a51b43)
![noknow-mobile-8](https://github.com/user-attachments/assets/57d229a7-4998-4246-a60a-504d372a33f1)
![noknow-9](https://github.com/user-attachments/assets/fd149b5f-8d1f-4ee1-8c70-b510da7956e9)
![noknow-mobile-9](https://github.com/user-attachments/assets/2d5d424e-1173-423f-9837-d096c1d80aa2)
![noknow-10](https://github.com/user-attachments/assets/f9c8fa57-8e5c-47d9-a367-bcdf778827e6)
![noknow-mobile-10](https://github.com/user-attachments/assets/737682fb-2bbb-4a46-8929-d588c5b790f4)
