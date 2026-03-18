# NOKNOW

## ABOUT

This is the backend client for NoKnow; a realtime live chatting web application.

API usage requires no signup (with limitations) for accessing basic features such as creating & engaging public chatrooms,
however more advanced features are unlocked for signed-up/authenticated users, such as
creating/engaging private password protected chatrooms, fully private unrecorded chats,
assigning moderators and successors to owned chatrooms, banning offenders from owned chatrooms, adding friends,
and adding friends to chatrooms.

Logged-in/authenticated users can hide their presence and remain fully anonymous as if logged out,
As the core purpose behind this application is to offer community in anonymity

## FEATURES

- User signup and login.
- No-signup, straight to use (with limitations).
- JWT authentication and authorization.
- Oauth2 authentication (Google).
- Websockets for live data sharing via.
- Fully unrecorded conversations for logged-in/authenticated users.
- Admin content management system.

## TECH STACK

- Python
- FastApi
- UV
- Pydantic
- Alembic
- Postgresql
- SqlAlchemy & SqlModel
- Uvicorn

## Environment variables

- `DEBUG`

- `SECRET_KEY`
- `HASHING_ALGORITHM`

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

## INSTALLATION

- Fork & clone this repository to your local machine.

- Set the necessary environment variables.

- If you don't have `UV` installed, go to the official [uv](https://docs.astral.sh/uv/) website for a proper installation guide.

- To install dependencies:

  - With UV as package manager, install from `pyproject.toml` & `uv.lock` files, by running:

```bash
  python -m uv sync --locked
```

This will automatically create a .venv environment folder, which you then activate by running:

- for Windows:

```bash
  python -m .venv/scripts/activate
```

- for Linux/Mac:

```bash
  python -m .venv/bin/activate
```

- With Pip as package manager, firstly create a virtual environment named `.venv` by running:

```bash
  python -m venv .venv
```

Activate the virtual environment by running:

- for Windows:

```bash
  python -m .venv/scripts/activate
```

- for Linux/Mac:

```bash
python -m .venv/bin/activate
```

- Install dependencies by running:

```bash
  python -m pip install -r requirements.txt
```

- Ensure that your text editor has the correct python interpreter set
  (i.e intepreter in the newly created virtual environment.)
- Initialise database with command:

```bash
  python -m alembic -c alembic.ini upgrade head
```

- Start a redis server (preferably in Docker with an exposed port) and configure the `REDIS_URL` environment variable accordingly.
  The redis server will be used as a broker and result back-end by celery, which handles email tasks.
- Start a postgresql server (preferably in Docker with an exposed port) and configure the nessary posgres environment variables accordingly.
- Open a new terminal and start a celery worker by running:

```bash
  python -m celery -A src.services.celery.celery_app worker
```

- Finally, run server with command:

```bash
  python -m uvicorn src.main:app --reload
```

## TESTS

Tests are written as methods of classes.
A test class may inherit from a parent test class having a name starting with 'Base'.
The inherited parent class' tests run before the child class' tests. 
This is needed to set up for integration tests and to avoid tests running repeatedly e.g initial run, then rerunning when inherited by another test classes.

### Test classes inheritance tree

- BaseTestAdminUserAndTokenBlacklisting -> TestAdminChat
- BaseTestUserSignupLogin -> BaseTestUserIntegrations -> TestPrivateChatroomAndMessagingFeatures

### Standalone test classes

- TestPublicChatroomAndMessagingFeatures

### Running tests

- Start a redis server (preferably in Docker with an exposed port), properly configure your `REDIS_URL` value in root project '.env' file,
  enter the following pytest command to run tests (extra optional flags stop the test at the earliest failure)

```bash
python -m pytest -x -v
```

- Test coverage folder 'htmlcov' is initialized after each test (configured in 'pytests.ini' file).
- View the 'htmlcov/index.html' file in a browser to see your test coverage and other related information.

### Project Structure
The backend code is structured as follows:

* `api/.app_folder_template` - Template for creating new app in line with project style.

* `api/.migrations` - Alembic migrations folder.

* `api/create_superuser` - Module   for creating superuser account via CLI.

* `api/src/src` - Main backend code.

* `api/src/apps` - Distinct routes and controllers.

* `api/src/configurations` - Runtime configurations.

* `api/src/db` - Setup for databases.

* `api/src/exceptions` - Utility functions for raising various errors.

* `api/src/generics` - Usable code used across the application.

* `api/src/services` - Background/in-memory services.

* `api/src/templates` - Jinja2 HTML templates.

* `api/src/tests` - Contains configuration code for test environment and fixtures.

* `api/src/utilities` - Callable functions.
