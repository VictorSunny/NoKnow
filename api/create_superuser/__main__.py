import json
from pathlib import Path

from src.apps.user.schemas.base_schemas import UserPrivate, UserRoleChoices
from src.configurations.apps_config.config import DATABASE_URL
from create_superuser.utilities import (
    enter_username,
    enter_alpha,
    enter_email,
    enter_password,
    enter_password_confirmation,
)

from src.utilities.utilities import hash_password
from src.db.models import User
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker


engine = create_engine(DATABASE_URL, echo=False)
Session = sessionmaker(bind=engine)


def create_superuser():
    with Session() as db:
        first_name = enter_alpha("first name")
        last_name = enter_alpha("last name")
        username = enter_username(db=db)
        email = enter_email(db=db)
        password = enter_password()
        enter_password_confirmation(password)
        bio = "this user is a superuser"

        hashed_password = hash_password(password=password)
        try:
            new_superuser = User(
                first_name=first_name,
                last_name=last_name,
                username=username,
                email=email,
                password=hashed_password,
                bio=bio,
                is_hidden=True,
                role=UserRoleChoices.SUPERUSER,
            )
            db.add(new_superuser)
            db.commit()
            db.refresh(new_superuser)
        except Exception as e:
            print("an error occured creating superuser.", e)
        user_details = UserPrivate(**new_superuser).model_dump_json()
        user_details = json.loads(user_details)
    result = {"message": "success", "user": user_details}
    print(result)


if __name__ == "__main__":
    create_superuser()
