from datetime import datetime, timedelta, timezone
import email
from uuid import UUID, uuid4
import pytest
from regex import F
from sqlmodel import select, func

from api.src.configurations.config import Config
from src.db.models import BlacklistedEmail, BlacklistedToken, User
from src.utilities.utilities import check_password, hash_password
from src.apps.auth.tests.base_test_user_signup_login_jwt import BaseTestUserSignupLogin
from src.tests.conftest import test_client, r_client, test_session
from fastapi import status


EXPENDABLE_USER_FIRST_NAME_KEYWORD = "man"


class BaseTestAdminUserAndTokenBlacklisting:
    @classmethod
    def setup_class(self):
        self.all_users_password = "comPl3x-passw0rd"
        self.all_users_password_confirm = self.all_users_password

        self.SUPERUSER_PASSWORD = "Sup3rU$er"

        self.goodman_user_uids = dict()
        self.goodman_user_emails = dict()
        self.goodman_user_access_tokens = dict()
        self.goodman_users_uid_list = list()
        self.goodman_users_email_list = list()

        self.superuser_create_data = {
            "first_name": "super",
            "last_name": "user",
            "username": "superuser001",
            "email": "super@user.com",
            "confirm_password": self.all_users_password_confirm,
            "bio": "user one is a superuser",
        }

        self.admin_user_create_data = {
            "first_name": "admin",
            "last_name": "one",
            "username": "admin1",
            "email": "admin@one.com",
            "password": self.all_users_password,
            "confirm_password": self.all_users_password_confirm,
            "bio": "admin user. this bio has to be at least 25 characters long",
            "role": "admin",
            "active": "True",
            "is_hidden": "False",
            "is_two_factor_authenticated": "False",
        }

        self.goodman_user_create_data = {
            "first_name": EXPENDABLE_USER_FIRST_NAME_KEYWORD,
            "last_name": "man",
            "password": self.all_users_password,
            "confirm_password": self.all_users_password_confirm,
            "role": "user",
            "bio": "normal user. this bio has to be at least 25 characters long",
            "active": "True",
            "is_hidden": "True",
            "is_two_factor_authenticated": "False",
        }

        self.expected_user_complete_data_keys = {
            "uid",
            "first_name",
            "last_name",
            "username",
            "bio",
            "joined",
            "active",
            "is_hidden",
            "is_two_factor_authenticated",
            "email",
            "role",
            "last_seen",
            "online",
        }

    async def test_user_setup(self, test_client, test_session):
        """
        set up data to be used across tests' post requests
        """
        # password over 8 characters, containing uppercase, lowercase, numeric, and special characters

        # superuser can only be created in cli
        parsed_password = hash_password(self.SUPERUSER_PASSWORD)
        new_superuser = User(
            first_name=self.superuser_create_data["first_name"],
            last_name=self.superuser_create_data["last_name"],
            username=self.superuser_create_data["username"],
            email=self.superuser_create_data["email"],
            password=parsed_password,
            bio=self.superuser_create_data["bio"],
            is_hidden=True,
            role="superuser",
        )
        test_session.add(new_superuser)
        await test_session.commit()
        await test_session.refresh(new_superuser)

        # confirm that superuser exists
        # login superuser
        post_login_superuser_response = test_client.post(
            "/admin/auth/login",
            json={
                "email": self.superuser_create_data["email"],
                "password": self.SUPERUSER_PASSWORD,
            },
        )
        assert post_login_superuser_response.status_code == 200
        assert "refresh_token" in post_login_superuser_response.cookies
        login_superuser_json = post_login_superuser_response.json()

        self.__class__.superuser_access_token = login_superuser_json.get("access_token")

        # confirm user details
        get_superuser_details_after_login_response = test_client.get(
            "/user",
            headers={"Authorization": f"Bearer {self.superuser_access_token}"},
        )
        assert get_superuser_details_after_login_response.status_code == 200
        superuser_uid = get_superuser_details_after_login_response.json().get("uid")
        assert superuser_uid == str(new_superuser.uid)
        self.__class__.superuser_uid = superuser_uid

    def test_superuser_create_new_users(self, test_client):
        """
        test superuser user creation
        """

        for n in range(1, 6):
            # create user
            user_create_data = self.goodman_user_create_data.copy()
            user_create_data.update(
                {"email": f"good{n}@mail.com", "username": f"goodman{n}"}
            )
            post_superusuer_create_new_user_response = test_client.post(
                "/admin/user",
                headers={"Authorization": f"Bearer {self.superuser_access_token}"},
                json=user_create_data,
            )
            delnow = post_superusuer_create_new_user_response.json()
            assert post_superusuer_create_new_user_response.status_code == 201
            assert (
                post_superusuer_create_new_user_response.json().keys()
                == self.expected_user_complete_data_keys
            )
            new_user_json = post_superusuer_create_new_user_response.json()

            assert new_user_json.get("role") == "user"
            # confirm that user is active by default upon creation
            assert new_user_json.get("active") is True

            self.goodman_user_uids[new_user_json.get("username")] = new_user_json.get(
                "uid"
            )
            self.goodman_user_emails[new_user_json["username"]] = new_user_json.get(
                "email"
            )
            self.goodman_users_uid_list.append(new_user_json.get("uid"))
            self.goodman_users_email_list.append(new_user_json.get("email"))

            # try to login normal user through admin login endpoint
            # should fail as only admin users can login through admin endpoint
            post_goodman_user_login_through_admin_endpoint_failed_response = (
                test_client.post(
                    "/admin/auth/login",
                    json={
                        "email": new_user_json.get("email"),
                        "password": self.all_users_password,
                    },
                )
            )
            assert (
                post_goodman_user_login_through_admin_endpoint_failed_response.status_code
                == 403
            )

            # try to login normal user through normal login endpoint
            # should succeed as all users regardless of role can login through normal login endpoint
            post_goodman_user_login_response = test_client.post(
                "/auth/login",
                json={
                    "email": new_user_json.get("email"),
                    "password": self.all_users_password,
                },
            )
            assert post_goodman_user_login_response.status_code == 200
            self.goodman_user_access_tokens[new_user_json.get("username")] = (
                post_goodman_user_login_response.json().get("access_token")
            )

        self.__class__.goodman_one_access_token = self.goodman_user_access_tokens[
            "goodman1"
        ]
        self.__class__.goodman_two_access_token = self.goodman_user_access_tokens[
            "goodman2"
        ]
        self.__class__.goodman_three_access_token = self.goodman_user_access_tokens[
            "goodman3"
        ]
        self.__class__.goodman_four_access_token = self.goodman_user_access_tokens[
            "goodman4"
        ]
        self.__class__.goodman_five_access_token = self.goodman_user_access_tokens[
            "goodman5"
        ]

        self.__class__.goodman_one_uid = self.goodman_user_uids["goodman1"]
        self.__class__.goodman_two_uid = self.goodman_user_uids["goodman2"]
        self.__class__.goodman_three_uid = self.goodman_user_uids["goodman3"]
        self.__class__.goodman_four_uid = self.goodman_user_uids["goodman4"]
        self.__class__.goodman_five_uid = self.goodman_user_uids["goodman5"]

        ################################ LOGIN GOODMAN1 ########################################
        # logged in as goodman1
        # try to create a new user
        # should fail as only superuser can create new users

        goodman_user_create_data_copy = user_create_data.copy()
        goodman_user_create_data_copy.update(
            {"email": "random@mail.com", "username": "random22"}
        )
        post_create_user_as_goodman_one_response = test_client.post(
            "/admin/user",
            headers={"Authorization": f"Bearer {self.goodman_one_access_token}"},
            json=goodman_user_create_data_copy,
        )
        assert post_create_user_as_goodman_one_response.status_code == 403

        ################################ LOGOUT GOODMAN1 ########################################

        ################################ LOGIN SUPERUSER ########################################
        # test admin user creation
        post_superusuer_create_new_admin_user_response = test_client.post(
            "/admin/user",
            headers={"Authorization": f"Bearer {self.superuser_access_token}"},
            json=self.admin_user_create_data,
        )
        delnow = post_superusuer_create_new_admin_user_response.json()
        assert post_superusuer_create_new_admin_user_response.status_code == 201
        assert (
            post_superusuer_create_new_admin_user_response.json().keys()
            == self.expected_user_complete_data_keys
        )
        new_admin_user_json = post_superusuer_create_new_admin_user_response.json()
        # confirm created user role is admin
        assert new_admin_user_json.get("role") == "admin"

        self.__class__.admin_user_uid = new_admin_user_json.get("uid")

        # login admin user to get admin access token
        post_login_admin_user_response = test_client.post(
            "/admin/auth/login",
            json={
                "email": self.admin_user_create_data["email"],
                "password": self.admin_user_create_data["password"],
            },
        )
        assert post_login_admin_user_response.status_code == 200
        login_admin_user_json = post_login_admin_user_response.json()
        self.__class__.admin_one_access_token = login_admin_user_json.get(
            "access_token"
        )

        ################################ LOGOUT SUPERUSER ########################################

    def test_admin_user_details_route(self, test_client):

        ################################ LOGIN SUPERUSER ########################################
        # logged in as superuser
        # get complete user details for self
        # should work as user is an admin user - superuser
        get_superuser_complete_data_as_superuser_response = test_client.get(
            "/admin/user",
            headers={"Authorization": f"Bearer {self.superuser_access_token}"},
        )
        assert get_superuser_complete_data_as_superuser_response.status_code == 200
        assert (
            self.expected_user_complete_data_keys
            == get_superuser_complete_data_as_superuser_response.json().keys()
        )

        assert (
            get_superuser_complete_data_as_superuser_response.json().get("role")
            == "superuser"
        )
        assert (
            get_superuser_complete_data_as_superuser_response.json().get("uid")
            == self.superuser_uid
        )

        # get complete details for normal user - goodman1
        get_normal_goodman_one_user_complete_data_as_superuser_response = (
            test_client.get(
                f"/admin/user?id={self.goodman_one_uid}",
                headers={"Authorization": f"Bearer {self.superuser_access_token}"},
            )
        )
        assert (
            get_normal_goodman_one_user_complete_data_as_superuser_response.status_code
            == 200
        )
        assert (
            self.expected_user_complete_data_keys
            == get_normal_goodman_one_user_complete_data_as_superuser_response.json().keys()
        )
        assert (
            get_normal_goodman_one_user_complete_data_as_superuser_response.json().get(
                "role"
            )
            == "user"
        )
        assert (
            get_normal_goodman_one_user_complete_data_as_superuser_response.json().get(
                "uid"
            )
            == self.goodman_one_uid
        )

        ################################ LOGOUT SUPERUSER ########################################

        ################################ LOGIN GOODMAN1 ########################################
        # logged in as goodman1
        # try to call admin user details endpoint
        # should fail as only admins can access complete user details endpoint
        get_user_complete_data_as_goodman1_response = test_client.get(
            f"/admin/user?id={self.goodman_one_uid}",
            headers={"Authorization": f"Bearer {self.goodman_one_access_token}"},
        )
        assert get_user_complete_data_as_goodman1_response.status_code == 403

        ################################ LOGOUT GOODMAN1 ########################################

    def test_admin_get_all_users_route(self, test_client):
        """
        test admin get all users route
        """
        ################################ LOGIN SUPERUSER ########################################
        # logged in as superuser
        # get all created users
        get_all_created_users_as_admin_user_superuser_response = test_client.get(
            "/admin/user/all",
            headers={"Authorization": f"Bearer {self.superuser_access_token}"},
        )
        assert get_all_created_users_as_admin_user_superuser_response.status_code == 200
        all_created_users_json = (
            get_all_created_users_as_admin_user_superuser_response.json()
        )
        assert {"users"}.issubset(all_created_users_json.keys())
        all_users_list = all_created_users_json.get("users")
        # confirm that user list has at least one user
        assert len(all_users_list) > 0
        first_user_in_list = all_users_list[0]
        expected_user_details_json_keys = {
            "uid",
            "first_name",
            "last_name",
            "username",
            "bio",
            "joined",
            "last_seen",
            "online",
            "role"
        }
        assert first_user_in_list.keys() == expected_user_details_json_keys

        ################################ LOGOUT SUPERUSER ########################################

        ################################ LOGIN GOODMAN1 ########################################
        get_all_created_users_as_admin_user_goodman_one_response = test_client.get(
            "/admin/user/all",
            headers={"Authorization": f"Bearer {self.goodman_one_access_token}"},
        )
        assert (
            get_all_created_users_as_admin_user_goodman_one_response.status_code == 403
        )
        # logged in as goodman1
        # try to get all users via admin endpoint
        # should fail as goodman1 is not an admin

        ################################ LOGOUT GOODMAN1 ########################################

        ################################ LOGIN ADMIN1 ########################################
        # logged in as admin1
        # try to get all users via admin endpoint
        # should succeed as admin users can view all created users
        get_all_created_users_as_admin_user_admin_one_response = test_client.get(
            "/admin/user/all",
            headers={"Authorization": f"Bearer {self.admin_one_access_token}"},
        )
        assert get_all_created_users_as_admin_user_admin_one_response.status_code == 200
        ################################ LOGOUT ADMIN1 ########################################

    def test_mass_update_user_roles(self, test_client):
        """
        test mass update user roles
        """
        ################################ LOGIN SUPERUSER ########################################

        # get admin users to before adding users to admin group
        get_all_admin_users_before_adding_users = test_client.get(
            "/admin/user/all?role=admin",
            headers={"Authorization": f"Bearer {self.superuser_access_token}"},
        )
        assert get_all_admin_users_before_adding_users.status_code == 200
        admin_users_before_removing_goodman_one_and_goodman_two = (
            get_all_admin_users_before_adding_users.json().get("users")
        )

        # add goodman1 and goodman2 to admin
        patch_add_goodman_one_and_goodman_two_to_admin_group_as_superuser_response = test_client.patch(
            f"/admin/user/groups/admin/add?id={self.goodman_one_uid},{self.goodman_two_uid}",
            headers={"Authorization": f"Bearer {self.superuser_access_token}"},
        )
        assert (
            patch_add_goodman_one_and_goodman_two_to_admin_group_as_superuser_response.status_code
            == 200
        )

        # get admin users to after adding users to admin group
        get_all_admin_users_after_adding_users = test_client.get(
            "/admin/user/all?role=admin",
            headers={"Authorization": f"Bearer {self.superuser_access_token}"},
        )
        assert get_all_admin_users_after_adding_users.status_code == 200
        admin_users_after_adding_goodman_one_and_goodman_two = (
            get_all_admin_users_after_adding_users.json().get("users")
        )

        # confirm that admin users have increased by 2
        assert len(admin_users_after_adding_goodman_one_and_goodman_two) == (
            len(admin_users_before_removing_goodman_one_and_goodman_two) + 2
        )
        # confirm that the new admins are the users added by superuser
        for new_admin in admin_users_after_adding_goodman_one_and_goodman_two:
            new_admin_uid = new_admin.get("uid")
            assert new_admin_uid in [
                self.goodman_one_uid,
                self.goodman_two_uid,
                self.admin_user_uid,
            ]

        ################################ LOGOUT SUPERUSER ########################################

        ################################ LOGIN GOODMAN1 - NOW AN ADMIN ########################################
        # logged in as goodman1, now an admin
        # try to add goodman3 to admin group
        # should fail as only superuser can assign users to groups
        patch_add_goodman_three_to_admin_group_as_goodman_one = test_client.patch(
            f"/admin/user/groups/admin/add?id={self.goodman_three_uid}",
            headers={"Authorization": f"Bearer {self.goodman_one_access_token}"},
        )
        assert patch_add_goodman_three_to_admin_group_as_goodman_one.status_code == 403
        ################################ LOGOUT GOODMAN1 - NOW AN ADMIN ########################################

        ################################ LOGIN GOODMAN3 ########################################
        # logged in as goodman3 - normal user
        # try to add goodman4 to admin group
        # should fail as only superuser can assign users to groups
        patch_add_goodman_four_to_admin_group_as_goodman_three = test_client.patch(
            f"/admin/user/groups/admin/add?id={self.goodman_four_uid}",
            headers={"Authorization": f"Bearer {self.goodman_three_access_token}"},
        )
        assert patch_add_goodman_four_to_admin_group_as_goodman_three.status_code == 403
        ################################ LOGOUT GOODMAN1 - NOW AN ADMIN ########################################

        ################################ LOGIN SUPERUSER ########################################

        # get admin users from before removing users from admin group
        get_all_admin_users_before_removing_users = test_client.get(
            "/admin/user/all?role=admin",
            headers={"Authorization": f"Bearer {self.superuser_access_token}"},
        )
        assert get_all_admin_users_before_removing_users.status_code == 200
        admin_users_before_removing_goodman_one_and_goodman_two = (
            get_all_admin_users_before_removing_users.json().get("users")
        )

        # remove goodman1 and goodman2 from admin
        patch_add_goodman_one_and_goodman_two_to_user_group_as_superuser_response = test_client.patch(
            f"/admin/user/groups/user/add?id={self.goodman_one_uid},{self.goodman_two_uid}",
            headers={"Authorization": f"Bearer {self.superuser_access_token}"},
        )
        assert (
            patch_add_goodman_one_and_goodman_two_to_user_group_as_superuser_response.status_code
            == 200
        )

        # get admin users from after removing users from admin group
        get_all_admin_users_after_removing_goodman_one_and_goodman_two = (
            test_client.get(
                "/admin/user/all?role=admin",
                headers={"Authorization": f"Bearer {self.superuser_access_token}"},
            )
        )
        assert (
            get_all_admin_users_after_removing_goodman_one_and_goodman_two.status_code
            == 200
        )
        admin_users_after_removing_goodman_one_and_goodman_two = (
            get_all_admin_users_after_removing_goodman_one_and_goodman_two.json().get(
                "users"
            )
        )

        # confirm that admin users have decreased by 2
        assert len(admin_users_after_removing_goodman_one_and_goodman_two) == (
            len(admin_users_before_removing_goodman_one_and_goodman_two) - 2
        )
        # confirm that the new admins are the users removeed by superuser
        for admin_user in admin_users_after_removing_goodman_one_and_goodman_two:
            admin_uid = admin_user.get("uid")
            assert admin_uid not in [self.goodman_one_uid, self.goodman_two_uid]

        ################################ LOGOUT SUPERUSER ########################################

    def test_update_user_basic_updates(self, test_client):
        """
        test user first name, last name, email, username, bio, email, and role update via user update endpoint using update form
        """
        new_first_name = "first"
        new_last_name = "last"
        new_email = "gooman@newemail.com"
        new_username = "goodman3changed"
        new_bio = "new bio. bio must be at least 25 characters long"

        ##### GOODMAN3 WILL BE THE SUBJECT TO UPDATE IN TEST
        ##### WITH ATTEMPTS FROM SUPERUSER, ADMIN USER, AND NORMAL USER

        ################################ LOGIN ADMIN ########################################
        # get goodman3 data
        get_goodman_three_complete_data_as_admin_user_response = test_client.get(
            f"/admin/user?id={self.goodman_three_uid}",
            headers={"Authorization": f"Bearer {self.admin_one_access_token}"},
        )
        assert get_goodman_three_complete_data_as_admin_user_response.status_code == 200
        goodman_three_data_before_updates = (
            get_goodman_three_complete_data_as_admin_user_response.json()
        )
        new_is_hidden = not goodman_three_data_before_updates.get("is_hidden")

        patch_goodman_three_data_with_no_changes_as_admin_user_failed_response = (
            test_client.patch(
                f"/admin/user/?id={self.goodman_three_uid}",
                headers={"Authorization": f"Bearer {self.admin_one_access_token}"},
                json=goodman_three_data_before_updates,
            )
        )
        s = (
            patch_goodman_three_data_with_no_changes_as_admin_user_failed_response.json()
        )
        assert (
            patch_goodman_three_data_with_no_changes_as_admin_user_failed_response.status_code
            == 422
        )
        # try to update goodman3 details with new role
        # should fail as only admin has the privilege to update roles
        update_role_data = goodman_three_data_before_updates.copy()
        update_role_data.update({"role": "admin"})
        patch_goodman_three_role_data_update_as_admin_user_failed_response = (
            test_client.patch(
                f"/admin/user/?id={self.goodman_three_uid}",
                headers={"Authorization": f"Bearer {self.admin_one_access_token}"},
                json=update_role_data,
            )
        )
        assert (
            patch_goodman_three_role_data_update_as_admin_user_failed_response.status_code
            == 403
        )

        # update goodman3 basic details
        json_without_role = goodman_three_data_before_updates.copy()
        json_without_role.update(
            {
                "first_name": new_first_name,
                "last_name": new_last_name,
                "username": new_username,
                "email": new_email,
                "bio": new_bio,
                "is_hidden": new_is_hidden,
            }
        )
        patch_goodman_three_data_without_role_update_as_admin_user_success_response = (
            test_client.patch(
                f"/admin/user/?id={self.goodman_three_uid}",
                headers={"Authorization": f"Bearer {self.admin_one_access_token}"},
                json=json_without_role,
            )
        )
        assert (
            patch_goodman_three_data_without_role_update_as_admin_user_success_response.status_code
            == 200
        )
        goodman_three_data_from_update_response = (
            patch_goodman_three_data_without_role_update_as_admin_user_success_response.json()
        )
        assert (
            self.expected_user_complete_data_keys
            == goodman_three_data_from_update_response.keys()
        )

        # the response after update must be the new state user object
        # confirm fields are updated and correctly cased
        assert (
            goodman_three_data_from_update_response.get("first_name")
            == new_first_name.title()
        )
        assert (
            goodman_three_data_from_update_response.get("last_name")
            == new_last_name.title()
        )
        assert (
            goodman_three_data_from_update_response.get("username")
            == new_username.lower()
        )
        assert goodman_three_data_from_update_response.get("email") == new_email.lower()
        assert goodman_three_data_from_update_response.get("bio") == new_bio

        # get goodman3 details via user details endpoint
        # to confirm that update endpoint does not just return updated state, and to confirm changes reflect in database
        get_goodman_three_data_after_update_response = test_client.get(
            f"/admin/user?id={self.goodman_three_uid}",
            headers={"Authorization": f"Bearer {self.admin_one_access_token}"},
        )
        assert get_goodman_three_data_after_update_response.status_code == 200
        goodman_three_data_after_update = (
            get_goodman_three_data_after_update_response.json()
        )

        assert (
            goodman_three_data_after_update.get("first_name") == new_first_name.title()
        )
        assert goodman_three_data_after_update.get("last_name") == new_last_name.title()
        assert goodman_three_data_after_update.get("username") == new_username.lower()
        assert goodman_three_data_after_update.get("email") == new_email.lower()
        assert goodman_three_data_after_update.get("bio") == new_bio

        ################################ LOGOUT ADMIN ########################################

        ################################ LOGIN SUPERUSER ########################################
        # logged in as superuser
        # revert updates on goodman3 account via the same user update endpoint to confirm superuser is permitted to access the endpoint
        patch_reset_goodman_three_data_to_original_response = test_client.patch(
            f"/admin/user/?id={self.goodman_three_uid}",
            headers={"Authorization": f"Bearer {self.superuser_access_token}"},
            json=goodman_three_data_before_updates,
        )
        assert patch_reset_goodman_three_data_to_original_response.status_code == 200
        assert (
            patch_reset_goodman_three_data_to_original_response.json().keys()
            == goodman_three_data_before_updates.keys()
        )
        ################################ LOGOUT SUPERUSER ########################################

    def test_update_user_active_status_to_restrict_account(self, test_client):
        """
        test user active status update via user update endpoint using update form
        """
        goodman_three_email = self.goodman_user_emails.get("goodman3")

        ########        ########        ########        ########        ########
        # SUPERUSER ACTIVE STATUS UPDATE FOR GOODMAN3##
        ################################ LOGIN ADMIN ########################################
        # try to update goodman3 active status
        # should succeed as admin users and superuser possess privilege

        # users are acitve by default so to update, active status will be turned off - to false
        patch_goodman_three_active_status_response = test_client.patch(
            f"/admin/user/?id={self.goodman_three_uid}",
            headers={"Authorization": f"Bearer {self.admin_one_access_token}"},
            json={"active": "false"},
        )
        rr = patch_goodman_three_active_status_response.json()
        assert patch_goodman_three_active_status_response.status_code == 200
        assert patch_goodman_three_active_status_response.json().get("active") is False
        ################################ LOGOUT ADMIN ########################################

        ################################ LOGIN GOODMAN3 ########################################
        # try to access protected route to retrieve goodman3 user details
        # should fail as user active status is now false, account has been restricted
        get_goodman_three_info_as_goodman_three_after_account_restricted_failed_response = test_client.get(
            "/user",
            headers={"Authorization": f"Bearer {self.goodman_three_access_token}"},
        )
        assert (
            get_goodman_three_info_as_goodman_three_after_account_restricted_failed_response.status_code
            == 403
        )

        # try to login to account
        # should fail as user active status is now false, account has been restricted
        post_login_goodman_three_after_account_got_restricted_by_admin = (
            test_client.post(
                "/auth/login",
                json={
                    "email": goodman_three_email,
                    "password": self.all_users_password,
                },
            )
        )
        assert (
            post_login_goodman_three_after_account_got_restricted_by_admin.status_code
            == 403
        )
        ################################ LOGOUT GOODMAN3 ########################################

        ################################ LOGIN SUPERUSER ########################################
        # logged in as superuser
        # reset goodman3 active status
        # should succeed as superuser has privilege to perform this action
        patch_reset_goodman_three_active_status_to_defalt_true_as_superuser_response = (
            test_client.patch(
                f"/admin/user/?id={self.goodman_three_uid}",
                headers={"Authorization": f"Bearer {self.superuser_access_token}"},
                json={"active": "true"},
            )
        )
        assert (
            patch_reset_goodman_three_active_status_to_defalt_true_as_superuser_response.status_code
            == 200
        )

        # confirm goodman3 is now active
        get_goodman_three_info_after_superuser_reset_response = test_client.get(
            f"/admin/user?id={self.goodman_three_uid}",
            headers={"Authorization": f"Bearer {self.superuser_access_token}"},
        )
        assert get_goodman_three_info_after_superuser_reset_response.status_code == 200
        goodman_three_active_status_after_reset = (
            get_goodman_three_info_after_superuser_reset_response.json().get("active")
        )
        assert goodman_three_active_status_after_reset is True
        ################################ LOGOUT SUPERUSER ########################################

        # END OF SUPERUSER ACTIVE STATUS UPDATE FOR GOODMAN3##
        ########        ########        ########        ########        ########

    def test_user_password_update_via_update_endpoint(self, test_client):
        """
        test user password update via user update endpoint using update form
        """
        goodman_three_email = self.goodman_user_emails.get("goodman3")
        goodman_three_old_password = self.all_users_password
        goodman_three_new_password = "Bcda@1234"
        ########        ########        ########        ########        ########
        # ADMIN USER PASSWORD UPDATE FOR GOODMAN3##
        ######################################

        ################################ LOGIN GOODMAN3 ########################################
        # logged in as goodman3
        # login with original password before admin updates password
        # should succeed as password has not changed
        post_login_goodman_three_with_old_password_before_change_response = (
            test_client.post(
                "/auth/login",
                json={
                    "email": goodman_three_email,
                    "password": goodman_three_old_password,
                },
            )
        )
        assert (
            post_login_goodman_three_with_old_password_before_change_response.status_code
            == 200
        )
        ################################ LOGOUT GOODMAN3 ########################################

        ################################ LOGIN ADMIN ########################################
        # try to update goodman3 password
        # should succeed as admin users and superuser possess privilege
        patch_goodman_three_password_update_without_confirm_password_as_admin_failed_response = test_client.patch(
            f"/admin/user/?id={self.goodman_three_uid}",
            headers={"Authorization": f"Bearer {self.admin_one_access_token}"},
            json={"password": goodman_three_new_password},
        )
        delnow = (
            patch_goodman_three_password_update_without_confirm_password_as_admin_failed_response.json()
        )
        assert (
            patch_goodman_three_password_update_without_confirm_password_as_admin_failed_response.status_code
            == 422
        )

        patch_goodman_three_password_update_with_incorrect_confirm_password_as_admin_failed_response = test_client.patch(
            f"/admin/user/?id={self.goodman_three_uid}",
            headers={"Authorization": f"Bearer {self.admin_one_access_token}"},
            json={
                "password": goodman_three_new_password,
                "confirm_password": "inc0RRectConfirmpa$$word",
            },
        )
        assert (
            patch_goodman_three_password_update_with_incorrect_confirm_password_as_admin_failed_response.status_code
            == 422
        )

        patch_goodman_three_password_update_with_correct_confirm_password_as_admin_success_response = test_client.patch(
            f"/admin/user/?id={self.goodman_three_uid}",
            headers={"Authorization": f"Bearer {self.admin_one_access_token}"},
            json={
                "password": goodman_three_new_password,
                "confirm_password": goodman_three_new_password,
            },
        )
        assert (
            patch_goodman_three_password_update_with_correct_confirm_password_as_admin_success_response.status_code
            == 200
        )
        ################################ LOGOUT ADMIN ########################################

        ################################ LOGIN GOODMAN3 ########################################
        # login with original password after admin updates password
        # should fail as password has been changed
        post_login_goodman_three_with_old_password_after_change_response = (
            test_client.post(
                "/auth/login",
                json={
                    "email": goodman_three_email,
                    "password": goodman_three_old_password,
                },
            )
        )
        assert (
            post_login_goodman_three_with_old_password_after_change_response.status_code
            == 401
        )

        # login with new password
        # should succeed to prove update was successful
        post_login_goodman_three_with_new_password_after_change_response = (
            test_client.post(
                "/auth/login",
                json={
                    "email": goodman_three_email,
                    "password": goodman_three_new_password,
                },
            )
        )
        assert (
            post_login_goodman_three_with_new_password_after_change_response.status_code
            == 200
        )
        ################################ LOGOUT GOODMAN3 ########################################

        # SUPERUSER RESET UPDATES FOR GOODMAN3##
        ################################ LOGIN SUPERUSER ########################################
        # logged in as superuser
        # update goodman3 password to original password
        # should succeed as superuser can update password
        patch_goodman_three_password_update_reset_as_superuser_response = (
            test_client.patch(
                f"/admin/user/?id={self.goodman_three_uid}",
                headers={"Authorization": f"Bearer {self.superuser_access_token}"},
                json={
                    "password": goodman_three_old_password,
                    "confirm_password": goodman_three_old_password,
                },
            )
        )
        assert (
            patch_goodman_three_password_update_reset_as_superuser_response.status_code
            == 200
        )
        patch_goodman_three_password_update_reset_as_superuser_response = (
            test_client.patch(
                f"/admin/user/?id={self.goodman_three_uid}",
                headers={"Authorization": f"Bearer {self.superuser_access_token}"},
                json={
                    "password": goodman_three_old_password,
                    "confirm_password": goodman_three_old_password,
                },
            )
        )
        assert (
            patch_goodman_three_password_update_reset_as_superuser_response.status_code
            == 200
        )
        ################################ LOGOUT SUPERUSER ########################################

        ################################ LOGIN GOODMAN3 ########################################
        # login with original password after admin updates password
        # confirms that superuser reset update took effect in db
        post_login_goodman_three_with_old_password_after_reset_response = (
            test_client.post(
                "/auth/login",
                json={
                    "email": goodman_three_email,
                    "password": goodman_three_old_password,
                },
            )
        )
        assert (
            post_login_goodman_three_with_old_password_after_reset_response.status_code
            == 200
        )
        ################################ LOGOUT GOODMAN3 ########################################

    def test_user_role_update_via_update_endpoint(self, test_client):
        """
        test user role update via user update endpoint using update form
        """
        goodman_three_email = self.goodman_user_emails.get("goodman3")

        ################################ LOGIN ADMIN ########################################
        # logged in as admin
        # try to update goodman3 role to admin
        # should fail as only superuser possesses the privilege
        patch_goodman_three_role_update_as_admin_failed_response = test_client.patch(
            f"/admin/user/?id={self.goodman_three_uid}",
            headers={"Authorization": f"Bearer {self.admin_one_access_token}"},
            json={"role": "admin"},
        )
        assert (
            patch_goodman_three_role_update_as_admin_failed_response.status_code == 403
        )
        ################################ LOGOUT ADMIN ########################################

        ################################ LOGIN SUPERUSER ########################################
        # logged in as superuser
        # try to update goodman3 role to superuser
        # should fail as this endpoint can only update to 'admin' or 'user' for updates
        patch_goodman_three_role_update_to_superuser_as_superuser_failed_response = (
            test_client.patch(
                f"/admin/user/?id={self.goodman_three_uid}",
                headers={"Authorization": f"Bearer {self.superuser_access_token}"},
                json={"role": "superuser"},
            )
        )
        assert (
            patch_goodman_three_role_update_to_superuser_as_superuser_failed_response.status_code
            == 422
        )

        # try to update goodman3 role to admin
        # should succeed as only superuser possesses the privilege
        patch_goodman_three_role_update_to_admin_as_superuser_success_response = (
            test_client.patch(
                f"/admin/user/?id={self.goodman_three_uid}",
                headers={"Authorization": f"Bearer {self.superuser_access_token}"},
                json={"role": "admin"},
            )
        )
        assert (
            patch_goodman_three_role_update_to_admin_as_superuser_success_response.status_code
            == 200
        )

        # confirm goodman3 role in dict is now admin
        get_goodman_three_info_after_role_update_response = test_client.get(
            f"/admin/user?id={self.goodman_three_uid}",
            headers={"Authorization": f"Bearer {self.superuser_access_token}"},
        )
        assert get_goodman_three_info_after_role_update_response.status_code == 200
        goodman_three_role_after_update = (
            get_goodman_three_info_after_role_update_response.json().get("role")
        )
        assert goodman_three_role_after_update == "admin"
        ################################ LOGOUT SUPERUSER ########################################

        ################################ LOGIN GOODMAN3 - NOW ADMIN USER ########################################
        # logged in as goodman3
        # login via admin login endpoint
        # should succeed to prove goodman3 role update was successful
        post_goodman_three_login_via_admin_endpoint_after_update_response = (
            test_client.post(
                "/admin/auth/login",
                json={
                    "email": goodman_three_email,
                    "password": self.all_users_password,
                },
            )
        )
        assert (
            post_goodman_three_login_via_admin_endpoint_after_update_response.status_code
            == 200
        )
        ################################ LOGOUT GOODMAN3 - NOW ADMIN USER ########################################

        ################################ LOGIN SUPERUSER ########################################
        # reset goodman3 role back
        patch_goodman_three_role_reset_to_user_as_superuser_success_response = (
            test_client.patch(
                f"/admin/user/?id={self.goodman_three_uid}",
                headers={"Authorization": f"Bearer {self.superuser_access_token}"},
                json={"role": "user"},
            )
        )
        assert (
            patch_goodman_three_role_reset_to_user_as_superuser_success_response.status_code
            == 200
        )
        ################################ LOGOUT SUPERUSER ########################################

    def test_add_user_to_superusers_group(self, test_client):
        """
        test adding user to superuser group via the specific superuser endpoint
        """

        ################################ LOGIN SUPERUSER ########################################
        # logged in as supeuser
        # try to add goodman3 to superusers without password
        # should fail as password form is required
        patch_add_goodman3_to_superusers_as_superuser_without_password_form_failed_response = test_client.post(
            f"/admin/user/groups/superuser/add?id={self.goodman_three_uid}",
            headers={"Authorization": f"Bearer {self.superuser_access_token}"},
        )
        patch_add_goodman3_to_superusers_as_superuser_without_password_form_failed_response.status_code == 422

        # try to add goodman3 to superusers with incorrect password
        # should fail as password is incorrect
        patch_add_goodman3_to_superusers_as_superuser_with_incorrect_password_failed_response = test_client.post(
            f"/admin/user/groups/superuser/add?id={self.goodman_three_uid}",
            headers={"Authorization": f"Bearer {self.superuser_access_token}"},
            json={"password": "wr0ng_7assword"},
        )
        patch_add_goodman3_to_superusers_as_superuser_with_incorrect_password_failed_response.status_code == 403

        # try to add goodman3 to superusers with correct password
        # should succeed as password is correct
        patch_add_goodman3_to_superusers_as_superuser_with_correct_password_success_response = test_client.post(
            f"/admin/user/groups/superuser/add?id={self.goodman_three_uid}",
            headers={"Authorization": f"Bearer {self.superuser_access_token}"},
            json={"password": self.SUPERUSER_PASSWORD},
        )
        patch_add_goodman3_to_superusers_as_superuser_with_correct_password_success_response.status_code == 200

        # try to add goodman3 to superusers again
        # should fail as goodman3 is already a superuser
        patch_add_goodman3_to_superusers_for_second_time_as_superuser_success_response = test_client.post(
            f"/admin/user/groups/superuser/add?id={self.goodman_three_uid}",
            headers={"Authorization": f"Bearer {self.superuser_access_token}"},
            json={"password": self.SUPERUSER_PASSWORD},
        )
        patch_add_goodman3_to_superusers_for_second_time_as_superuser_success_response.status_code == 422

        # confirm that goodman3 user role has updated to superuser
        get_goodman_three_data_after_to_confirm_superuser_role_response = (
            test_client.get(
                f"/admin/user?id={self.goodman_three_uid}",
                headers={"Authorization": f"Bearer {self.superuser_access_token}"},
            )
        )
        assert (
            get_goodman_three_data_after_to_confirm_superuser_role_response.status_code
            == 200
        )
        goodman_three_data_after_to_confirm_superuser_role = (
            get_goodman_three_data_after_to_confirm_superuser_role_response.json()
        )
        assert (
            goodman_three_data_after_to_confirm_superuser_role.get("role")
            == "superuser"
        )
        assert (
            goodman_three_data_after_to_confirm_superuser_role.get("is_hidden") is True
        )

        # try to update goodman3 data
        # should fail as goodman three is now a superuser
        # only a superuser can update their own data
        patch_superuser_update_goodman_three_data_failed_response = test_client.patch(
            f"/admin/user/?id={self.goodman_three_uid}",
            headers={"Authorization": f"Bearer {self.superuser_access_token}"},
            json={"first_name": "peter"},
        )
        assert (
            patch_superuser_update_goodman_three_data_failed_response.status_code == 403
        )
        ################################ LOGOUT SUPERUSER ########################################

        ################################ LOGIN GOODMAN4  - NORMAL USER ########################################
        # logged in as goodman4 try to add goodman5 to superusers
        # should fail as goodman4 is not a superuser
        patch_add_goodman_five_to_superusers_as_goodman_four_with_password_failed_response = test_client.post(
            f"/admin/user/groups/superuser/add?id={self.goodman_five_uid}",
            headers={"Authorization": f"Bearer {self.goodman_four_access_token}"},
            json={"password": self.all_users_password},
        )
        patch_add_goodman_five_to_superusers_as_goodman_four_with_password_failed_response.status_code == 403
        ################################ LOGOUT GOODMAN4 - NORMAL USER  ########################################

        ################################ LOGIN ADMIN ########################################
        # logged in as admin user try to add admin user to superusers
        # should fail as admin user is not a superuser
        patch_add_goodman_five_to_superusers_as_admin_user_with_password_failed_response = test_client.post(
            f"/admin/user/groups/superuser/add?id={self.goodman_five_uid}",
            headers={"Authorization": f"Bearer {self.admin_one_access_token}"},
            json={"password": self.all_users_password},
        )
        patch_add_goodman_five_to_superusers_as_admin_user_with_password_failed_response.status_code == 403
        ################################ LOGOUT ADMIN  ########################################

    def test_mass_user_account_restriction_and_unrestriction(self, test_client):
        """
        test mass user account activation endpoints. endpoints should activate/deactivate all users with queried comma seperated id list
        """
        # test mass account restriction for goodman4, and goodman5
        goodman_five_and_four_uids_list = [
            self.goodman_five_uid,
            self.goodman_four_uid,
        ]
        goodman_five_and_four_uids_list_string = ",".join(
            goodman_five_and_four_uids_list
        )

        ################## RESTRICT/DEACTIVATE
        ################################ LOGIN GOODMAN2 - NORMAL USER ########################################
        # logged in as goodman2 - normal user
        # try to mass restrict queried users
        # should fail as normal user does not possess the privilege
        patch_mass_users_deactivate_as_goodman_two_normal_user_failed_response = (
            test_client.patch(
                f"/admin/user/all/restrict?id={goodman_five_and_four_uids_list_string}",
                headers={"Authorization": f"Bearer {self.goodman_two_access_token}"},
            )
        )
        assert (
            patch_mass_users_deactivate_as_goodman_two_normal_user_failed_response.status_code
            == 403
        )
        ################################ LOGOUT GOODMAN2 - NORMAL USER ########################################

        ################################ LOGIN ADMIN ########################################
        # logged in as admin
        # try to mass restrict queried users
        # should fail as admin user does not possess the privilege
        patch_mass_users_deactivate_as_admin_user_failed_response = test_client.patch(
            f"/admin/user/all/restrict?id={goodman_five_and_four_uids_list_string}",
            headers={"Authorization": f"Bearer {self.admin_one_access_token}"},
        )
        assert (
            patch_mass_users_deactivate_as_admin_user_failed_response.status_code == 403
        )
        ################################ LOGOUT ADMIN ########################################

        ################################ LOGIN SUPERUSER ########################################
        # logged in as superuser
        # try to mass restrict queried users
        # should succeed as superuser possesses the privilege
        patch_mass_users_deactivate_as_superuser_success_response = test_client.patch(
            f"/admin/user/all/restrict?id={goodman_five_and_four_uids_list_string}",
            headers={"Authorization": f"Bearer {self.superuser_access_token}"},
        )
        assert (
            patch_mass_users_deactivate_as_superuser_success_response.status_code == 200
        )

        # get users details to confirm accounts have been restricted/deactivated
        for goodman_uid in goodman_five_and_four_uids_list:
            get_goodman_user_to_confirm_account_restricted_status_response = (
                test_client.get(
                    f"/admin/user?id={goodman_uid}",
                    headers={"Authorization": f"Bearer {self.superuser_access_token}"},
                )
            )
            assert (
                get_goodman_user_to_confirm_account_restricted_status_response.status_code
                == 200
            )
            goodman_active_status = get_goodman_user_to_confirm_account_restricted_status_response.json().get(
                "active"
            )
            assert goodman_active_status is False
        ################################ LOGOUT SUPERUSER ########################################

        ################################ LOGIN GOODMAN4 - Now restricted user ########################################
        # try to access protected route to get user details
        # should fail as user is now restricted
        get_goodman_four_user_info_after_restriction_failed_response = test_client.get(
            "/user",
            headers={"Authorization": f"Bearer {self.goodman_four_access_token}"},
        )
        assert (
            get_goodman_four_user_info_after_restriction_failed_response.status_code
            == 403
        )

        assert (
            "detail"
            in get_goodman_four_user_info_after_restriction_failed_response.json().keys()
        )
        user_restricted_error_dict = (
            get_goodman_four_user_info_after_restriction_failed_response.json().get(
                "detail"
            )
        )
        assert type(user_restricted_error_dict) == dict
        assert "error" in user_restricted_error_dict.keys()
        assert user_restricted_error_dict.get("error") == Config.ACCOUNT_SUSPENDED_ERROR_CODE

        # try to login after account
        # should fail as restricted user login is prohibited
        post_login_goodman_four_after_restriction_failed_response = test_client.post(
            "/auth/login",
            json={
                "email": self.goodman_user_emails.get("goodman4"),
                "password": self.all_users_password,
            },
        )
        assert (
            post_login_goodman_four_after_restriction_failed_response.status_code == 403
        )
        ################################ LOGOUT GOODMAN4 ########################################

        ################################ LOGIN GOODMAN2 - NORMAL USER ########################################
        # logged in as goodman2 - normal user
        # try to mass unrestrict queried users
        # should fail as normal user does not possess the privilege
        patch_mass_users_activate_as_goodman_two_normal_user_failed_response = test_client.patch(
            f"/admin/user/all/unrestrict?id={goodman_five_and_four_uids_list_string}",
            headers={"Authorization": f"Bearer {self.goodman_two_access_token}"},
        )
        assert (
            patch_mass_users_activate_as_goodman_two_normal_user_failed_response.status_code
            == 403
        )
        ################################ LOGOUT GOODMAN2 - NORMAL USER ########################################

        ################################ LOGIN ADMIN ########################################
        # logged in as admin
        # try to mass unrestrict queried users
        # should fail as admin user does not possess the privilege
        patch_mass_users_activate_as_admin_user_failed_response = test_client.patch(
            f"/admin/user/all/unrestrict?id={goodman_five_and_four_uids_list_string}",
            headers={"Authorization": f"Bearer {self.admin_one_access_token}"},
        )
        assert (
            patch_mass_users_activate_as_admin_user_failed_response.status_code == 403
        )
        ################################ LOGOUT ADMIN ########################################

        ################################ LOGIN SUPERUSER ########################################
        # logged in as superuser
        # try to mass unrestrict queried users
        # should succeed as superuser possesses the privilege
        patch_mass_users_activate_as_superuser_success_response = test_client.patch(
            f"/admin/user/all/unrestrict?id={goodman_five_and_four_uids_list_string}",
            headers={"Authorization": f"Bearer {self.superuser_access_token}"},
        )
        assert (
            patch_mass_users_activate_as_superuser_success_response.status_code == 200
        )

        # get users details to confirm accounts have been unrestricted/activated
        for goodman_uid in goodman_five_and_four_uids_list:
            get_goodman_user_to_confirm_account_unrestricted_status_response = (
                test_client.get(
                    f"/admin/user?id={goodman_uid}",
                    headers={"Authorization": f"Bearer {self.superuser_access_token}"},
                )
            )
            assert (
                get_goodman_user_to_confirm_account_unrestricted_status_response.status_code
                == 200
            )
            goodman_active_status = get_goodman_user_to_confirm_account_unrestricted_status_response.json().get(
                "active"
            )
            assert goodman_active_status is True
        ################################ LOGOUT SUPERUSER ########################################

        ################################ LOGIN GOODMAN4 - Now restricted user ########################################
        # try to access protected route to get user details
        # should succeed as user is no longer restricted
        get_goodman_four_user_info_after_unrestriction_success_response = (
            test_client.get(
                "/user",
                headers={"Authorization": f"Bearer {self.goodman_four_access_token}"},
            )
        )
        assert (
            get_goodman_four_user_info_after_unrestriction_success_response.status_code
            == 200
        )

        # try to login after account
        # should succeed as user is no longer restricted and can now login
        post_login_goodman_four_after_unrestriction_success_response = test_client.post(
            "/auth/login",
            json={
                "email": self.goodman_user_emails.get("goodman4"),
                "password": self.all_users_password,
            },
        )
        assert (
            post_login_goodman_four_after_unrestriction_success_response.status_code
            == 200
        )
        ################################ LOGOUT GOODMAN4 ########################################

    async def test_mass_user_deletion_and_email_blacklisting(
        self, test_client, test_session
    ):
        """
        test mass delete created users
        """
        ###!!!!!! IMPORTANT !!!!!!###
        ## THIS SHOULD BE THE LAST TEST ##
        scrap_users_uid_list = []
        scrap_users_email_list = []

        parsed_password = hash_password("Abcd@1234")
        for n in range(1, 6):
            new_scrap_user = User(
                first_name="scrap",
                last_name="user",
                username=f"scrapuser{n}",
                email=f"scrap{n}@user.com",
                password=parsed_password,
                bio="this user is to be scrapped in this test",
            )
            test_session.add(new_scrap_user)
            await test_session.commit()
            await test_session.refresh(new_scrap_user)

            scrap_user_uid = str(new_scrap_user.uid)
            scrap_user_email = str(new_scrap_user.email)

            scrap_users_uid_list.append(scrap_user_uid)
            scrap_users_email_list.append(scrap_user_email)

        all_scrap_users_uid_list_string = ",".join(scrap_users_uid_list)
        ################################ LOGIN ADMIN ########################################
        # confirm all users to be deleted exist in database before mass deletion
        for user_uid in scrap_users_uid_list:
            get_scrap_user_user_before_deletion_response = test_client.get(
                f"/admin/user?id={user_uid}",
                headers={"Authorization": f"Bearer {self.admin_one_access_token}"},
            )
            assert get_scrap_user_user_before_deletion_response.status_code == 200
            scrap_user_uid = get_scrap_user_user_before_deletion_response.json().get(
                "uid"
            )
            assert scrap_user_uid == user_uid

        # logged in as admin user
        # try to mass delete users
        # should fail as only superuser can mass delete users
        delete_all_users_as_admin_user_failed_response = test_client.delete(
            f"/admin/user/all?id={all_scrap_users_uid_list_string}",
            headers={"Authorization": f"Bearer {self.admin_one_access_token}"},
        )
        assert delete_all_users_as_admin_user_failed_response.status_code == 403
        ################################ LOGOUT ADMIN ########################################

        ################################ LOGIN GOODMAN3 - NORMAL USER ########################################
        # logged in as scrap_user3 - normal user
        # try to mass delete users
        # should fail as only superuser can mass delete users
        delete_all_users_as_scrap_user_three_failed_response = test_client.delete(
            f"/admin/user/all?id={all_scrap_users_uid_list_string}",
            headers={"Authorization": f"Bearer {self.goodman_five_access_token}"},
        )
        assert delete_all_users_as_scrap_user_three_failed_response.status_code == 403
        ################################ LOGOUT GOODMAN3 - NORMAL USER ########################################

        ################################ LOGIN SUPERUSER ########################################
        # logged in as superuser
        # try to mass delete users
        # should succeed as only superuser is allowd to mass delete all users
        delete_all_users_as_superuser_success_response = test_client.delete(
            f"/admin/user/all?id={all_scrap_users_uid_list_string}",
            headers={"Authorization": f"Bearer {self.superuser_access_token}"},
        )
        assert delete_all_users_as_superuser_success_response.status_code == 200

        # confirm all users to be deleted no longer exist in database after mass deletion
        for user_uid in scrap_users_uid_list:
            get_scrap_user_user_after_deletion_response = test_client.get(
                f"/admin/user?id={user_uid}",
                headers={"Authorization": f"Bearer {self.superuser_access_token}"},
            )
            assert get_scrap_user_user_after_deletion_response.status_code == 404

        # confirm email is blacklisted in db
        blacklisted_email_count = 0
        for email in scrap_users_email_list:
            executed_query = await test_session.execute(
                select(BlacklistedEmail).where(
                    func.lower(BlacklistedEmail.sub) == email.lower()
                )
            )
            blacklisted_email = executed_query.scalar_one_or_none()
            assert blacklisted_email
            assert blacklisted_email.sub == email.lower()

            # increase the blacklisted email count to confirm during blacklisted email endpoint testing
            blacklisted_email_count += 1

            # confirm email cannot be used to create a new account with blacklisted email
            new_scrap_user_signup_data = self.goodman_user_create_data.copy()
            new_scrap_user_signup_data.update(
                {"email": email, "username": "returningscrapuser"}
            )
            post_new_scrap_user_user_signup_with_blacklisted_email_failed_response = (
                test_client.post(
                    "/admin/user",
                    headers={"Authorization": f"Bearer {self.superuser_access_token}"},
                    json=new_scrap_user_signup_data,
                )
            )
            de = (
                post_new_scrap_user_user_signup_with_blacklisted_email_failed_response.json()
            )
            assert (
                post_new_scrap_user_user_signup_with_blacklisted_email_failed_response.status_code
                == 403
            )

        # test get all blacklisted emails endpoint
        get_all_blacklisted_emails_response = test_client.get(
            "/admin/email_blacklist/all",
            headers={"Authorization": f"Bearer {self.superuser_access_token}"},
        )
        assert get_all_blacklisted_emails_response.status_code == 200
        blacklisted_emails_json = get_all_blacklisted_emails_response.json()
        assert "emails" in blacklisted_emails_json.keys()
        blacklisted_emails_list = blacklisted_emails_json.get("emails")
        assert len(blacklisted_emails_list) == blacklisted_email_count
        first_blacklisted_email = blacklisted_emails_list[0]
        assert type(first_blacklisted_email) == dict
        assert {"sub", "id", "created_at"}.issubset(first_blacklisted_email.keys())

        ################################ LOGOUT SUPERUSER ########################################

    async def test_blacklisted_token_user_logout_mechanism(
        self, test_client, test_session
    ):
        # retrieve all current blacklisted tokens before starting tests
        executed_before_token_count_query = await test_session.execute(
            select(func.count()).select_from(BlacklistedToken)
        )
        blacklisted_token_count_before_user_logout = (
            executed_before_token_count_query.scalar_one_or_none()
        )

        ################################ LOGIN SUPERUSER ########################################
        # login as superuser
        post_superuser_login_response = test_client.post(
            "/auth/login",
            json={
                "email": self.superuser_create_data["email"],
                "password": self.SUPERUSER_PASSWORD,
            },
        )
        assert post_superuser_login_response.status_code == 200
        assert "refresh_token" in post_superuser_login_response.cookies

        post_superuser_logout_response = test_client.post(
            "/auth/logout",
        )
        assert post_superuser_logout_response.status_code == 200
        ################################ LOGOUT SUPERUSER ########################################

        executed_after_token_count_query = await test_session.execute(
            select(func.count()).select_from(BlacklistedToken)
        )
        blacklisted_token_count_after_user_logout = (
            executed_after_token_count_query.scalar_one_or_none()
        )

        # confirm that blacklisted token in database increased by one after user logout
        # indicating that token was blacklisted
        assert blacklisted_token_count_after_user_logout == (
            blacklisted_token_count_before_user_logout + 1
        )

    async def test_token_blacklisting_deletion(self, test_client, test_session):

        expired_jti = uuid4()
        expired_exp = (datetime.now(tz=timezone.utc) - timedelta(hours=2)).timestamp()

        fresh_jti = uuid4()
        fresh_exp = (datetime.now(tz=timezone.utc) + timedelta(hours=2)).timestamp()

        expired_token = BlacklistedToken(jti=expired_jti, exp=expired_exp)
        test_session.add(expired_token)
        await test_session.commit()
        await test_session.refresh(expired_token)
        expired_token_id = expired_token.id

        fresh_token = BlacklistedToken(jti=fresh_jti, exp=fresh_exp)
        test_session.add(fresh_token)
        await test_session.commit()
        await test_session.refresh(fresh_token)
        fresh_token_id = fresh_token.id

        ################################ LOGIN ADMIN ########################################
        # try to delete fresh token
        # should fail since the fresh blacklisted token is not yet expired
        delete_fresh_blacklisted_token_failed_response = test_client.delete(
            f"/admin/token_blacklist/all/?id={fresh_token_id}",
            headers={"Authorization": f"Bearer {self.admin_one_access_token}"},
        )
        assert delete_fresh_blacklisted_token_failed_response.status_code == 422

        # try to delete both fresh and expired tokens
        # should fail since one of the tokens is not yet expired
        delete_both_fresh_and_expired_blacklisted_tokens_failed_response = (
            test_client.delete(
                f"/admin/token_blacklist/all/?id={expired_token_id},{fresh_token_id}",
                headers={"Authorization": f"Bearer {self.admin_one_access_token}"},
            )
        )
        assert (
            delete_both_fresh_and_expired_blacklisted_tokens_failed_response.status_code
            == 422
        )

        # try to delete only expired token
        # should succeed since tokens is expired
        delete_expired_blacklisted_token_success_response = test_client.delete(
            f"/admin/token_blacklist/all/?id={expired_token_id}",
            headers={"Authorization": f"Bearer {self.admin_one_access_token}"},
        )
        assert delete_expired_blacklisted_token_success_response.status_code == 200
        ################################ LOGOUT ADMIN ########################################

        # delete fresh blacklisted token
        await test_session.delete(fresh_token)
        await test_session.commit()
