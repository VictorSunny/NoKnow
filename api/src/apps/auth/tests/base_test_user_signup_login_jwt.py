import ast
import pytest

from src.utilities.utilities import ast, slugify_strings
from src.tests.conftest import test_client, get_test_session, r_client

BASE_AUTH_URL_PREFIX = "/auth"
BASE_USER_URL_PREFIX = "/user"

USER_COMPLETE_KEYS = {
    "uid",
    "first_name",
    "last_name",
    "email",
    "username",
    "bio",
    "joined",
    "last_seen",
    "online",
    "is_two_factor_authenticated",
    "is_hidden",
    "active",
    "role",
}


class BaseTestUserSignupLogin:

    @classmethod
    def setup_class(self):
        """
        set up data to be used across tests' post requests
        """

        # password over 8 characters, containing uppercase, lowercase, numeric, and special characters
        self.all_users_password = "comPl3x-passw0rd"
        self.all_users_password_confirm = self.all_users_password

        self.user_one_signup_data = {
            "first_name": "user",
            "last_name": "one",
            "username": "user1",
            "email": "user@one.com",
            "password": self.all_users_password,
            "confirm_password": self.all_users_password_confirm,
            "bio": "user one is an npc and this bio has to be above 24 characters",
        }
        self.user_two_signup_data = {
            "first_name": "user",
            "last_name": "two",
            "username": "user2",
            "email": "user@two.com",
            "password": self.all_users_password,
            "confirm_password": self.all_users_password_confirm,
            "bio": "user two is an npc and this bio has to be above 25 characters",
        }
        self.user_three_signup_data = {
            "first_name": "user",
            "last_name": "three",
            "username": "user3",
            "email": "user@three.com",
            "password": self.all_users_password,
            "confirm_password": self.all_users_password_confirm,
            "bio": "user three is an npc and this bio has to be above 25 characters",
        }
        self.user_four_signup_data = {
            "first_name": "user",
            "last_name": "four",
            "username": "user4",
            "email": "user@four.com",
            "password": self.all_users_password,
            "confirm_password": self.all_users_password_confirm,
            "bio": "user four is an npc and this bio has to be above 25 characters",
        }

        self.user_one_email = self.user_one_signup_data["email"]
        self.user_two_email = self.user_two_signup_data["email"]
        self.user_three_email = self.user_three_signup_data["email"]
        self.user_four_email = self.user_four_signup_data["email"]

        self.user_one_username = self.user_one_signup_data["username"]
        self.user_one_first_name = self.user_one_signup_data["first_name"]
        self.user_one_last_name = self.user_one_signup_data["last_name"]
        self.user_one_bio = self.user_one_signup_data["bio"]

        self.signup_otp_jwts = dict()
        self.user_access_tokens = dict()
        self.user_uids = dict()

        self.updated_user_email = "new@email.com"

    async def test_otp_generation_and_verification(self, test_client, r_client):
        """
        test otp code generation and
        """

        signup_use_case = "signup"
        for email in [
            self.user_one_email,
            self.user_two_email,
            self.user_three_email,
            self.user_four_email,
            self.updated_user_email,
        ]:
            # request for otp token
            signup_otp_code_request = test_client.post(
                f"{BASE_AUTH_URL_PREFIX}/otp/request?use_case={signup_use_case}",
                json={"email": email},
            )
            # check otp token has been cached to redis
            # otp token will be sent to user's email, but that cannot be tested for
            assert signup_otp_code_request.status_code == 202

            # get otp token from redis
            signup_otp_key = slugify_strings([email, signup_use_case])
            redis_res = await r_client.get(signup_otp_key)
            otp_data = ast.literal_eval(redis_res)
            assert otp_data is not None
            expected_otp_json_keys = {"sub", "code", "exp", "otp_type"}
            assert expected_otp_json_keys == set(otp_data.keys())
            # extract otp code
            otp_code = otp_data.get("code")

            # confirm otp code for token
            signup_otp_token_request = test_client.post(
                f"{BASE_AUTH_URL_PREFIX}/otp/token?use_case={signup_use_case}",
                json={"email": email, "otp": otp_code},
            )
            assert signup_otp_token_request.status_code == 200

            assert "otp_jwt" in signup_otp_token_request.json().keys()

            self.__class__.signup_otp_jwts[email] = signup_otp_token_request.json().get(
                "otp_jwt"
            )
            assert email in self.signup_otp_jwts

    def test_user_signup_field_constraints_and_otp_jwt_email_security(
        self, test_client
    ):
        # create 2 new users with fresh information
        # creating 2 users to test other features
        user_one_otp_jwt = self.signup_otp_jwts.get(self.user_one_email)
        user_two_otp_jwt = self.signup_otp_jwts.get(self.user_two_email)
        user_three_otp_jwt = self.signup_otp_jwts.get(self.user_three_email)
        user_four_otp_jwt = self.signup_otp_jwts.get(self.user_four_email)

        updated_email_otp_jwt = self.signup_otp_jwts.get(self.updated_user_email)

        for signup_otp_token, signup_data in zip(
            [user_one_otp_jwt, user_two_otp_jwt, user_three_otp_jwt, user_four_otp_jwt],
            [
                self.user_one_signup_data,
                self.user_two_signup_data,
                self.user_three_signup_data,
                self.user_four_signup_data,
            ],
        ):

            # test signup data check endpoint
            # endpoint checks if user sharing sensitive data like email, username already exists in db
            # confirm no user sharing data already exists in db
            post_signup_data_check_before_signup_response = test_client.post(
                f"{BASE_AUTH_URL_PREFIX}/data/check", json=signup_data
            )
            # confirm success status
            # proves that there is no user in db sharing sensitive data
            assert post_signup_data_check_before_signup_response.status_code == 200

            # test weak password constraints
            copied_signup_data_for_weak_password = signup_data.copy()
            # each of these passwords is lacking in one required area
            # e.g contains lowercase, uppercase, and symbol, but no number
            weak_passwords = [
                "$H0rt",
                "n0_upper_cas3",
                "N0_LOWER_CAS3",
                "N0symbolINCLUD3D",
                "noNUMBERincluded$",
            ]
            for weak_password in weak_passwords:
                copied_signup_data_for_weak_password.update(
                    {"password": weak_password, "confirm_password": weak_password}
                )
                weak_password_user_signup_response = test_client.post(
                    f"{BASE_AUTH_URL_PREFIX}/signup?otp_token={signup_otp_token}",
                    json=copied_signup_data_for_weak_password,
                )
                assert weak_password_user_signup_response.status_code == 422

            # test username character type constraint
            # should fail if username containts non alphanumeric characters
            user_signup_with_unsupported_username = signup_data.copy()
            user_signup_with_unsupported_username.update(
                {"username": "3number_underscore"}
            )
            post_invalid_username_signup_response = test_client.post(
                f"{BASE_AUTH_URL_PREFIX}/signup?otp_token={signup_otp_token}",
                json=user_signup_with_unsupported_username,
            )
            assert post_invalid_username_signup_response.status_code == 422

            # signup with correct data and otp_token
            user_signup_with_correct_email_used_for_otp_request_success_response = (
                test_client.post(
                    f"{BASE_AUTH_URL_PREFIX}/signup?otp_token={signup_otp_token}",
                    json=signup_data,
                )
            )
            assert (
                user_signup_with_correct_email_used_for_otp_request_success_response.status_code
                == 201
            )

            # confirm successful signup response content
            user_signup_response_json = (
                user_signup_with_correct_email_used_for_otp_request_success_response.json()
            )

            assert USER_COMPLETE_KEYS == user_signup_response_json.keys()

            # save user uid into class attribute
            self.__class__.user_uids[signup_data.get("email")] = (
                user_signup_response_json.get("uid")
            )

            # confirm no user sharing data already exists in db
            post_signup_data_check_after_signup_response = test_client.post(
                f"{BASE_AUTH_URL_PREFIX}/data/check", json=signup_data
            )
            # confirm success status
            # proves that there is no user in db sharing sensitive data
            assert post_signup_data_check_after_signup_response.status_code == 409

            # test user username unique constraint
            copied_signup_data_for_username_unique_constraint_test = signup_data.copy()
            # set new email, but username is unchanged from previously used, and is still taken
            copied_signup_data_for_username_unique_constraint_test.update(
                # use correct otp_token for updated_user_email to test
                {"email": self.updated_user_email}
            )
            reused_username_user_signup_response_with_valid_otp_jwt = test_client.post(
                f"{BASE_AUTH_URL_PREFIX}/signup?otp_token={updated_email_otp_jwt}",  # USE CORRECT OTP TOKEN FOR TEST TO WORK
                json=copied_signup_data_for_username_unique_constraint_test,
            )
            assert (
                reused_username_user_signup_response_with_valid_otp_jwt.status_code
                == 409
            )

            # test user email unique constraint
            copied_signup_data_for_email_unique_constraint_test = signup_data.copy()
            # set new usernmae, but email is unchanged from previously used, and is still taken
            copied_signup_data_for_email_unique_constraint_test.update(
                {"username": "newusernameeee"}
            )
            reused_email_user_signup_response_with_valid_otp_jwt = test_client.post(
                f"{BASE_AUTH_URL_PREFIX}/signup?otp_token={signup_otp_token}",
                json=copied_signup_data_for_email_unique_constraint_test,
            )
            assert (
                reused_email_user_signup_response_with_valid_otp_jwt.status_code == 409
            )

            # try to signup with otp token not matching email in signup form
            # should fail as new updated email was not used for requesting otp
            # suspicious activity detected
            singup_data_with_different_email_from_one_used_for_otp_request = (
                signup_data.copy()
            )
            singup_data_with_different_email_from_one_used_for_otp_request.update(
                {"email": "suspicious@mail.com"}
            )
            user_signup_with_incorrect_email_different_from_otp_request_email_failed_response = test_client.post(
                f"{BASE_AUTH_URL_PREFIX}/signup?otp_token={signup_otp_token}",
                json=singup_data_with_different_email_from_one_used_for_otp_request,
            )
            assert (
                user_signup_with_incorrect_email_different_from_otp_request_email_failed_response.status_code
                == 403
            )

        # initaiize user uid attributes for all users
        self.__class__.user_one_uid = self.user_uids.get(self.user_one_email)
        self.__class__.user_two_uid = self.user_uids.get(self.user_two_email)
        self.__class__.user_three_uid = self.user_uids.get(self.user_three_email)
        self.__class__.user_four_uid = self.user_uids.get(self.user_four_email)

    def test_user_login_logout_access_token_refresh_token_mechanism(self, test_client):
        """
        test for user login mechanism
        """
        login_form = {"email": self.user_one_email, "password": self.all_users_password}
        successful_login_response = test_client.post(
            f"{BASE_AUTH_URL_PREFIX}/login", json=login_form
        )

        assert successful_login_response.status_code == 200

        response_token_dict = successful_login_response.json()

        assert {"access_token", "token_type"} == response_token_dict.keys()
        assert "refresh_token" in successful_login_response.cookies

        get_user_one_refreshed_access_token_response = test_client.get(
            f"{BASE_AUTH_URL_PREFIX}/token"
        )
        assert get_user_one_refreshed_access_token_response.status_code == 200
        assert {
            "access_token",
            "token_type",
        } == get_user_one_refreshed_access_token_response.json().keys()
        user_one_refreshed_access_token = (
            get_user_one_refreshed_access_token_response.json().get("access_token")
        )

        # confirm refreshed access token is truly for last logged in user: user1
        get_user_one_details_with_refreshed_access_token_response = test_client.get(
            f"{BASE_USER_URL_PREFIX}",
            headers={"Authorization": f"Bearer {user_one_refreshed_access_token}"},
        )
        assert (
            get_user_one_details_with_refreshed_access_token_response.status_code == 200
        )
        assert (
            get_user_one_details_with_refreshed_access_token_response.json().keys()
            == USER_COMPLETE_KEYS
        )
        refreshed_user_uid = (
            get_user_one_details_with_refreshed_access_token_response.json().get("uid")
        )
        assert refreshed_user_uid == self.user_one_uid

        user_one_access_token = response_token_dict["access_token"]
        self.__class__.user_access_tokens[self.user_one_email] = user_one_access_token
        user_profile_response = test_client.get(
            f"{BASE_USER_URL_PREFIX}",
            headers={"Authorization": f"Bearer {user_one_access_token}"},
        )
        assert user_profile_response.status_code == 200
        user_profile_info = user_profile_response.json()

        assert str(user_profile_info["first_name"]).istitle()
        assert str(user_profile_info["last_name"]).istitle()
        assert str(user_profile_info["email"]).islower()

        assert str(self.user_one_email).lower() == str(user_profile_info["email"])
        assert str(self.user_one_username).lower() == str(user_profile_info["username"])
        assert str(self.user_one_first_name).title() == str(
            user_profile_info["first_name"]
        )
        assert str(self.user_one_last_name).title() == str(
            user_profile_info["last_name"]
        )

        # login to retrieve otp for the other users
        for email, password in zip(
            [self.user_two_email, self.user_three_email, self.user_four_email],
            [self.all_users_password, self.all_users_password, self.all_users_password],
        ):
            login_form = {"email": email, "password": password}
            successful_login_response = test_client.post(
                f"{BASE_AUTH_URL_PREFIX}/login", json=login_form
            )
            assert successful_login_response.status_code == 200
            access_token = successful_login_response.json().get("access_token")
            self.__class__.user_access_tokens[email] = access_token

        self.__class__.user_one_access_token = self.user_access_tokens.get(
            self.user_one_email
        )
        self.__class__.user_two_access_token = self.user_access_tokens.get(
            self.user_two_email
        )
        self.__class__.user_three_access_token = self.user_access_tokens.get(
            self.user_three_email
        )
        self.__class__.user_four_access_token = self.user_access_tokens.get(
            self.user_four_email
        )

        # test refresh token endpoint
        get_refreshed_acccess_token_response = test_client.get(
            f"{BASE_AUTH_URL_PREFIX}/token",
        )
        assert get_refreshed_acccess_token_response.status_code == 200
        refresh_token_keys = get_refreshed_acccess_token_response.json().keys()
        assert {"access_token", "token_type"} == refresh_token_keys

    def test_user_login_password_constraint(self, test_client):
        """
        test for user login
        """
        # try to login user with wrong password
        # should fail
        login_form = {"email": self.user_one_email, "password": "wrong password"}
        post_unsuccessful_login_response = test_client.post(
            f"{BASE_AUTH_URL_PREFIX}/login", json=login_form
        )
        assert post_unsuccessful_login_response.status_code == 401

    def test_user_login_email_check(self, test_client):
        """
        test for successful login of user
        """
        login_form = {
            "email": "email_not_in_database@gmail.com",
            "password": self.all_users_password,
        }
        post_unsuccessful_login_response = test_client.post(
            f"{BASE_AUTH_URL_PREFIX}/login", json=login_form
        )

        assert post_unsuccessful_login_response.status_code == 404

    async def test_is_two_factor_authenticated_login_and_logout(
        self, test_client, r_client
    ):
        """
        test two factor authentication for user1.
        require otp token for login.
        """
        login_use_case = "login"
        ################################ LOGIN USER1 ########################################
        # confirm that two factor auth is not active by default

        ### get current two factor auth status

        # using auth header without json data
        get_user_two_factor_auth_status_without_auth_header_and_without_email_form_failed_response = test_client.post(
            f"{BASE_AUTH_URL_PREFIX}/two_factor_authentication",
        )
        assert (
            get_user_two_factor_auth_status_without_auth_header_and_without_email_form_failed_response.status_code
            == 401
        )

        # using auth header without json data
        get_user_two_factor_auth_status_with_auth_header_response = test_client.post(
            f"{BASE_AUTH_URL_PREFIX}/two_factor_authentication",
            headers={"Authorization": f"Bearer {self.user_one_access_token}"},
        )
        assert (
            get_user_two_factor_auth_status_with_auth_header_response.status_code == 200
        )
        # confirm the necessary key is available in the response json
        assert (
            "is_two_factor_authenticated"
            in get_user_two_factor_auth_status_with_auth_header_response.json()
        )
        user_one_two_factor_auth_status = (
            get_user_two_factor_auth_status_with_auth_header_response.json().get(
                "is_two_factor_authenticated"
            )
        )
        # confirm two factor auth is not active
        assert user_one_two_factor_auth_status == False

        # using auth header without json data
        get_user_two_factor_auth_status_with_json_data_response = test_client.post(
            f"{BASE_AUTH_URL_PREFIX}/two_factor_authentication",
            json={"email": self.user_one_email},
        )
        assert (
            get_user_two_factor_auth_status_with_json_data_response.status_code == 200
        )
        # confirm the necessary key is available in the response json
        assert (
            "is_two_factor_authenticated"
            in get_user_two_factor_auth_status_with_json_data_response.json()
        )
        user_one_two_factor_auth_status = (
            get_user_two_factor_auth_status_with_json_data_response.json().get(
                "is_two_factor_authenticated"
            )
        )
        # confirm two factor auth is not active
        assert user_one_two_factor_auth_status == False

        # toggle on user two factor auth
        patch_user_one_two_factor_auth_switch_response = test_client.patch(
            f"{BASE_AUTH_URL_PREFIX}/two_factor_authentication",
            json={"password": self.all_users_password},
            headers={"Authorization": f"Bearer {self.user_one_access_token}"},
        )
        assert patch_user_one_two_factor_auth_switch_response.status_code == 200
        # confirm the necessary key is available in the response json
        assert (
            "is_two_factor_authenticated"
            in patch_user_one_two_factor_auth_switch_response.json()
        )
        user_one_is_two_factor_authenticated_status = (
            patch_user_one_two_factor_auth_switch_response.json().get(
                "is_two_factor_authenticated"
            )
        )
        # confirm two factor auth is not active
        assert user_one_is_two_factor_authenticated_status == True
        ################################ LOGOUT USER1 ########################################

        # try to login user1 for access and refresh token
        # login without otp_token
        # should fail as user1 two factor authentication is now active and requires otp_token url param
        login_form = {"email": self.user_one_email, "password": self.all_users_password}
        post_user_one_failed_login_response = test_client.post(
            f"{BASE_AUTH_URL_PREFIX}/login", json=login_form
        )
        assert post_user_one_failed_login_response.status_code == 401

        post_user_one_login_otp_request = test_client.post(
            f"{BASE_AUTH_URL_PREFIX}/otp/request?use_case={login_use_case}",
            json={"email": self.user_one_email},
        )
        assert post_user_one_login_otp_request.status_code == 202

        # get otp token from redis
        user_one_login_otp_key = slugify_strings([self.user_one_email, login_use_case])
        redis_res = await r_client.get(user_one_login_otp_key)
        user_one_login_otp_json = ast.literal_eval(redis_res)
        assert user_one_login_otp_json is not None
        expected_otp_json_keys = {"sub", "code", "exp", "otp_type"}
        assert expected_otp_json_keys == set(user_one_login_otp_json.keys())
        # extract otp code
        user_one_login_otp_code = user_one_login_otp_json.get("code")

        post_user_one_login_otp_token_response = test_client.post(
            f"{BASE_AUTH_URL_PREFIX}/otp/token?use_case={login_use_case}",
            json={"email": self.user_one_email, "otp": user_one_login_otp_code},
        )
        assert post_user_one_login_otp_token_response.status_code == 200
        assert "otp_jwt" in post_user_one_login_otp_token_response.json().keys()
        user_one_login_otp_token = post_user_one_login_otp_token_response.json().get(
            "otp_jwt"
        )

        ### USER1 REAL LOGIN VIA ENDPOINT
        # login with otp_token
        # should succeed as user1 two factor authentication is active otp_token url param is present
        login_form = {"email": self.user_one_email, "password": self.all_users_password}
        post_user_one_successful_login_response = test_client.post(
            f"{BASE_AUTH_URL_PREFIX}/login?otp_token={user_one_login_otp_token}",
            json=login_form,
        )
        assert post_user_one_successful_login_response.status_code == 200
        user_one_access_token = post_user_one_successful_login_response.json().get(
            "access_token"
        )

        ################################ LOGIN USER1 ########################################
        # toggle off two factor authentication
        post_user_one_two_factor_auth_switch_off_response = test_client.patch(
            f"{BASE_AUTH_URL_PREFIX}/two_factor_authentication",
            json={"password": self.all_users_password},
            headers={"Authorization": f"Bearer {user_one_access_token}"},
        )
        assert post_user_one_two_factor_auth_switch_off_response.status_code == 200
        # confirm the necessary key is available in the response json
        user_one_two_factor_auth_inactive_status = (
            post_user_one_two_factor_auth_switch_off_response.json().get(
                "is_two_factor_authenticated"
            )
        )
        # confirm two factor auth is not active
        assert user_one_two_factor_auth_inactive_status == False

        # test user details endpoint for user1 to confirm user
        get_user_one_details_with_auth_header_response = test_client.get(
            f"{BASE_USER_URL_PREFIX}",
            headers={"Authorization": f"Bearer {user_one_access_token}"},
        )
        assert get_user_one_details_with_auth_header_response.status_code == 200
        user_uid = get_user_one_details_with_auth_header_response.json().get("uid")
        assert user_uid == self.user_one_uid

        #### test logout

        # try to refresh access token before logout
        # should succeed as user is logged in and user refresh token is not yet blacklisted
        get_user_one_refreshed_access_token_before_logout_response = test_client.get(
            f"{BASE_AUTH_URL_PREFIX}/token"
        )
        assert (
            get_user_one_refreshed_access_token_before_logout_response.status_code
            == 200
        )
        assert {
            "access_token",
            "token_type",
        } == get_user_one_refreshed_access_token_before_logout_response.json().keys()
        user_one_refreshed_access_token = (
            get_user_one_refreshed_access_token_before_logout_response.json().get(
                "access_token"
            )
        )

        # confirm refreshed access token is truly for last logged in user: user1
        get_user_one_details_with_refreshed_access_token_response = test_client.get(
            f"{BASE_USER_URL_PREFIX}",
            headers={"Authorization": f"Bearer {user_one_refreshed_access_token}"},
        )
        assert (
            get_user_one_details_with_refreshed_access_token_response.status_code == 200
        )
        refreshed_user_uid = (
            get_user_one_details_with_refreshed_access_token_response.json().get("uid")
        )
        assert refreshed_user_uid == self.user_one_uid

        ### USER1 REAL LOGOUT VIA ENDPOINT
        # try logout
        # should succeed as user has refresh_token cookie meaning user is logged in
        post_logout_last_logged_in_user_first_attempt_response = test_client.post(
            f"{BASE_AUTH_URL_PREFIX}/logout"
        )
        # logout must clear refresh token cookie
        assert post_logout_last_logged_in_user_first_attempt_response.status_code == 200

        # try logout
        # should fail as us already logged out
        # should succeed as user has refresh_token cookie meaning user is logged in
        post_logout_last_logged_in_user_first_second_response = test_client.post(
            f"{BASE_AUTH_URL_PREFIX}/logout"
        )
        assert post_logout_last_logged_in_user_first_second_response.status_code == 401

        # try to refresh access token after logout
        # should fail as user is logged out and user refresh token is cleared from browser
        get_user_one_refreshed_access_token_after_logout_response = test_client.get(
            f"{BASE_AUTH_URL_PREFIX}/token"
        )
        assert (
            get_user_one_refreshed_access_token_after_logout_response.status_code == 401
        )

        ################################ LOGOUT USER1 ########################################

    async def test_update_user_email(self, test_client, r_client):
        """
        test email change mechanism logged in as user one
        """
        new_email = "new@updated.email"
        user_one_email_update_form = {
            "email": new_email,
            "password": self.all_users_password,
        }
        email_change_use_case = "email_change"
        user_one_signup_otp_token = self.signup_otp_jwts[self.user_one_email]

        get_user_one_details_response = test_client.get(
            f"{BASE_USER_URL_PREFIX}",
            headers={"Authorization": f"Bearer {self.user_one_access_token}"},
        )
        user_one_details_json = get_user_one_details_response.json()
        # confirm that user1 details response email matches the original user1 email
        assert self.user_one_email == user_one_details_json.get("email")
        assert user_one_details_json.get("email") != new_email

        # try to update email without otp_token url param
        # should fail as otp_token is required
        patch_user_one_email_without_otp_token_fail_response = test_client.patch(
            f"{BASE_AUTH_URL_PREFIX}/email",
            headers={"Authorization": f"Bearer {self.user_one_access_token}"},
            json=user_one_email_update_form,
        )
        # confirm error
        assert patch_user_one_email_without_otp_token_fail_response.status_code == 422

        post_user_one_email_change_otp_code_request_response = test_client.post(
            f"{BASE_AUTH_URL_PREFIX}/otp/request?use_case={email_change_use_case}",
            json={"email": new_email},
        )
        assert post_user_one_email_change_otp_code_request_response.status_code == 202

        # confirm retrieve otp code from redis server
        # get otp token from redis
        email_change_otp_key = slugify_strings([new_email, email_change_use_case])
        redis_res = await r_client.get(email_change_otp_key)
        email_change_otp_data = ast.literal_eval(redis_res)
        assert email_change_otp_data is not None
        # extract otp code
        user_one_email_change_otp_code = email_change_otp_data.get("code")

        post_user_one_email_change_otp_token_request_response = test_client.post(
            f"{BASE_AUTH_URL_PREFIX}/otp/token?use_case={email_change_use_case}",
            json={"email": new_email, "otp": user_one_email_change_otp_code},
        )
        assert post_user_one_email_change_otp_token_request_response.status_code == 200
        # extract otp token from response json
        user_one_email_change_otp_token = (
            post_user_one_email_change_otp_token_request_response.json().get("otp_jwt")
        )

        # try to update email otp_token url param
        # should succeed as valid otp_token is provided
        patch_user_one_email_change_with_otp_token_success_response = test_client.patch(
            f"{BASE_AUTH_URL_PREFIX}/email?otp_token={user_one_email_change_otp_token}",
            headers={"Authorization": f"Bearer {self.user_one_access_token}"},
            json=user_one_email_update_form,
        )
        assert (
            patch_user_one_email_change_with_otp_token_success_response.status_code
            == 200
        )

        # confirm email update changes are reflected
        # get user details for check
        get_user_one_details_after_email_update_response = test_client.get(
            f"{BASE_USER_URL_PREFIX}",
            headers={"Authorization": f"Bearer {self.user_one_access_token}"},
        )
        user_one_updated_email_details_json = (
            get_user_one_details_after_email_update_response.json()
        )
        # confirm that user1 details response email matches the updated new email
        assert user_one_updated_email_details_json.get("email") == new_email
        assert user_one_updated_email_details_json.get("email") != self.user_one_email

        test_client.post(
            f"{BASE_AUTH_URL_PREFIX}/otp/request?use_case={email_change_use_case}",
            json={"email": self.user_one_email},
        )
        email_reset_otp_key = slugify_strings(
            [self.user_one_email, email_change_use_case]
        )
        redis_res = await r_client.get(email_reset_otp_key)
        email_reset_otp_data = ast.literal_eval(redis_res)
        assert email_reset_otp_data is not None
        # extract otp code
        user_one_email_reset_otp_code = email_reset_otp_data.get("code")
        post_email_reset_response = test_client.post(
            f"{BASE_AUTH_URL_PREFIX}/otp/token?use_case={email_change_use_case}",
            json={"email": self.user_one_email, "otp": user_one_email_reset_otp_code},
        )
        user_one_email_reset_otp_token = post_email_reset_response.json().get("otp_jwt")
        # revert user1 email to original to carry out future tests smoothly
        patch_user_one_email_reset_success_response = test_client.patch(
            f"{BASE_AUTH_URL_PREFIX}/email?otp_token={user_one_email_reset_otp_token}",
            headers={"Authorization": f"Bearer {self.user_one_access_token}"},
            json={"email": self.user_one_email, "password": self.all_users_password},
        )
        assert patch_user_one_email_reset_success_response.status_code == 200

        # try to update user1 email using signup jwt token
        # should fail as token was created for signup not email change
        patch_user_one_email_update_with_signup_otp_jwt_token_failed_response = (
            test_client.patch(
                f"{BASE_AUTH_URL_PREFIX}/email?otp_token={user_one_signup_otp_token}",
                headers={"Authorization": f"Bearer {self.user_one_access_token}"},
                json={
                    "email": "Wrong@token.com",
                    "password": self.all_users_password,
                },
            )
        )
        assert (
            patch_user_one_email_update_with_signup_otp_jwt_token_failed_response.status_code
            == 403
        )

    async def test_update_user_password(self, test_client, r_client):
        """
        test password change mechanism logged in as user one
        """

        email = self.user_one_email
        access_token = self.user_one_access_token

        new_password_one = "Compl3x-N3wpassword"
        new_password_two = "Compl3x-N3w--password"

        default_user_password = self.all_users_password

        password_change_use_case = "password_change"

        # try to update user1 password without old password and without password change otp token
        # should fail as password update requires either old password or password change otp token

        patch_user_one_password_change_no_otp_token_no_old_password_fail_response = (
            test_client.patch(
                f"{BASE_AUTH_URL_PREFIX}/password",
                headers={"Authorization": f"Bearer {access_token}"},
                json={
                    "password": new_password_one,
                    "confirm_password": new_password_one,
                },
            )
        )
        assert (
            patch_user_one_password_change_no_otp_token_no_old_password_fail_response.status_code
            == 422
        )

        # try to update user1 password with old password
        # should succeed as old password is provided
        patch_user_one_password_change_with_old_password_without_otp_token_success_response = test_client.patch(
            f"{BASE_AUTH_URL_PREFIX}/password",
            headers={"Authorization": f"Bearer {access_token}"},
            json={
                "old_password": default_user_password,
                "password": new_password_one,
                "confirm_password": new_password_one,
            },
        )
        assert (
            patch_user_one_password_change_with_old_password_without_otp_token_success_response.status_code
            == 200
        )
        # check password
        post_password_valid_after_no_otp_token_update_response = test_client.post(
            f"{BASE_AUTH_URL_PREFIX}/confirm/password",
            headers={"Authorization": f"Bearer {access_token}"},
            json={"password": new_password_one},
        )
        password_valid_after_no_otp_token_update = (
            post_password_valid_after_no_otp_token_update_response.json().get("valid")
        )
        assert password_valid_after_no_otp_token_update == True

        # request for password_change otp code
        password_change_otp_code_request = test_client.post(
            f"{BASE_AUTH_URL_PREFIX}/otp/request?use_case={password_change_use_case}",
            json={"email": email},
        )
        # check otp token has been cached to redis
        # otp token will be sent to user's email, but that cannot be tested for
        assert password_change_otp_code_request.status_code == 202
        # get otp token from redis

        # get otp token from redis
        password_change_otp_key = slugify_strings([email, password_change_use_case])
        redis_res = await r_client.get(password_change_otp_key)
        password_change_otp_data = ast.literal_eval(redis_res)
        assert password_change_otp_data is not None
        # extract otp code
        password_change_otp_code = password_change_otp_data.get("code")

        post_user_one_password_change_otp_token_request_response = test_client.post(
            f"{BASE_AUTH_URL_PREFIX}/otp/token?use_case=password_change",
            json={"email": email, "otp": password_change_otp_code},
        )
        assert (
            post_user_one_password_change_otp_token_request_response.status_code == 200
        )
        # extract otp token from response json
        user_one_password_change_otp_token = (
            post_user_one_password_change_otp_token_request_response.json().get(
                "otp_jwt"
            )
        )

        # try to update user1 password without old password, and with otp_token
        # should succeed as otp_token is provided
        # in case of forgotten password
        patch_user_one_password_change_without_old_new_password_two_success_response = test_client.patch(
            f"{BASE_AUTH_URL_PREFIX}/password?otp_token={user_one_password_change_otp_token}",
            headers={"Authorization": f"Bearer {access_token}"},
            json={
                "password": new_password_two,
                "confirm_password": new_password_two,
            },
        )
        assert (
            patch_user_one_password_change_without_old_new_password_two_success_response.status_code
            == 200
        )

        post_password_valid_after_otp_token_update_response = test_client.post(
            f"{BASE_AUTH_URL_PREFIX}/confirm/password",
            headers={"Authorization": f"Bearer {access_token}"},
            json={"password": new_password_two},
        )
        password_valid_after_otp_token_update = (
            post_password_valid_after_otp_token_update_response.json().get("valid")
        )
        assert password_valid_after_otp_token_update == True

        # try to update user1 password without mismatching cofirm password
        # should fail as password and confirm password do not match is provided
        patch_user_one_password_change_with_mismatching_passwords_response = test_client.patch(
            f"{BASE_AUTH_URL_PREFIX}/password?otp_token={user_one_password_change_otp_token}",
            headers={"Authorization": f"Bearer {access_token}"},
            json={
                "password": "n3w-pwORD",
                "confirm_password": "mismatching-n3w-pWOrd",
            },
        )
        assert (
            patch_user_one_password_change_with_mismatching_passwords_response.status_code
            == 422
        )

        # reset user1 password to default password for all test users
        patch_revert_user_one_password_to_default_success_response = test_client.patch(
            f"{BASE_AUTH_URL_PREFIX}/password?otp_token={user_one_password_change_otp_token}",
            headers={"Authorization": f"Bearer {access_token}"},
            json={
                "password": default_user_password,
                "confirm_password": default_user_password,
            },
        )
        assert (
            patch_revert_user_one_password_to_default_success_response.status_code
            == 200
        )

        # try to update user1 password with same current password
        # should fail as password and confirm password do not match is provided
        patch_user_one_password_change_with_same_current_password_fail_response = test_client.patch(
            f"{BASE_AUTH_URL_PREFIX}/password?otp_token={user_one_password_change_otp_token}",
            headers={"Authorization": f"Bearer {access_token}"},
            json={
                "password": default_user_password,
                "confirm_password": default_user_password,
            },
        )
        assert (
            patch_user_one_password_change_with_same_current_password_fail_response.status_code
            == 422
        )

    async def test_user_hidden_status_update(self, test_client):
        """
        test user hidden status update
        """
        user_one_access_token = self.user_access_tokens.get(self.user_one_email)
        ################################ LOGIN USER1 ########################################
        # retrive current user one details
        get_user_one_info_before_privacy_status_update_response = test_client.get(
            f"{BASE_AUTH_URL_PREFIX}/privacy",
            headers={"Authorization": f"Bearer {user_one_access_token}"},
        )
        assert (
            get_user_one_info_before_privacy_status_update_response.status_code == 200
        )
        user_one_info_before_privacy_status_update_json = (
            get_user_one_info_before_privacy_status_update_response.json()
        )
        assert {"is_hidden"} == user_one_info_before_privacy_status_update_json.keys()
        initial_user_one_hidden_status_before_first_toggle = (
            user_one_info_before_privacy_status_update_json.get("is_hidden")
        )
        # is_hidden status must be False by default
        assert initial_user_one_hidden_status_before_first_toggle is False

        # update user one privacy status
        # endpoint works as toggle and sets to user's hidden status to it's opposite i.e true to false and vice versa
        patch_user_one_privacy_status_update_response = test_client.patch(
            f"{BASE_AUTH_URL_PREFIX}/privacy",
            headers={"Authorization": f"Bearer {user_one_access_token}"},
        )
        assert patch_user_one_privacy_status_update_response.status_code == 200
        user_one_privacy_status_update_json = (
            patch_user_one_privacy_status_update_response.json()
        )
        assert {"is_hidden"} == user_one_privacy_status_update_json.keys()
        user_one_privacy_status_is_hidden_status = (
            user_one_privacy_status_update_json.get("is_hidden")
        )
        assert (
            user_one_privacy_status_is_hidden_status
            is not initial_user_one_hidden_status_before_first_toggle
        )

        # retrive current user one details after switch
        get_user_one_info_after_privacy_status_update_response = test_client.get(
            f"{BASE_AUTH_URL_PREFIX}/privacy",
            headers={"Authorization": f"Bearer {user_one_access_token}"},
        )
        assert get_user_one_info_after_privacy_status_update_response.status_code == 200
        user_one_info_after_privacy_status_update_json = (
            get_user_one_info_after_privacy_status_update_response.json()
        )
        assert {"is_hidden"} == user_one_info_after_privacy_status_update_json.keys()
        user_one_hidden_status_after_update = (
            user_one_info_after_privacy_status_update_json.get("is_hidden")
        )
        # is_hidden status must be False by default
        assert (
            user_one_hidden_status_after_update
            is not initial_user_one_hidden_status_before_first_toggle
        )

        # revert user hidden status to default for future tests
        patch_user_one_privacy_status_update_to_reset_response = test_client.patch(
            f"{BASE_AUTH_URL_PREFIX}/privacy",
            headers={"Authorization": f"Bearer {user_one_access_token}"},
        )
        assert patch_user_one_privacy_status_update_to_reset_response.status_code == 200
        user_one_hidden_status_after_reset = (
            patch_user_one_privacy_status_update_to_reset_response.json().get(
                "is_hidden"
            )
        )
        # confirm that is_hidden status now matches the initial after reversion
        assert (
            user_one_hidden_status_after_reset
            is initial_user_one_hidden_status_before_first_toggle
        )

    async def test_user_bio_details_update(self, test_client):
        """
        test user bio information update
        """
        user_one_access_token = self.user_access_tokens.get(self.user_one_email)
        ################################ LOGIN USER1 ########################################
        # retrive current user one details
        get_user_one_info_before_updates_response = test_client.get(
            f"{BASE_USER_URL_PREFIX}",
            headers={"Authorization": f"Bearer {user_one_access_token}"},
        )
        assert get_user_one_info_before_updates_response.status_code == 200
        user_one_info_before_updates = get_user_one_info_before_updates_response.json()

        # test bion details update
        user_one_update_data_unchanged = {
            "first_name": user_one_info_before_updates.get("first_name"),
            "last_name": user_one_info_before_updates.get("last_name"),
            "username": user_one_info_before_updates.get("username"),
            "bio": user_one_info_before_updates.get("bio"),
            "is_hidden": user_one_info_before_updates.get("is_hidden"),
        }
        new_first_name = "newton"
        new_last_name = "lastman"
        new_username = "user1newnam3"
        new_bio = "this is the new bio of user1"
        new_is_hidden = not user_one_info_before_updates.get("is_hidden")

        # update bio data with new first name
        user_update_data_changed_first_name = user_one_update_data_unchanged.copy()
        user_update_data_changed_first_name.update({"first_name": new_first_name})

        user_update_data_changed_last_name = user_one_update_data_unchanged.copy()
        user_update_data_changed_last_name.update({"last_name": new_last_name})

        user_update_data_changed_username = user_one_update_data_unchanged.copy()
        user_update_data_changed_username.update({"username": new_username})

        user_update_data_changed_bio = user_one_update_data_unchanged.copy()
        user_update_data_changed_bio.update({"bio": new_bio})

        user_update_data_changed_is_hidden = user_one_update_data_unchanged.copy()
        user_update_data_changed_is_hidden.update({"is_hidden": new_is_hidden})

        # update bio data with the exact same signup information
        # should fail as no change in any field
        patch_user_one_update_bio_data_with_unchanged_data_failed_response = (
            test_client.patch(
                f"{BASE_AUTH_URL_PREFIX}",
                headers={"Authorization": f"Bearer {user_one_access_token}"},
                json=user_one_update_data_unchanged,
            )
        )
        assert (
            patch_user_one_update_bio_data_with_unchanged_data_failed_response.status_code
            == 422
        )

        # update data with new first name
        patch_user_one_update_bio_data_with_only_changed_first_name_response = (
            test_client.patch(
                f"{BASE_AUTH_URL_PREFIX}",
                headers={"Authorization": f"Bearer {user_one_access_token}"},
                json=user_update_data_changed_first_name,
            )
        )
        assert (
            patch_user_one_update_bio_data_with_only_changed_first_name_response.status_code
            == 200
        )
        assert (
            patch_user_one_update_bio_data_with_only_changed_first_name_response.json().keys()
            == USER_COMPLETE_KEYS
        )
        # confirm user first name changed
        get_user_one_info_to_check_first_name_change_response = test_client.get(
            f"{BASE_USER_URL_PREFIX}",
            headers={"Authorization": f"Bearer {user_one_access_token}"},
        )
        assert get_user_one_info_to_check_first_name_change_response.status_code == 200
        user_one_first_name = (
            get_user_one_info_to_check_first_name_change_response.json().get(
                "first_name"
            )
        )
        assert user_one_first_name == new_first_name.title()

        # update data with new last name
        patch_user_one_update_bio_data_with_only_changed_last_name_response = (
            test_client.patch(
                f"{BASE_AUTH_URL_PREFIX}",
                headers={"Authorization": f"Bearer {user_one_access_token}"},
                json=user_update_data_changed_last_name,
            )
        )
        assert (
            patch_user_one_update_bio_data_with_only_changed_last_name_response.status_code
            == 200
        )
        # confirm user first name changed
        get_user_one_info_to_check_last_name_change = test_client.get(
            f"{BASE_USER_URL_PREFIX}",
            headers={"Authorization": f"Bearer {user_one_access_token}"},
        )
        assert get_user_one_info_to_check_last_name_change.status_code == 200
        user_one_last_name = get_user_one_info_to_check_last_name_change.json().get(
            "last_name"
        )
        assert user_one_last_name == new_last_name.title()

        # update data with new username
        patch_user_one_update_bio_data_with_only_changed_username_response = (
            test_client.patch(
                f"{BASE_AUTH_URL_PREFIX}",
                headers={"Authorization": f"Bearer {user_one_access_token}"},
                json=user_update_data_changed_username,
            )
        )
        assert (
            patch_user_one_update_bio_data_with_only_changed_username_response.status_code
            == 200
        )
        # confirm user username changed
        get_user_one_info_to_check_username_change = test_client.get(
            f"{BASE_USER_URL_PREFIX}",
            headers={"Authorization": f"Bearer {user_one_access_token}"},
        )
        assert get_user_one_info_to_check_username_change.status_code == 200
        user_one_username = get_user_one_info_to_check_username_change.json().get(
            "username"
        )
        assert user_one_username == new_username.lower()

        # update data with new bio
        patch_user_one_update_bio_data_with_only_changed_bio_response = (
            test_client.patch(
                f"{BASE_AUTH_URL_PREFIX}",
                headers={"Authorization": f"Bearer {user_one_access_token}"},
                json=user_update_data_changed_bio,
            )
        )
        assert (
            patch_user_one_update_bio_data_with_only_changed_bio_response.status_code
            == 200
        )
        # confirm user bio changed
        get_user_one_info_to_check_bio_change = test_client.get(
            f"{BASE_USER_URL_PREFIX}",
            headers={"Authorization": f"Bearer {user_one_access_token}"},
        )
        assert get_user_one_info_to_check_bio_change.status_code == 200
        user_one_bio = get_user_one_info_to_check_bio_change.json().get("bio")
        assert user_one_bio == new_bio

        # update data with new is_hidden
        patch_user_one_update_bio_data_with_only_changed_is_hidden_response = (
            test_client.patch(
                f"{BASE_AUTH_URL_PREFIX}",
                headers={"Authorization": f"Bearer {user_one_access_token}"},
                json=user_update_data_changed_is_hidden,
            )
        )
        assert (
            patch_user_one_update_bio_data_with_only_changed_is_hidden_response.status_code
            == 200
        )
        # confirm user first name changed
        get_user_one_info_to_check_is_hidden_change_response = test_client.get(
            f"{BASE_USER_URL_PREFIX}",
            headers={"Authorization": f"Bearer {user_one_access_token}"},
        )
        assert get_user_one_info_to_check_is_hidden_change_response.status_code == 200
        user_one_is_hidden = (
            get_user_one_info_to_check_is_hidden_change_response.json().get("is_hidden")
        )
        assert user_one_is_hidden == new_is_hidden

        # update data with new unchanged
        patch_user_one_update_bio_data_with_unchanged_data_response = test_client.patch(
            f"{BASE_AUTH_URL_PREFIX}",
            headers={"Authorization": f"Bearer {user_one_access_token}"},
            json=user_one_update_data_unchanged,
        )
        assert (
            patch_user_one_update_bio_data_with_unchanged_data_response.status_code
            == 200
        )
        # confirm user first name changed
        get_user_one_info_to_check_unchanged_data_response = test_client.get(
            f"{BASE_USER_URL_PREFIX}",
            headers={"Authorization": f"Bearer {user_one_access_token}"},
        )
        assert get_user_one_info_to_check_unchanged_data_response.status_code == 200
        user_one_data_after_reset_updates = (
            get_user_one_info_to_check_unchanged_data_response.json()
        )
        assert user_one_info_before_updates == user_one_data_after_reset_updates

        ################################ LOGIN USER1 ########################################

    def test_user_account_delete(self, test_client):
        """
        test user account delete mechanism using user4
        """
        user_four_access_token = self.user_access_tokens[self.user_four_email]
        user_four_uid = self.user_four_uid
        user_four_username = self.user_four_signup_data["username"]

        ###!!! IMPORTANT !!!###
        # valid delete text must be  "i {username} want to delete my account"
        invalid_account_delete_confirmation_text = "just delete the account"
        valid_account_delete_confirmation_text = (
            f"i {user_four_username} want to delete my account"
        )

        ################################ LOGIN USER4 ########################################
        # logged in as user4
        # retrieve user4 info before deletion user details to confirm user exists
        get_user_four_info_before_deletion_response = test_client.get(
            f"{BASE_USER_URL_PREFIX}",
            headers={"Authorization": f"Bearer {user_four_access_token}"},
        )
        assert get_user_four_info_before_deletion_response.status_code == 200
        user_uid_for_user_four_info = (
            get_user_four_info_before_deletion_response.json().get("uid")
        )
        assert user_uid_for_user_four_info == user_four_uid

        # try to delete user account without cofirmation form
        # should fail as user must submit confirmation form
        delete_user_four_account_without_confirmation_form_failed_response = (
            test_client.post(
                f"{BASE_AUTH_URL_PREFIX}/confirm_delete",
                headers={"Authorization": f"Bearer {user_four_access_token}"},
            )
        )
        assert (
            delete_user_four_account_without_confirmation_form_failed_response.status_code
            == 422
        )

        # try to delete user account with invalid confirmation message
        # should fail as confirmation text is invalid
        delete_user_four_account_with_invalid_confirmation_form_failed_response = (
            test_client.post(
                f"{BASE_AUTH_URL_PREFIX}/confirm_delete",
                headers={"Authorization": f"Bearer {user_four_access_token}"},
                json={"text": invalid_account_delete_confirmation_text},
            )
        )
        assert (
            delete_user_four_account_with_invalid_confirmation_form_failed_response.status_code
            == 422
        )

        # try to delete user account with valid confirmation message
        # should fail as confirmation text is valid
        delete_user_four_account_with_valid_confirmation_form_failed_response = (
            test_client.post(
                f"{BASE_AUTH_URL_PREFIX}/confirm_delete",
                headers={"Authorization": f"Bearer {user_four_access_token}"},
                json={"text": valid_account_delete_confirmation_text},
            )
        )
        assert (
            delete_user_four_account_with_valid_confirmation_form_failed_response.status_code
            == 200
        )

        # retrieve user4 info after deletion user details to confirm user does not exist
        get_user_four_info_after_deletion_response = test_client.get(
            f"{BASE_USER_URL_PREFIX}",
            headers={"Authorization": f"Bearer {user_four_access_token}"},
        )
        # confirm user is unathorized even with auth header as user4 account no longer exists
        assert get_user_four_info_after_deletion_response.status_code == 401

        ################################ LOGOUT USER4 ########################################
