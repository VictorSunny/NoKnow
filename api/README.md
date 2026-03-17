# NOKNOW

## ABOUT

This is the REST API for NoKnow; a realtime live chatting web application.

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

## INSTALLATION

### FOR DOCKER

- Fork & clone this repository to your local machine
- Make sure you have Docker running on your local machine
- Inside project folder containing `Dockerfile`, run
  ```bash
  docker build -t noknow:clone -f .
  ```
- Activate the virtual environment by running:
  - for Windows:
  ```bash
  python -m .venv/scripts/activate
  ```
  - for Linux/Mac:
  ```bash
  python -m .venv/bin/activate
  ```

### FOR LOCAL

- Fork & clone this repository to your local machine.
- If you don't have `UV` installed, go to the official [uv](https://docs.astral.sh/uv/) website for a proper installation guide.
- To install dependencies:
  - With UV as package manager, install from `pyproject.toml` & `uv.lock` files, by running:
    ```bash
    python -m uv sync --locked
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
    Finally, install dependencies by running:
    ```bash
      python -m pip install -r requirements.txt
    ```
- Ensure that your text editor has the correct python interpreter set
  (i.e intepreter in the newly created virtual environment.)
- Initialise database with command:
  ```bash
    python -m alembic -c alembic.ini upgrade head
  ```
- Start a redis server (preferably in Docker) and configure the `REDIS_URL` environment variable accordingly.
  The redis server will be used as a broker and result backend by celery, which handles email tasks.
- Open a new terminal and start a celery worker by running:
  ```bash
  python -m celery -A src.services.celery.celery_app worker
  ```
- Run server with command:
  ```bash
  python -m uvicorn src.main:app --reload
  ```

## TESTS

Tests are written as methods of classes.
A test class may inherit from a parent test class having a name starting with 'Base'.
This is needed for the sake of integration tests and to avoid tests running repeatedly e.g initial run, then rerunning when inherited by other test classes.

### Test classes inheritance tree

- BaseTestAdminUserAndTokenBlacklisting -> TestAdminChat
- BaseTestUserSignupLogin -> BaseTestUserIntegrations -> TestPrivateChatroomAndMessagingFeatures

### Standalone test classes

- TestPublicChatroomAndMessagingFeatures

### Running tests

- With an active redis server (preferably in Docker with an exposed port), then properly configured `REDIS_URL` value in root project '.env' file,
  enter the following pytest command to run tests (extra optional flags stop the test at the earliest failure)
  ```bash
  python -m pytest -x -v
  ```
- Test coverage folder 'htmlcov' is initialized after each test (configured in 'pytests.ini' file).
- View the 'htmlcov/index.html' file in a browser to see your test coverage and other related information.
