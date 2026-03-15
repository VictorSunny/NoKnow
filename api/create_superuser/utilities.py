import os
from typing import Callable

from src.db.models import BlacklistedEmail, User
from src.apps.auth.schemas.base_schemas import EmailForm
from src.utilities.utilities import check_password_strength
from sqlalchemy.orm import Session
from sqlalchemy import select


def check_is_alpha(user_input: str, recursive_function: Callable, field_name: str):
    if not user_input.isalpha():
        os.system("cls")
        print("enter only letters.")
        return recursive_function(field_name)
    return str(user_input).strip()


def check_username(user_input: str, recursive_function: Callable, db: Session):
    if not user_input.isalpha() and not user_input.isalnum():
        os.system("cls")
        print("enter a combination of letters and numbers, or only letters")
        return recursive_function(db)

    user_input = user_input.lower().strip()

    # reject if user with matching username exists in database
    query = select(User).where(User.username == user_input)
    executed_query = db.execute(query)
    user_using_username = executed_query.scalar_one_or_none()
    if user_using_username:
        os.system("cls")
        print("username is already taken by an existing account.")
        return recursive_function(db)


def check_password(user_input: str, recursive_function: Callable):
    password_strength = check_password_strength(password=user_input)
    if not password_strength.get("strong"):
        os.system("cls")
        print(password_strength.get("message"))
        return recursive_function()
    return str(user_input).strip()


def confirm_password(user_input: str, password: str, recursive_function: Callable):
    if user_input != password:
        os.system("cls")
        print("passwords do not match")
        return recursive_function(password)
    return str(user_input).strip()


def check_email(user_input: str, recursive_function: Callable, db: Session):
    user_input = user_input.strip()
    try:
        email_validate = EmailForm(email=user_input)
    except:
        os.system("cls")
        print("enter a valid email address.")
        return recursive_function(db)

    # reject if user with matching email exists in database
    query = select(User).where(User.email == user_input)
    executed_query = db.execute(query)
    user_using_email = executed_query.scalar_one_or_none()
    if user_using_email:
        os.system("cls")
        print("email is already connected to an existing account.")
        return recursive_function(db)

    # reject if user email is blacklisted in database
    query = select(BlacklistedEmail).where(BlacklistedEmail.sub == user_input)
    executed_query = db.execute(query)
    email_in_blacklist = executed_query.scalar_one_or_none()
    if email_in_blacklist:
        os.system("cls")
        print("This email is blacklisted.")
        return recursive_function(db)

    return user_input


def enter_alpha(field_name: str):
    user_input = check_is_alpha(
        input(f"Enter {field_name}:\n"), enter_alpha, field_name
    )
    return str(user_input)


def enter_username(db: Session):
    user_input = check_username(input(f"Enter username:\n"), enter_username, db=db)
    return str(user_input)


def enter_password():
    user_input = check_password(input(f"Enter password:\n"), enter_password)
    return str(user_input)


def enter_email(db):
    user_input = check_email(input(f"Enter email:\n"), enter_email, db)
    return str(user_input)


def enter_password_confirmation(password):
    user_input = confirm_password(
        input("Confirm password:\n"),
        password=password,
        recursive_function=enter_password_confirmation,
    )
    return user_input
