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
- `REDIS_TEST_URL`

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

- Setup docker if you do not already have it set up on your device. Click and follow the link to the official guide for setting up Docker on your [Linux device](https://docs.docker.com/desktop/setup/install/linux), [Windows device](https://docs.docker.com/desktop/setup/install/windows-install), or [Mac device](https://docs.docker.com/desktop/setup/install/mac-install)

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

<img width="1366" height="768" alt="noknow-desktop-1" src="https://github.com/user-attachments/assets/57c7a9c2-7607-4af7-addf-6deb1eba3495" />
<img width="1366" height="768" alt="noknow-mobile-1" src="https://github.com/user-attachments/assets/05df968d-e257-4518-8f72-a833b90a752d" />
<img width="1366" height="768" alt="noknow-desktop-2" src="https://github.com/user-attachments/assets/c224c859-3eee-4d86-a0f9-72fb516ba455" />
<img width="1366" height="768" alt="noknow-mobile-2" src="https://github.com/user-attachments/assets/f646459f-cd81-4e84-96d8-5b7e644b374c" />
<img width="1366" height="768" alt="noknow-desktop-3" src="https://github.com/user-attachments/assets/744369dd-f08c-4806-8d96-326b905adf9d" />
<img width="1366" height="768" alt="noknow-mobile-3" src="https://github.com/user-attachments/assets/9d0b9169-24b7-45dc-951e-8a16874ac6c0" />
<img width="1366" height="768" alt="noknow-desktop-4" src="https://github.com/user-attachments/assets/92a26a72-66fe-4932-afbf-e45761613dc0" />
<img width="1366" height="768" alt="noknow-mobile-4" src="https://github.com/user-attachments/assets/c7fd836b-51ac-4abc-940d-ce66813c5076" />
<img width="1366" height="768" alt="noknow-desktop-5" src="https://github.com/user-attachments/assets/b89df01d-f974-4fb0-b985-0349dfed92b3" />
<img width="1366" height="768" alt="noknow-mobile-5" src="https://github.com/user-attachments/assets/ea993485-1983-4c72-9973-c7fc0b90d317" />
<img width="1366" height="768" alt="noknow-desktop-6" src="https://github.com/user-attachments/assets/f4383597-050f-4b2d-abd7-455d50d2a665" />
<img width="1366" height="768" alt="noknow-mobile-6" src="https://github.com/user-attachments/assets/b8f9eb0a-f400-414e-9d27-4b932d2a07ce" />
<img width="1366" height="768" alt="noknow-desktop-7" src="https://github.com/user-attachments/assets/500f15c6-09ee-4eae-b866-e11b219bbdba" />
<img width="1366" height="768" alt="noknow-mobile-7" src="https://github.com/user-attachments/assets/2f3acacc-4c47-4254-bd4e-21f8092631c9" />
<img width="1366" height="768" alt="noknow-desktop-8" src="https://github.com/user-attachments/assets/49af64da-6357-434f-a65b-b027583bbaf1" />
<img width="1366" height="768" alt="noknow-mobile-8" src="https://github.com/user-attachments/assets/3c664d65-6173-4989-a7b1-97cc01f98d26" />
<img width="1366" height="768" alt="noknow-desktop-9" src="https://github.com/user-attachments/assets/6984a79a-ac00-4d5f-948c-750188b78aa8" />
<img width="1366" height="768" alt="noknow-mobile-9" src="https://github.com/user-attachments/assets/630f22b8-e7f7-4877-8610-57e792e2f398" />
<img width="1366" height="768" alt="noknow-desktop-10" src="https://github.com/user-attachments/assets/c1c592e1-7b59-4ee5-88b7-4f5eba0bb60e" />
<img width="1366" height="768" alt="noknow-mobile-10" src="https://github.com/user-attachments/assets/5511fc8c-9c70-4a0d-9589-4929fac91252" />
