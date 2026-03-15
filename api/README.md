
# NOKNOW - ABOUT
This is the REST API for NoKnow; a realtime live chatting web application.

API usage requires no signup (with limitations) for accessing basic features such as creating & engaging public chatrooms,
however more advanced features are unlocked for signed-up/authenticated users, such as
creating/engaging private password protected chatrooms, fully private unrecorded chats,
assigning moderators and successors to owned chatrooms, banning offenders from owned chatrooms, adding friends,
and adding friends to chatrooms.

Logged-in/authenticated users can hide their presence and remain fully anonymous as if logged out,
As the core purpose behind this application is to offer community in anonymity

# FEATURES
- User signup and login
- JWT Authorization and authentication
- Oauth2 authentication
- Live data sharing via websockets
- No-signup, straight to use (with limitations)
- Fully unrecorded conversations for logged-in/authenticated users
- Admin content management system

# TECH STACK
- Python
- FastApi
- UV
- Pydantic
- Alembic
- Postgresql
- SqlAlchemy & SqlModel
- Uvicorn

# INSTALLATION

## FOR LOCAL
- Fork & clone this repository to your local machine
- If you don't have `UV` installed, go to the official [uv](https://docs.astral.sh/uv/) website for a proper guide
- Inside the project folder containing 
- With UV package manager, install app dependencies by running
    ```bash
        uv sync
    ```
- Ensure that your text editor has the correct python interpreter in the newly created virtual environment
- Initialise database with command:
    ```bash
        alembic upgrade head
    ```
- For Email features to work:
    - Open a new terminal and start a celery worker by running:
    ```bash
        celery -A src.services.celery.celery_app worker
    ```
    - Activate a redis container in docker to be used by celery
- Run tests before any modifications to be sure that everything works with the command:
    ```bash
        pytest -x -v
    ```
- Run server with command:
    ```bash
        uvicorn src.main:app --reload
    ```
## FOR DOCKER
- Fork & clone this repository to your local machine
- Make sure you have Docker running on your local machine
- Inside project folder containing `Dockerfile`, run
    ```bash
        docker build -t noknow:clone -f .
    ```