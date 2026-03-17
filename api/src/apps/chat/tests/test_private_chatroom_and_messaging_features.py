import re

import pytest

from src.apps.user.tests.base_test_user_integrations import BaseTestUserIntegrations
from src.apps.auth.tests.base_test_user_signup_login_jwt import BaseTestUserSignupLogin

# from src.apps.auth.tests.base_test_user_signup_login_jwt import BaseTestUserSignupLogin
from src.tests.conftest import test_client, r_client
from fastapi import status

BASE_CHAT_URL_PREFIX = "/chat"
PRIVATE_CHAT_URL_PREFIX = f"{BASE_CHAT_URL_PREFIX}/private/room"
BASE_AUTH_URL_PREFIX = "/auth"
PRIVATE_CHATROOM_KEYWORD = "private"
PUBLIC_CHATROOM_KEYWORD = "public"
GENERAL_CHATROOM_KEYWORD = "chat_keyword"

PRIVATE_CHATROOM_PASSWORD = "comPl3x-passw0rd"

EXPECTED_CHATROOM_DETAILS_KEYS = {
    "uid",
    "name",
    "about",
    "created_at",
    "modified_at",
    "original_creator_username",
    "room_type",
    "members_count",
    "record_messages",
}


class TestPrivateChatroomAndMessagingFeatures(BaseTestUserIntegrations):

    def setup_method(self):
        self.private_chatroom_one_create_data = {
            "name": f"first ever zzzz{PRIVATE_CHATROOM_KEYWORD}{GENERAL_CHATROOM_KEYWORD}zzzz chatroom",
            "about": "this is a proper private chatroom with password provided.",
            "room_type": "private",
        }
        self.public_chatroom_one_create_data = {
            "name": f"first ever zzzzz{PUBLIC_CHATROOM_KEYWORD}{GENERAL_CHATROOM_KEYWORD}dmkkj chatroom",
            "about": "this is a public chatroom",
            "room_type": "public",
        }

    def test_create_private_and_public_chatroom(self, test_client):
        """
        test chatroom creation and websocket messaging
        """

        # login test assertions have already been made in BaseTestUserSigupLogin class
        ### CREATE PRIVATE CHATROOM - USER ONE

        # create chatroom with base data which does not contain password values
        post_create_private_chatroom_without_password_failed_response = (
            test_client.post(
                f"{BASE_CHAT_URL_PREFIX}?anon_username=anonymoususer1",
                json=self.private_chatroom_one_create_data,
                headers={"Authorization": f"Bearer {self.user_one_access_token}"},
            )
        )
        assert (
            post_create_private_chatroom_without_password_failed_response.status_code
            == 422
        )

        create_data_with_password = self.private_chatroom_one_create_data.copy()
        create_data_with_password.update({"password": PRIVATE_CHATROOM_PASSWORD})
        post_create_private_chatroom_with_password_and_without_confirm_password_failed_response = test_client.post(
            f"{BASE_CHAT_URL_PREFIX}?anon_username=anonymoususer1",
            json=create_data_with_password,
            headers={"Authorization": f"Bearer {self.user_one_access_token}"},
        )
        assert (
            post_create_private_chatroom_with_password_and_without_confirm_password_failed_response.status_code
            == 422
        )

        create_data_with_password_and_incorrect_confirm_password = (
            self.private_chatroom_one_create_data.copy()
        )
        create_data_with_password_and_incorrect_confirm_password.update(
            {
                "password": PRIVATE_CHATROOM_PASSWORD,
                "confirm_password": "INc0rr3ct-Confirm",
            }
        )
        post_create_private_chatroom_with_password_and_inccorrect_confirm_password_failed_response = test_client.post(
            f"{BASE_CHAT_URL_PREFIX}?anon_username=anonymoususer1",
            json=create_data_with_password_and_incorrect_confirm_password,
            headers={"Authorization": f"Bearer {self.user_one_access_token}"},
        )
        assert (
            post_create_private_chatroom_with_password_and_inccorrect_confirm_password_failed_response.status_code
            == 422
        )

        create_data_with_password_and_correct_confirm_password = (
            self.private_chatroom_one_create_data.copy()
        )
        create_data_with_password_and_correct_confirm_password.update(
            {
                "password": PRIVATE_CHATROOM_PASSWORD,
                "confirm_password": PRIVATE_CHATROOM_PASSWORD,
            }
        )
        post_create_private_chatroom_with_password_and_correct_confirm_password_success_response = test_client.post(
            f"{BASE_CHAT_URL_PREFIX}?anon_username=anonymoususer1",
            json=create_data_with_password_and_correct_confirm_password,
            headers={"Authorization": f"Bearer {self.user_one_access_token}"},
        )
        assert (
            post_create_private_chatroom_with_password_and_correct_confirm_password_success_response.status_code
            == 201
        )

        chatroom_success_details_dict = (
            post_create_private_chatroom_with_password_and_correct_confirm_password_success_response.json()
        )

        assert EXPECTED_CHATROOM_DETAILS_KEYS.issubset(
            set(chatroom_success_details_dict.keys())
        )
        # confirm that creator username
        # should match user1 username as user1 is not hidden
        assert (
            chatroom_success_details_dict.get("original_creator_username")
            == self.user_one_username
        )
        # confirm that chatroom has 1 member
        # user1 is the only member as logged in user must be automatically added to chatroom on creation
        assert chatroom_success_details_dict.get("members_count") == 1
        assert chatroom_success_details_dict.get("room_type") == "private"
        assert chatroom_success_details_dict.get("record_messages") == True
        assert (
            chatroom_success_details_dict.get("original_creator_username")
            == self.user_one_username
        )

        self.__class__.user_one_private_chatroom_one_uid = (
            chatroom_success_details_dict["uid"]
        )

        ### CREATE PUBLIC CHATROOM - USER ONE
        post_create_public_chatroom_success_response = test_client.post(
            f"{BASE_CHAT_URL_PREFIX}?anon_username={self.user_one_username}",
            json=self.public_chatroom_one_create_data,
            headers={"Authorization": f"Bearer {self.user_one_access_token}"},
        )
        assert post_create_public_chatroom_success_response.status_code == 201
        public_chatroom_created_json = (
            post_create_public_chatroom_success_response.json()
        )
        assert (
            public_chatroom_created_json.get("original_creator_username")
            == self.user_one_username
        )
        assert public_chatroom_created_json.get("members_count") == 1
        assert public_chatroom_created_json.get("room_type") == "public"
        assert public_chatroom_created_json.get("record_messages") == True

        self.__class__.user_one_public_chatroom_one_uid = public_chatroom_created_json[
            "uid"
        ]

        ### get chatrooms user1 has joined

        # get all joined chatrooms
        get_user_one_all_joined_chatrooms_response = test_client.get(
            f"{PRIVATE_CHAT_URL_PREFIX}/all",
            headers={"Authorization": f"Bearer {self.user_one_access_token}"},
        )
        assert get_user_one_all_joined_chatrooms_response.status_code == 200
        user_one_all_joined_chatrooms_json = (
            get_user_one_all_joined_chatrooms_response.json()
        )
        assert "chatrooms" in user_one_all_joined_chatrooms_json.keys()
        user_one_all_joined_chatrooms_list = user_one_all_joined_chatrooms_json.get(
            "chatrooms"
        )
        # length should be 2 as user 2 created 2 chatrooms
        # logged in user is added to chatroom on creation, regardless of chatroom type
        assert len(user_one_all_joined_chatrooms_list) == 2

        # get all created by user1
        get_user_one_all_owned_chatrooms_response = test_client.get(
            f"{PRIVATE_CHAT_URL_PREFIX}/all?role=creator",
            headers={"Authorization": f"Bearer {self.user_one_access_token}"},
        )
        user_one_all_owned_chatrooms = (
            get_user_one_all_owned_chatrooms_response.json().get("chatrooms")
        )
        # length should be 2 as user1 created only 2 chatroom
        assert len(user_one_all_owned_chatrooms) == 2

        # get all public chatrooms created by user1
        get_user_one_all_owned_public_chatrooms_response = test_client.get(
            f"{PRIVATE_CHAT_URL_PREFIX}/all?role=creator&room_type=public",
            headers={"Authorization": f"Bearer {self.user_one_access_token}"},
        )
        user_one_all_owned_public_chatrooms = (
            get_user_one_all_owned_public_chatrooms_response.json().get("chatrooms")
        )
        # length should be 1 as user1 has created only 1 public chatroom
        assert len(user_one_all_owned_public_chatrooms) == 1

        # get all private chatrooms created by user1
        get_user_one_all_owned_private_chatrooms_response = test_client.get(
            f"{PRIVATE_CHAT_URL_PREFIX}/all?role=creator&room_type=private",
            headers={"Authorization": f"Bearer {self.user_one_access_token}"},
        )
        user_one_all_owned_private_chatrooms = (
            get_user_one_all_owned_private_chatrooms_response.json().get("chatrooms")
        )
        # length should be 1 as user1 has created only 1 private chatroom
        assert len(user_one_all_owned_private_chatrooms) == 1

        # get all private chatrooms only
        # owned and un-owned
        get_user_one_all_joined_private_chatrooms_response = test_client.get(
            f"{PRIVATE_CHAT_URL_PREFIX}/all?room_type=private",
            headers={"Authorization": f"Bearer {self.user_one_access_token}"},
        )
        user_one_all_joined_private_chatrooms = (
            get_user_one_all_joined_private_chatrooms_response.json().get("chatrooms")
        )
        # length should be 1 as  user1 has joined only 1 private chatroom
        assert len(user_one_all_joined_private_chatrooms) == 1
        # confirm that the only chatroom is truly the private chatroom
        assert (
            user_one_all_joined_private_chatrooms[0].get("uid")
            == self.user_one_private_chatroom_one_uid
        )

        # get public chatrooms only
        # owned and un-owned
        get_user_one_all_joined_public_chatrooms_response = test_client.get(
            f"{PRIVATE_CHAT_URL_PREFIX}/all?room_type=public",
            headers={"Authorization": f"Bearer {self.user_one_access_token}"},
        )
        user_one_all_joined_public_chatrooms = (
            get_user_one_all_joined_public_chatrooms_response.json().get("chatrooms")
        )
        # length should be 1 as user1 has joined only 1 public chatroom
        assert len(user_one_all_joined_public_chatrooms) == 1
        # confirm that the only chatroom is truly the public chatroom
        assert (
            user_one_all_joined_public_chatrooms[0].get("uid")
            == self.user_one_public_chatroom_one_uid
        )

        # test chatroom search endpoint for uid search
        # should work without auth header

        # search for the two chatrooms
        created_chatrooms_uid_list = [
            self.user_one_private_chatroom_one_uid,
            self.user_one_public_chatroom_one_uid,
        ]
        created_chatrooms_uid_list_string = ",".join(created_chatrooms_uid_list)
        get_chatrooms_with_matching_uids_response = test_client.get(
            f"{BASE_CHAT_URL_PREFIX}/all?id={created_chatrooms_uid_list_string}"
        )
        assert get_chatrooms_with_matching_uids_response.status_code == 200
        get_chatrooms_with_matching_uids_json = (
            get_chatrooms_with_matching_uids_response.json()
        )
        all_chatrooms_with_matching_uids = get_chatrooms_with_matching_uids_json.get(
            "chatrooms"
        )
        # confirm that exactly two matching chatrooms were found
        assert len(all_chatrooms_with_matching_uids) == 2
        # confirm return has correct keys
        expected_chatroom_extended_keys = EXPECTED_CHATROOM_DETAILS_KEYS.copy()
        expected_chatroom_extended_keys.update(
            ["user_status", "user_is_hidden", "active_visitors"]
        )
        assert (
            expected_chatroom_extended_keys
            == dict(all_chatrooms_with_matching_uids[0]).keys()
        )
        # confirm matching chatrooms having uids matching query
        for matching_chatroom in all_chatrooms_with_matching_uids:
            assert "uid" in matching_chatroom.keys()
            assert matching_chatroom["uid"] in created_chatrooms_uid_list

        # get user_one_private_chatroom_one_uid only
        get_private_chatroom_one_as_user_one_logged_in_response = test_client.get(
            f"{BASE_CHAT_URL_PREFIX}/all?id={self.user_one_private_chatroom_one_uid}",
            headers={"Authorization": f"Bearer {self.user_one_access_token}"},
        )
        assert (
            get_private_chatroom_one_as_user_one_logged_in_response.status_code == 200
        )
        matching_private_chatroom_one_json = (
            get_private_chatroom_one_as_user_one_logged_in_response.json()
        )
        chatrooms_matching_private_one_uid = matching_private_chatroom_one_json.get(
            "chatrooms"
        )
        # confirm that only exacly one chatroom matches search
        assert len(chatrooms_matching_private_one_uid) == 1
        # confirm that matching chatroom uid matches actual user_one_private_chatroom_one_uid
        assert (
            chatrooms_matching_private_one_uid[0].get("uid")
            == self.user_one_private_chatroom_one_uid
        )
        # check user_status value while logged in as user1
        # user_status should be "creator" as user1 is the chatroom creator
        assert chatrooms_matching_private_one_uid[0].get("user_status") == "creator"

        # get user_one_private_chatroom_one_uid while logged out
        get_private_chatroom_one_while_logged_out_response = test_client.get(
            f"{BASE_CHAT_URL_PREFIX}/all?id={self.user_one_private_chatroom_one_uid}",
        )
        # check user_status value while logged out
        # user_status should be "creator" as user1 is the chatroom creator
        assert get_private_chatroom_one_while_logged_out_response.status_code == 200
        chatroom_one_while_logged_out_json = (
            get_private_chatroom_one_while_logged_out_response.json().get("chatrooms")[
                0
            ]
        )
        assert chatroom_one_while_logged_out_json.get("user_status") == "removed"

        # get user_one_public_chatroom_one_uid only
        get_public_chatroom_one_response_as_user_one_logged_in_response = test_client.get(
            f"{BASE_CHAT_URL_PREFIX}/all?id={self.user_one_public_chatroom_one_uid}",
            headers={"Authorization": f"Bearer {self.user_one_access_token}"},
        )
        assert (
            get_public_chatroom_one_response_as_user_one_logged_in_response.status_code
            == 200
        )
        matching_public_chatroom_one_json = (
            get_public_chatroom_one_response_as_user_one_logged_in_response.json()
        )
        chatrooms_matching_public_one_uid = matching_public_chatroom_one_json.get(
            "chatrooms"
        )
        # confirm that only exacly one chatroom matches search
        assert len(chatrooms_matching_public_one_uid) == 1
        # confirm that matching chatroom uid matches actual user_one_public_chatroom_one_uid
        assert (
            chatrooms_matching_public_one_uid[0].get("uid")
            == self.user_one_public_chatroom_one_uid
        )
        assert chatrooms_matching_public_one_uid[0].get("user_status") == "creator"

        # user1 is the logged in user therefore the expected original creator username must match
        self.__class__.all_chatrooms_original_creator_username = self.user_one_username

    def test_chatroom_search(self, test_client):
        """
        test chatroom search endpoint.
        endpoint should allow search for chatrooms with search query matching chatroom name,
        and/or matching original creator username.
        endpoint should not require login.
        search keywords can be in any case to find matches.
        """
        ### recall that 2 chatrooms were created. one private, one public.
        # each with respective keyword variables positioned randomly their f-string names
        # searches will be carried out using these keyword variables

        ### search for chatroom

        # search with unmatching keyword
        # none should be found
        ################

        # search with private chatroom keyword
        keyword_that_matches_no_created_chatroom = "randomword"
        get_matching_searched_chatrooms_response = test_client.get(
            f"{BASE_CHAT_URL_PREFIX}/search?search_query={keyword_that_matches_no_created_chatroom}"
        )
        assert get_matching_searched_chatrooms_response.status_code == 200
        assert "chatrooms" in get_matching_searched_chatrooms_response.json().keys()
        # confirm that no matching chatroom was found
        empty_matching_chatrooms_list = (
            get_matching_searched_chatrooms_response.json().get("chatrooms")
        )
        assert len(empty_matching_chatrooms_list) == 0

        # search using uppercase keyword added to private chatroom one name on creation
        get_matching_chatrooms_with_uppercase_private_keyword_response = test_client.get(
            f"{BASE_CHAT_URL_PREFIX}/search?search_query={PRIVATE_CHATROOM_KEYWORD.upper()}"
        )
        assert (
            get_matching_chatrooms_with_uppercase_private_keyword_response.status_code
            == 200
        )
        matching_chatrooms_with_uppercase_private_keyword = (
            get_matching_chatrooms_with_uppercase_private_keyword_response.json().get(
                "chatrooms"
            )
        )
        # confirm that only 1 chatroom matched the private chatroom keyword
        # the private chatroom was the only one to be created with this keyword
        assert len(matching_chatrooms_with_uppercase_private_keyword) == 1
        # confirm that the one matching chatroom from uppercase search is the only private chatroom created
        uppercase_search_matching_chatroom_uid = (
            matching_chatrooms_with_uppercase_private_keyword[0].get("uid")
        )
        assert (
            uppercase_search_matching_chatroom_uid
            == self.user_one_private_chatroom_one_uid
        )

        # search using lowercase keyword added to private chatroom one name on creation
        get_matching_chatrooms_with_lowercase_private_keyword_response = test_client.get(
            f"{BASE_CHAT_URL_PREFIX}/search?search_query={PRIVATE_CHATROOM_KEYWORD.lower()}"
        )
        assert (
            get_matching_chatrooms_with_lowercase_private_keyword_response.status_code
            == 200
        )
        matching_chatrooms_with_lowercase_private_keyword = (
            get_matching_chatrooms_with_lowercase_private_keyword_response.json().get(
                "chatrooms"
            )
        )
        # confirm that only 1 chatroom matched the private chatroom keyword
        # the private chatroom was the only one to be created with this keyword
        assert len(matching_chatrooms_with_lowercase_private_keyword) == 1
        # confirm that the one matching chatroom from lowercase search is the only private chatroom created
        lowercase_search_matching_chatroom_uid = (
            matching_chatrooms_with_lowercase_private_keyword[0].get("uid")
        )
        assert (
            lowercase_search_matching_chatroom_uid
            == self.user_one_private_chatroom_one_uid
        )

        # search using fragment of keyword added to private chatroom one name on creation
        get_matching_chatrooms_with_fragment_of_private_keyword_response = test_client.get(
            f"{BASE_CHAT_URL_PREFIX}/search?search_query={PRIVATE_CHATROOM_KEYWORD[2:6]}"
        )
        assert (
            get_matching_chatrooms_with_fragment_of_private_keyword_response.status_code
            == 200
        )
        matching_chatrooms_with_fragment_of_private_keyword = (
            get_matching_chatrooms_with_fragment_of_private_keyword_response.json().get(
                "chatrooms"
            )
        )
        # confirm that only 1 chatroom matched the private chatroom keyword
        assert len(matching_chatrooms_with_fragment_of_private_keyword) == 1
        # confirm that the one matching chatroom from fragment search is the only private chatroom created
        fragment_search_matching_chatroom_uid = (
            matching_chatrooms_with_fragment_of_private_keyword[0].get("uid")
        )
        assert (
            fragment_search_matching_chatroom_uid
            == self.user_one_private_chatroom_one_uid
        )

        # search with public chatroom keyword
        # search in titlecase. recall search should work case-insensitively
        # search using fragment of keyword added to private chatroom one name on creation
        get_matching_chatrooms_with_titlecase_public_keyword_response = test_client.get(
            f"{BASE_CHAT_URL_PREFIX}/search?search_query={PUBLIC_CHATROOM_KEYWORD.title()}"
        )
        assert (
            get_matching_chatrooms_with_titlecase_public_keyword_response.status_code
            == 200
        )
        matching_chatrooms_with_titlecase_public_keyword = (
            get_matching_chatrooms_with_titlecase_public_keyword_response.json().get(
                "chatrooms"
            )
        )
        # confirm that only 1 chatroom matched the public chatroom keyword
        assert len(matching_chatrooms_with_titlecase_public_keyword) == 1
        # confirm that the one matching chatroom from titlecase search is the only public chatroom created
        titlecase_search_matching_chatroom_uid = (
            matching_chatrooms_with_titlecase_public_keyword[0].get("uid")
        )
        assert (
            titlecase_search_matching_chatroom_uid
            == self.user_one_public_chatroom_one_uid
        )

        ################
        # test search with general keyword

        # search with general chatroom keyword
        # search in general. recall search should work case-insensitively
        # search using fragment of keyword added to private chatroom one name on creation
        get_matching_chatrooms_with_general_keyword_response = test_client.get(
            f"{BASE_CHAT_URL_PREFIX}/search?search_query={GENERAL_CHATROOM_KEYWORD.title()}"
        )
        assert get_matching_chatrooms_with_general_keyword_response.status_code == 200
        matching_chatrooms_with_general_keyword = (
            get_matching_chatrooms_with_general_keyword_response.json().get("chatrooms")
        )
        # confirm that 2 chatroom matched the general chatroom keyword
        # only 2 chatrooms were created and each contained the keyword in name on creation
        assert len(matching_chatrooms_with_general_keyword) == 2
        # confirm that the one matching chatroom from general search is the only general chatroom created
        for chatroom in matching_chatrooms_with_general_keyword:
            matching_uid = chatroom.get("uid")
            assert matching_uid in [
                self.user_one_public_chatroom_one_uid,
                self.user_one_private_chatroom_one_uid,
            ]

        ################

        ################

        # test search with creator username
        creator_username = str(self.all_chatrooms_original_creator_username)

        # search with uppercase creator username
        # search in uppercase_creator_username. recall search should work case-insensitively
        # search using fragment of keyword added to private chatroom one name on creation
        get_matching_chatrooms_with_uppercase_creator_username_keyword_response = (
            test_client.get(
                f"{BASE_CHAT_URL_PREFIX}/search?search_query={creator_username.upper()}"
            )
        )
        assert (
            get_matching_chatrooms_with_uppercase_creator_username_keyword_response.status_code
            == 200
        )
        matching_chatrooms_with_uppercase_creator_username_keyword = get_matching_chatrooms_with_uppercase_creator_username_keyword_response.json().get(
            "chatrooms"
        )
        # confirm that 2 chatroom matched the uppercase_creator_username chatroom keyword
        # only 2 chatrooms were created by user with username matching creator username
        assert len(matching_chatrooms_with_uppercase_creator_username_keyword) == 2
        # confirm that the one matching chatroom from uppercase_creator_username search is the only uppercase_creator_username chatroom created
        for chatroom in matching_chatrooms_with_uppercase_creator_username_keyword:
            matching_uid = chatroom.get("uid")
            assert matching_uid in [
                self.user_one_public_chatroom_one_uid,
                self.user_one_private_chatroom_one_uid,
            ]

        # search with lowercase creator username
        # search in lowercase_creator_username. recall search should work case-insensitively
        # search using fragment of keyword added to private chatroom one name on creation
        get_matching_chatrooms_with_lowercase_creator_username_keyword_response = (
            test_client.get(
                f"{BASE_CHAT_URL_PREFIX}/search?search_query={creator_username.lower()}"
            )
        )
        assert (
            get_matching_chatrooms_with_lowercase_creator_username_keyword_response.status_code
            == 200
        )
        matching_chatrooms_with_lowercase_creator_username_keyword = get_matching_chatrooms_with_lowercase_creator_username_keyword_response.json().get(
            "chatrooms"
        )
        # confirm that 2 chatroom matched the lowercase_creator_username chatroom keyword
        # only 2 chatrooms were created by user with username matching creator username
        assert len(matching_chatrooms_with_lowercase_creator_username_keyword) == 2
        # confirm that the one matching chatroom from lowercase_creator_username search is the only lowercase_creator_username chatroom created
        for chatroom in matching_chatrooms_with_lowercase_creator_username_keyword:
            matching_uid = chatroom.get("uid")
            assert matching_uid in [
                self.user_one_public_chatroom_one_uid,
                self.user_one_private_chatroom_one_uid,
            ]

        ################

    def test_chatroom_privacy_enforcement_and_get_chatroom_messages_for_user_two(
        self, test_client
    ):
        """
        test get messages endpoint logged in as user 2
        chatroom was created by user 1
        """
        ################################ LOGIN USER2

        # try to retrieve messages to test privacy enforcement
        # try to retrieve messages without authorization header
        get_chatroom_messages_unauthorized_response = test_client.get(
            f"{BASE_CHAT_URL_PREFIX}/messages/{self.user_one_private_chatroom_one_uid}",
        )
        assert get_chatroom_messages_unauthorized_response.status_code == 401

        # try to retrieve messages to test privacy enforcement
        # try to retrieve messages with authorization header
        # should fail as user is not a member of the chatroom
        get_chatroom_messages_as_authorized_non_member_response = test_client.get(
            f"{BASE_CHAT_URL_PREFIX}/messages/{self.user_one_private_chatroom_one_uid}/",
            headers={"Authorization": f"Bearer {self.user_two_access_token}"},
        )
        assert (
            get_chatroom_messages_as_authorized_non_member_response.status_code == 403
        )

        # try to join without authorization header
        post_join_chatroom_as_unauthorized_response = test_client.post(
            f"{PRIVATE_CHAT_URL_PREFIX}/join/{self.user_one_private_chatroom_one_uid}"
        )
        assert post_join_chatroom_as_unauthorized_response.status_code == 401

        # try to join with authorization header
        # should fail as user is supposed to provide a password to join
        post_no_password_join_chatroom_with_password_fail_response = test_client.post(
            f"{PRIVATE_CHAT_URL_PREFIX}/join/{self.user_one_private_chatroom_one_uid}",
            headers={"Authorization": f"Bearer {self.user_two_access_token}"},
        )
        assert (
            post_no_password_join_chatroom_with_password_fail_response.status_code
            == 403
        )

        # try to join with authorization header and wrong password
        # should fail as user has provided wrong chatroom password
        post_wrong_password_join_chatroom_with_password_fail_response = test_client.post(
            f"{PRIVATE_CHAT_URL_PREFIX}/join/{self.user_one_private_chatroom_one_uid}",
            headers={"Authorization": f"Bearer {self.user_two_access_token}"},
            json={"password": "wrong_chatroom_password"},
        )
        assert (
            post_wrong_password_join_chatroom_with_password_fail_response.status_code
            == 403
        )

        ### test successful chatroom join
        # get current members count
        get_chatroom_info_for_user_two_before_joining_response = test_client.get(
            f"{BASE_CHAT_URL_PREFIX}/all?id={self.user_one_private_chatroom_one_uid}",
            headers={"Authorization": f"Bearer {self.user_two_access_token}"},
        )
        assert get_chatroom_info_for_user_two_before_joining_response.status_code == 200
        chatroom_one_members_count_before_user_two_joined = (
            get_chatroom_info_for_user_two_before_joining_response.json()
            .get("chatrooms")[0]
            .get("members_count")
        )

        # try to join with authorization header
        # should succeed as user has provided chatroom password
        post_post_join_chatroom_with_password_success_response = test_client.post(
            f"{PRIVATE_CHAT_URL_PREFIX}/join/{self.user_one_private_chatroom_one_uid}",
            headers={"Authorization": f"Bearer {self.user_two_access_token}"},
            json={"password": PRIVATE_CHATROOM_PASSWORD},
        )
        assert post_post_join_chatroom_with_password_success_response.status_code == 200

        # confirm chatroom members count has increased to 2
        # chatroom was created by user1 who automatically became a member; making members_count 1
        # user2 is the first external user to join chatroom; chatroom members_count must be 2
        get_chatroom_info_for_user_two_after_joining_response = test_client.get(
            f"{BASE_CHAT_URL_PREFIX}/all?id={self.user_one_private_chatroom_one_uid}",
            headers={"Authorization": f"Bearer {self.user_two_access_token}"},
        )
        assert get_chatroom_info_for_user_two_after_joining_response.status_code == 200
        chatroom_one_members_count_after_user_two_joined = (
            get_chatroom_info_for_user_two_after_joining_response.json()
            .get("chatrooms")[0]
            .get("members_count")
        )
        assert chatroom_one_members_count_after_user_two_joined == (
            chatroom_one_members_count_before_user_two_joined + 1
        )

        ### get chatrooms user2 has joined
        # get all
        get_user_two_all_joined_chatrooms_response = test_client.get(
            f"{PRIVATE_CHAT_URL_PREFIX}/all",
            headers={"Authorization": f"Bearer {self.user_two_access_token}"},
        )
        assert get_user_two_all_joined_chatrooms_response.status_code == 200
        user_two_all_joined_chatrooms_list = (
            get_user_two_all_joined_chatrooms_response.json().get("chatrooms")
        )
        # length should be 1 as this is the first chatroom user2 is joining
        assert len(user_two_all_joined_chatrooms_list) == 1

        # get all created by user2
        get_user_two_all_owned_chatrooms_response = test_client.get(
            f"{PRIVATE_CHAT_URL_PREFIX}/all?role=creator",
            headers={"Authorization": f"Bearer {self.user_two_access_token}"},
        )
        user_two_all_owned_chatrooms = (
            get_user_two_all_owned_chatrooms_response.json().get("chatrooms")
        )
        # length should be 0 as user2 has not created any chatroom
        assert len(user_two_all_owned_chatrooms) == 0

        # get private only
        get_user_two_all_joined_private_chatrooms_response = test_client.get(
            f"{PRIVATE_CHAT_URL_PREFIX}/all?room_type=private",
            headers={"Authorization": f"Bearer {self.user_two_access_token}"},
        )
        user_two_all_joined_private_chatrooms = (
            get_user_two_all_joined_private_chatrooms_response.json().get("chatrooms")
        )
        # length should be 1 as the only chatroom user2 has joined is chatroom_one which is private
        assert len(user_two_all_joined_private_chatrooms) == 1

        # get public only
        get_user_two_all_joined_public_chatrooms_response = test_client.get(
            f"{PRIVATE_CHAT_URL_PREFIX}/all?room_type=public",
            headers={"Authorization": f"Bearer {self.user_two_access_token}"},
        )
        user_two_all_joined_public_chatrooms = (
            get_user_two_all_joined_public_chatrooms_response.json().get("chatrooms")
        )
        # length should be 0 as the only chatroom user2 has not joined any public chatroom
        assert len(user_two_all_joined_public_chatrooms) == 0

        ### test chatroom user membership endpoint

        # confirm use2 membership status for chatroom_one
        # try to call endpoint without username parameter and without auth header
        # should fail as one must be provided
        get_user_two_chatroom_membership_without_auth_header_without_username_param = (
            test_client.get(
                f"/chat/check/{self.user_one_private_chatroom_one_uid}/user",
            )
        )
        assert (
            get_user_two_chatroom_membership_without_auth_header_without_username_param.status_code
            == 401
        )

        # try to call endpoint with only username parameter
        # should succeed provide details for user with matching username
        get_user_two_chatroom_membership_with_only_username_param_response = test_client.get(
            f"/chat/check/{self.user_one_private_chatroom_one_uid}/user/?username={self.user_two_signup_data["username"]}"
        )
        assert (
            get_user_two_chatroom_membership_with_only_username_param_response.status_code
            == 200
        )
        # try to call endpoint with only auth header
        # should succeed provide details for the logged in user
        get_user_two_chatroom_membership_with_only_auth_header_response = (
            test_client.get(
                f"/chat/check/{self.user_one_private_chatroom_one_uid}/user",
                headers={"Authorization": f"Bearer {self.user_two_access_token}"},
            )
        )
        assert (
            get_user_two_chatroom_membership_with_only_auth_header_response.status_code
            == 200
        )
        user_two_chatroom_one_membership_details = (
            get_user_two_chatroom_membership_with_only_auth_header_response.json()
        )
        expected_membership_details_keys = {"user_status"}
        assert expected_membership_details_keys.issubset(
            user_two_chatroom_one_membership_details.keys()
        )
        assert user_two_chatroom_one_membership_details.get("user_status") == "member"

        # try to retrieve messages to test privacy enforcement
        # try to retrieve messages with authorization header
        # should succeed as user is now a member
        get_chatroom_messages_as_authorized_member_response = test_client.get(
            f"{BASE_CHAT_URL_PREFIX}/messages/{self.user_one_private_chatroom_one_uid}",
            headers={"Authorization": f"Bearer {self.user_two_access_token}"},
        )
        assert get_chatroom_messages_as_authorized_member_response.status_code == 200

        chatroom_messages_details = (
            get_chatroom_messages_as_authorized_member_response.json()
        )

        # check that the chatroom type is correct
        assert chatroom_messages_details.get("room_type") == "private"

        ### test leave chatroom

        # get chatroom user count before leaving
        get_private_chatroom_one_info_before_leaving_response = test_client.get(
            f"{BASE_CHAT_URL_PREFIX}/all?id={self.user_one_private_chatroom_one_uid}"
        )
        assert get_private_chatroom_one_info_before_leaving_response.status_code == 200
        members_count_before_leaving = (
            get_private_chatroom_one_info_before_leaving_response.json()
            .get("chatrooms")[0]
            .get("members_count")
        )

        # leave chatroom
        post_leave_chatroom_response = test_client.post(
            f"{PRIVATE_CHAT_URL_PREFIX}/leave/{self.user_one_private_chatroom_one_uid}",
            headers={"Authorization": f"Bearer {self.user_two_access_token}"},
        )
        assert post_leave_chatroom_response.status_code == 200

        # get chatroom user count after leaving
        get_private_chatroom_one_info_after_leaving_response = test_client.get(
            f"{BASE_CHAT_URL_PREFIX}/all?id={self.user_one_private_chatroom_one_uid}"
        )
        assert get_private_chatroom_one_info_after_leaving_response.status_code == 200
        members_count_after_leaving = (
            get_private_chatroom_one_info_after_leaving_response.json()
            .get("chatrooms")[0]
            .get("members_count")
        )
        assert members_count_after_leaving == (members_count_before_leaving - 1)

        get_user_two_chatroom_membership_removed_response = test_client.get(
            f"/chat/check/{self.user_one_private_chatroom_one_uid}/user",
            headers={"Authorization": f"Bearer {self.user_two_access_token}"},
        )
        user_two_chatroom_membership_removed_details = (
            get_user_two_chatroom_membership_removed_response.json()
        )
        assert (
            user_two_chatroom_membership_removed_details.get("user_status") == "removed"
        )

        # join room to retrieve messages
        post_join_chatroom_with_password_success_response = test_client.post(
            f"{PRIVATE_CHAT_URL_PREFIX}/join/{self.user_one_private_chatroom_one_uid}",
            json={"password": PRIVATE_CHATROOM_PASSWORD},
            headers={"Authorization": f"Bearer {self.user_two_access_token}"},
        )
        assert post_join_chatroom_with_password_success_response.status_code == 200
        # retrieve messages after joining chatroom
        get_chatroom_messages_response = test_client.get(
            f"{BASE_CHAT_URL_PREFIX}/messages/{self.user_one_private_chatroom_one_uid}",
            headers={"Authorization": f"Bearer {self.user_two_access_token}"},
        )
        assert get_chatroom_messages_response.status_code == 200
        get_chatroom_messages_response_json = get_chatroom_messages_response.json()

        # check that the length of first page of messages returned
        # first message is for user creating the chatroom
        # second message is for user joining the chatroom
        # third message is for user leaving the chatroom
        # fourth message is for user joining the chatroom again
        assert len(get_chatroom_messages_response_json["messages"]) == 4

        ################################ LOGOUT USER2

    def test_chatroom_update(self, test_client):
        """
        test chatroom update
        """
        old_chatroom_password = PRIVATE_CHATROOM_PASSWORD

        new_private_chatroom_password = "N3wCh@tr00mPassword"
        new_private_chatroom_name = "New PRivate Chatroom Name"
        new_private_chatroom_about = "This is the new private chatroom about."
        private_chatroom_update_data = {
            "name": new_private_chatroom_name,
            "about": new_private_chatroom_about,
            "password": new_private_chatroom_password,
            "confirm_password": new_private_chatroom_password,
        }

        new_public_chatroom_password = "N3wCh@tr00mPassword"
        new_public_chatroom_name = "New PRivate Chatroom Name"
        new_public_chatroom_about = "This is the new public chatroom about."
        public_chatroom_update_data_without_password = {
            "name": new_public_chatroom_name,
            "about": new_public_chatroom_about,
        }

        # chatroom info before update
        ################################ LOGIN USER2
        # logged in as user2 try to update chatroom
        # should fail as user2 is not the chatroom creator
        patch_private_chatroom_one_update_as_user_two_failed_response = (
            test_client.patch(
                f"/chat/?id={self.user_one_private_chatroom_one_uid}",
                headers={"Authorization": f"Bearer {self.user_two_access_token}"},
                json=private_chatroom_update_data,
            )
        )
        delnow = patch_private_chatroom_one_update_as_user_two_failed_response.json()
        assert (
            patch_private_chatroom_one_update_as_user_two_failed_response.status_code
            == 403
        )

        # leave chatroom to later try and join again after updates
        test_client.post(
            f"{PRIVATE_CHAT_URL_PREFIX}/leave/{self.user_one_private_chatroom_one_uid}",
            headers={"Authorization": f"Bearer {self.user_two_access_token}"},
        )
        ################################ LOGOUT USER2 ################################

        ################################ LOGIN USER1 ################################
        # logged in as user1 try to update chatroom
        # should succeed as user1 is the chatroom creator
        patch_private_chatroom_one_data_update_as_owner_user_one_success_response = (
            test_client.patch(
                f"/chat/?id={self.user_one_private_chatroom_one_uid}",
                headers={"Authorization": f"Bearer {self.user_one_access_token}"},
                json=private_chatroom_update_data,
            )
        )
        de = (
            patch_private_chatroom_one_data_update_as_owner_user_one_success_response.json()
        )
        assert (
            patch_private_chatroom_one_data_update_as_owner_user_one_success_response.status_code
            == 200
        )

        # get chatroom data to confirm update was successful
        get_private_chatroom_one_data_after_update_response = test_client.get(
            f"/chat/all?id={self.user_one_private_chatroom_one_uid}",
            headers={"Authorization": f"Bearer {self.user_one_access_token}"},
        )
        assert get_private_chatroom_one_data_after_update_response.status_code == 200
        chatroom_one_data = (
            get_private_chatroom_one_data_after_update_response.json().get("chatrooms")[
                0
            ]
        )

        # confirm changes reflect in name and about fields
        assert (
            str(chatroom_one_data.get("name")).lower()
            == new_private_chatroom_name.lower()
        )
        assert (
            str(chatroom_one_data.get("about")).lower()
            == new_private_chatroom_about.lower()
        )

        # test public chatroom update
        # try to update public chatroom data with password
        # should fail as public chatroom cannot be updated to have a password
        public_chatroom_update_data_with_password = (
            public_chatroom_update_data_without_password.copy()
        )
        public_chatroom_update_data_with_password.update(
            {"password": new_public_chatroom_password}
        )
        patch_public_chatroom_data_update_with_password_as_owner_failed_response = (
            test_client.patch(
                f"/chat/?id={self.user_one_public_chatroom_one_uid}",
                headers={"Authorization": f"Bearer {self.user_one_access_token}"},
                json=public_chatroom_update_data_with_password,
            )
        )
        # confirm that update form was rejected as update form contains password
        assert (
            patch_public_chatroom_data_update_with_password_as_owner_failed_response.status_code
            == 422
        )

        # try to update public chatroom without password field filled
        # should succeed as password is not provided
        patch_public_chatroom_data_update_without_password_as_owner_success_response = (
            test_client.patch(
                f"/chat/?id={self.user_one_public_chatroom_one_uid}",
                headers={"Authorization": f"Bearer {self.user_one_access_token}"},
                json=public_chatroom_update_data_without_password,
            )
        )
        assert (
            patch_public_chatroom_data_update_without_password_as_owner_success_response.status_code
            == 200
        )

        # get public chatroom data to confirm changes
        get_public_chatroom_data_after_update_response = test_client.get(
            f"/chat/all?id={self.user_one_public_chatroom_one_uid}",
            headers={"Authorization": f"Bearer {self.user_one_access_token}"},
        )
        assert get_public_chatroom_data_after_update_response.status_code == 200
        public_chatroom_data_after_update = (
            get_public_chatroom_data_after_update_response.json().get("chatrooms")[0]
        )

        assert public_chatroom_data_after_update.get("name") == new_public_chatroom_name
        assert (
            public_chatroom_data_after_update.get("about") == new_public_chatroom_about
        )

        # reset public chatroom data to default
        patch_public_chatroom_data_reset_as_owner_success_response = test_client.patch(
            f"/chat/?id={self.user_one_public_chatroom_one_uid}",
            headers={"Authorization": f"Bearer {self.user_one_access_token}"},
            json=self.public_chatroom_one_create_data,
        )
        assert (
            patch_public_chatroom_data_reset_as_owner_success_response.status_code
            == 200
        )
        ################################ LOGOUT USER1 ################################

        ################################ LOGIN USER2 ################################
        # logged in as user2
        # try to join chatroom with previous password
        # should fail to confirm password update was successful
        post_user_two_join_chatroom_one_with_old_password_failed_response = test_client.post(
            f"{PRIVATE_CHAT_URL_PREFIX}/join/{self.user_one_private_chatroom_one_uid}",
            headers={"Authorization": f"Bearer {self.user_two_access_token}"},
            json={"password": old_chatroom_password},
        )
        assert (
            post_user_two_join_chatroom_one_with_old_password_failed_response.status_code
            == 403
        )

        # try to enter chatroom with new password
        # should succeed password update was successful
        post_user_two_join_chatroom_one_with_new_password_success_response = test_client.post(
            f"{PRIVATE_CHAT_URL_PREFIX}/join/{self.user_one_private_chatroom_one_uid}",
            headers={"Authorization": f"Bearer {self.user_two_access_token}"},
            json={"password": new_private_chatroom_password},
        )
        assert (
            post_user_two_join_chatroom_one_with_new_password_success_response.status_code
            == 200
        )

        post_user_two_leave_chatroom_one_success_response = test_client.post(
            f"{PRIVATE_CHAT_URL_PREFIX}/leave/{self.user_one_private_chatroom_one_uid}",
            headers={"Authorization": f"Bearer {self.user_two_access_token}"},
        )
        assert post_user_two_leave_chatroom_one_success_response.status_code == 200
        ################################ LOGOUT USER2 ################################

        ################################ LOGIN USER1 ################################
        # reset to chatroom data to original
        reset_data_with_password = self.private_chatroom_one_create_data.copy()
        reset_data_with_password.update(
            {
                "password": PRIVATE_CHATROOM_PASSWORD,
                "confirm_password": PRIVATE_CHATROOM_PASSWORD,
            }
        )
        patch_chatroom_one_data_reset_response = test_client.patch(
            f"/chat/?id={self.user_one_private_chatroom_one_uid}",
            headers={"Authorization": f"Bearer {self.user_one_access_token}"},
            json=reset_data_with_password,
        )
        assert patch_chatroom_one_data_reset_response.status_code == 200
        ################################ LOGOUT USER1 ################################

        ################################ LOGIN USER2 ################################
        # logged in as user2
        # try to enter chatroom with old password after reset
        # should succeed as superuser password update was successful
        post_user_two_join_chatroom_one_with_old_password_success_response = test_client.post(
            f"{PRIVATE_CHAT_URL_PREFIX}/join/{self.user_one_private_chatroom_one_uid}",
            headers={"Authorization": f"Bearer {self.user_two_access_token}"},
            json={"password": old_chatroom_password},
        )
        assert (
            post_user_two_join_chatroom_one_with_old_password_success_response.status_code
            == 200
        )
        ################################ LOGOUT USER2 ################################

    def test_get_chatroom_members_for_user_three(self, test_client):
        """
        test chatroom members retrieval for user three
        """

        ################################ LOGIN USER3 ################################
        # get chatroom members
        # should fail as user has not joined chatroom yet
        get_chatroom_one_members_failed_non_member_response = test_client.get(
            f"{PRIVATE_CHAT_URL_PREFIX}/members/{self.user_one_private_chatroom_one_uid}",
            headers={"Authorization": f"Bearer {self.user_three_access_token}"},
        )
        # should raise 403 forbidden error as user three is not a member yet
        assert get_chatroom_one_members_failed_non_member_response.status_code == 403

        # join chatroom
        post_join_chatroom_with_password_success_response = test_client.post(
            f"{PRIVATE_CHAT_URL_PREFIX}/join/{self.user_one_private_chatroom_one_uid}",
            headers={"Authorization": f"Bearer {self.user_three_access_token}"},
            json={"password": PRIVATE_CHATROOM_PASSWORD},
        )
        assert post_join_chatroom_with_password_success_response.status_code == 200

        # get chatroom members
        # should work as user is now a member
        get_chatroom_one_members_success_member_response = test_client.get(
            f"{PRIVATE_CHAT_URL_PREFIX}/members/{self.user_one_private_chatroom_one_uid}",
            headers={"Authorization": f"Bearer {self.user_three_access_token}"},
        )
        # should raise 403 forbidden error as user three is not a member yet
        assert get_chatroom_one_members_success_member_response.status_code == 200
        # check that chatroom now has 3 members
        # first member is user1, the creator
        # second member is user2
        # third member is user3, the account being used to retrieve messages
        chatroom_members_list = (
            get_chatroom_one_members_success_member_response.json().get("users")
        )
        assert len(chatroom_members_list) == 3
        ################################ LOGOUT USER3

    def test_chatroom_moderation_features(self, test_client):

        ################################ LOGIN USER2
        # hit endpoint to list all members
        get_members_response = test_client.get(
            f"{PRIVATE_CHAT_URL_PREFIX}/members/{self.user_one_private_chatroom_one_uid}",
            headers={"Authorization": f"Bearer {self.user_two_access_token}"},
        )
        assert get_members_response.status_code == 200
        chatroom_members_list = get_members_response.json().get("users")
        # check that the chatroom has 3 members
        # user1 joined on creation, user2 and user3 joined in previous tests
        assert len(chatroom_members_list) == 3

        # hit endpoint to list all moderators
        get_moderators_response = test_client.get(
            f"{PRIVATE_CHAT_URL_PREFIX}/members/{self.user_one_private_chatroom_one_uid}?role=moderator",
            headers={"Authorization": f"Bearer {self.user_two_access_token}"},
        )
        assert get_moderators_response.status_code == 200
        chatroom_moderators_list = get_moderators_response.json().get("users")
        # check that the chatroom has only one moderator
        # the chatroom creator should be automatically made into a moderator on chatroom creation if chatroom is private
        # the only moderator being the creator of the chatroom
        assert len(chatroom_moderators_list) == 1

        # try to remove user three from the group
        # should fail with 403 error since user2 is not an admin
        post_user_two_remove_user_three_forbidden_response = test_client.post(
            f"{PRIVATE_CHAT_URL_PREFIX}/members/{self.user_one_private_chatroom_one_uid}/remove/moderator?user_uid={self.user_three_uid}",
            headers={"Authorization": f"Bearer {self.user_two_access_token}"},
        )
        assert post_user_two_remove_user_three_forbidden_response.status_code == 403

        # try to toggle chatroom messages recording
        # should fail as user2 is not an admin
        post_user_two_toggle_chatroom_one_messages_recording_failed_response = test_client.patch(
            f"{PRIVATE_CHAT_URL_PREFIX}/recording/{self.user_one_private_chatroom_one_uid}/switch",
            headers={"Authorization": f"Bearer {self.user_two_access_token}"},
        )
        assert (
            post_user_two_toggle_chatroom_one_messages_recording_failed_response.status_code
            == 403
        )

        ################################# LOGOUT USER2 ########################################

        ################################# LOGIN USER1 - the creator of the chatroom_one
        # logged in as user1
        # try to remove user three
        # should success as user1 is a moderator
        post_user_one_remove_user_three_response = test_client.post(
            f"{PRIVATE_CHAT_URL_PREFIX}/members/{self.user_one_private_chatroom_one_uid}/remove?user_uid={self.user_three_uid}",
            headers={"Authorization": f"Bearer {self.user_one_access_token}"},
        )
        assert post_user_one_remove_user_three_response.status_code == 200

        ### confirm user3 membership status is removed

        # confirm user3 membership status is removed with username parameter and without auth header
        # should succeed as username parameter is provided
        get_user_three_chatroom_removed_response = test_client.get(
            f"/chat/check/{self.user_one_private_chatroom_one_uid}/user/?username={self.user_three_signup_data["username"]}",
            # no need for authorization header as username url parameter is provided
            # authorization header only needed if no username param is provided
        )
        user_three_chatroom_one_membership_details = (
            get_user_three_chatroom_removed_response.json()
        )
        assert (
            user_three_chatroom_one_membership_details.get("user_status") == "removed"
        )

        # get chatroom record_messages status before toggle
        get_chatroom_info_before_record_messages_toggle_response = test_client.get(
            f"{BASE_CHAT_URL_PREFIX}/all?id={self.user_one_private_chatroom_one_uid}",
            headers={"Authorization": f"Bearer {self.user_one_access_token}"},
        )
        chatroom_record_messages_status_before_toggle = (
            get_chatroom_info_before_record_messages_toggle_response.json()
            .get("chatrooms")[0]
            .get("record_messages")
        )

        # try to toggle chatroom messages recording
        # should fail as user2 is not an admin
        post_user_one_toggle_chatroom_one_messages_recording_failed_response = test_client.patch(
            f"{PRIVATE_CHAT_URL_PREFIX}/recording/{self.user_one_private_chatroom_one_uid}/switch",
            headers={"Authorization": f"Bearer {self.user_one_access_token}"},
        )
        assert (
            post_user_one_toggle_chatroom_one_messages_recording_failed_response.status_code
            == 200
        )

        # get chatroom record_messages status after toggle
        get_chatroom_info_after_record_messages_toggle_response = test_client.get(
            f"{BASE_CHAT_URL_PREFIX}/all?id={self.user_one_private_chatroom_one_uid}",
            headers={"Authorization": f"Bearer {self.user_one_access_token}"},
        )
        chatroom_record_messages_status_after_toggle = (
            get_chatroom_info_after_record_messages_toggle_response.json()
            .get("chatrooms")[0]
            .get("record_messages")
        )
        assert type(chatroom_record_messages_status_after_toggle) == bool
        assert type(chatroom_record_messages_status_before_toggle) == bool
        assert (
            chatroom_record_messages_status_after_toggle
            != chatroom_record_messages_status_before_toggle
        )

        ########################################
        # confirm users are down from 3 to 2 after removal
        get_members_response = test_client.get(
            f"{PRIVATE_CHAT_URL_PREFIX}/members/{self.user_one_private_chatroom_one_uid}",
            headers={"Authorization": f"Bearer {self.user_two_access_token}"},
        )
        assert get_members_response.status_code == 200
        chatroom_members_list = get_members_response.json().get("users")
        assert len(chatroom_members_list) == 2
        # confirm that user3 is in chatroom ban list
        get_chatroom_one_banned_users_after_user_three_removed_response = test_client.get(
            f"{PRIVATE_CHAT_URL_PREFIX}/members/{self.user_one_private_chatroom_one_uid}?role=removed",
            headers={"Authorization": f"Bearer {self.user_one_access_token}"},
        )
        delnow = get_chatroom_one_banned_users_after_user_three_removed_response.json()
        assert (
            get_chatroom_one_banned_users_after_user_three_removed_response.status_code
            == 200
        )
        # check ban list length
        chatroom_ban_list_with_user_three = (
            get_chatroom_one_banned_users_after_user_three_removed_response.json().get(
                "users"
            )
        )
        assert len(chatroom_ban_list_with_user_three) == 1

        # confirm banned user is user3
        chatroom_banned_user_uid = chatroom_ban_list_with_user_three[0].get("uid")
        assert chatroom_banned_user_uid == self.user_three_uid

        ########################################

        ######################################## LOGOUT USER1 ########################################

        ######################################## LOGIN USER3 ########################################
        # user3 got removed and bannedd by a moderator - user1
        # try to join chatroom
        # should fail as user is banned
        post_join_chatroom_with_password_success_response = test_client.post(
            f"{PRIVATE_CHAT_URL_PREFIX}/join/{self.user_one_private_chatroom_one_uid}",
            headers={"Authorization": f"Bearer {self.user_three_access_token}"},
            json={"password": PRIVATE_CHATROOM_PASSWORD},
        )
        # check that user is not able to join chatroom after ban
        # check for error_response
        assert post_join_chatroom_with_password_success_response.status_code == 403
        ######################################## LOGOUT USER3 ########################################

        ######################################## LOGIN USER1 ########################################
        # check that members are still just 2
        get_members_response = test_client.get(
            f"{PRIVATE_CHAT_URL_PREFIX}/members/{self.user_one_private_chatroom_one_uid}",
            headers={"Authorization": f"Bearer {self.user_one_access_token}"},
        )
        assert get_members_response.status_code == 200
        chatroom_members_list = get_members_response.json().get("users")
        # check length
        assert len(chatroom_members_list) == 2

        # add user3 back into chat to unban
        post_add_and_unban_user_three_response = test_client.post(
            f"{PRIVATE_CHAT_URL_PREFIX}/members/{self.user_one_private_chatroom_one_uid}/add?user_uid={self.user_three_uid}",
            headers={"Authorization": f"Bearer {self.user_one_access_token}"},
        )
        assert post_add_and_unban_user_three_response.status_code == 200
        ########################################
        # confirm user3 has been added
        get_members_response = test_client.get(
            f"{PRIVATE_CHAT_URL_PREFIX}/members/{self.user_one_private_chatroom_one_uid}",
            headers={"Authorization": f"Bearer {self.user_one_access_token}"},
        )
        assert get_members_response.status_code == 200
        chatroom_members_list = get_members_response.json().get("users")
        # check length
        assert len(chatroom_members_list) == 3
        # check that chatroom ban list is empty
        # check that user3 is no longer on chatroom ban list
        get_chatroom_one_banned_users_after_user_three_added = test_client.get(
            f"{PRIVATE_CHAT_URL_PREFIX}/members/{self.user_one_private_chatroom_one_uid}?role=removed",
            headers={"Authorization": f"Bearer {self.user_one_access_token}"},
        )
        assert get_chatroom_one_banned_users_after_user_three_added.status_code == 200
        # check members length
        chatroom_ban_list_without_user_three = (
            get_chatroom_one_banned_users_after_user_three_added.json().get("users")
        )
        assert len(chatroom_ban_list_without_user_three) == 0
        ########################################
        ######################################## LOGOUT USER1 ########################################

        ######################################## LOGIN USER3 ########################################
        # try to join chatroom as user3
        # should work as user3 fail as user3 automatically became a member upon unbanning
        user_three_unbanned_join_chatroom_failed_response = test_client.post(
            f"{PRIVATE_CHAT_URL_PREFIX}/join/{self.user_one_private_chatroom_one_uid}",
            headers={"Authorization": f"Bearer {self.user_three_access_token}"},
            json={"password": PRIVATE_CHATROOM_PASSWORD},
        )
        assert user_three_unbanned_join_chatroom_failed_response.status_code == 422

        # leave chatroom
        user_three_unbanned_leave_chatroom_response = test_client.post(
            f"{PRIVATE_CHAT_URL_PREFIX}/leave/{self.user_one_private_chatroom_one_uid}",
            headers={"Authorization": f"Bearer {self.user_three_access_token}"},
        )
        assert user_three_unbanned_leave_chatroom_response.status_code == 200

        # try to join chatroom as user3
        # should work as user3 has been unbanned and can join chatroom with password
        user_three_unbanned_join_chatroom_response = test_client.post(
            f"{PRIVATE_CHAT_URL_PREFIX}/join/{self.user_one_private_chatroom_one_uid}",
            headers={"Authorization": f"Bearer {self.user_three_access_token}"},
            json={"password": PRIVATE_CHATROOM_PASSWORD},
        )
        assert user_three_unbanned_join_chatroom_response.status_code == 200

        # logged in as user3
        # try to make user2 a moderator
        # should fail as user3 is not the creator of the chatroom
        post_user_three_add_user_two_to_moderators = test_client.post(
            f"{PRIVATE_CHAT_URL_PREFIX}/members/{self.user_one_private_chatroom_one_uid}/add/moderator?user_uid={self.user_two_uid}",
            headers={"Authorization": f"Bearer {self.user_three_access_token}"},
        )
        assert post_user_three_add_user_two_to_moderators.status_code == 403
        ######################################## LOGOUT USER3 ########################################

        ######################################## LOGIN USER1 ########################################
        # logged in as user1
        # try to make user2 a moderator
        # should succeed as user1 is a moderator
        post_user_one_add_user_two_to_moderators = test_client.post(
            f"{PRIVATE_CHAT_URL_PREFIX}/members/{self.user_one_private_chatroom_one_uid}/add/moderator?user_uid={self.user_two_uid}",
            headers={"Authorization": f"Bearer {self.user_one_access_token}"},
        )
        assert post_user_one_add_user_two_to_moderators.status_code == 200
        # confirm that there are now 2 moderators. incremented from 1
        get_moderators_after_user_two_addition_response = test_client.get(
            f"{PRIVATE_CHAT_URL_PREFIX}/members/{self.user_one_private_chatroom_one_uid}?role=moderator",
            headers={"Authorization": f"Bearer {self.user_one_access_token}"},
        )
        assert get_moderators_after_user_two_addition_response.status_code == 200
        chatroom_moderators_list_after_user_two_addition = (
            get_moderators_after_user_two_addition_response.json().get("users")
        )
        # check that the chatroom now has 2 moderators
        assert len(chatroom_moderators_list_after_user_two_addition) == 2
        ######################################## LOGOUT USER1 ########################################

        ######################################## LOGIN USER2 ########################################
        # logged in as user2
        # try to remove user3
        # should succeed as user2 is an admin now
        post_user_two_remove_user_three_success_response = test_client.post(
            f"{PRIVATE_CHAT_URL_PREFIX}/members/{self.user_one_private_chatroom_one_uid}/remove?user_uid={self.user_three_uid}",
            headers={"Authorization": f"Bearer {self.user_two_access_token}"},
        )
        delnow = post_user_two_remove_user_three_success_response.json()
        assert post_user_two_remove_user_three_success_response.status_code == 200
        # confirm chatroom members are now 2. decreased from 3.
        get_chatroom_one_members_after_user_two_removed_response = test_client.get(
            f"{PRIVATE_CHAT_URL_PREFIX}/members/{self.user_one_private_chatroom_one_uid}",
            headers={"Authorization": f"Bearer {self.user_two_access_token}"},
        )
        assert (
            get_chatroom_one_members_after_user_two_removed_response.status_code == 200
        )
        # check that members are now 2 after removal of user3 by user2
        chatroom_members_without_user_two = (
            get_chatroom_one_members_after_user_two_removed_response.json().get("users")
        )
        assert len(chatroom_members_without_user_two) == 2

        # logged in as user2 - moderator
        # try to remove user3 - regular
        # should succeed as user2 is an admin now
        post_user_two_remove_user_three_success_response = test_client.post(
            f"{PRIVATE_CHAT_URL_PREFIX}/members/{self.user_one_private_chatroom_one_uid}/remove?user_uid={self.user_three_uid}",
            headers={"Authorization": f"Bearer {self.user_two_access_token}"},
        )
        assert post_user_two_remove_user_three_success_response.status_code == 200
        ########################################
        # check that members are now 2 after removal of user3 by user2
        get_chatroom_one_members_after_user_two_removed_response = test_client.get(
            f"{PRIVATE_CHAT_URL_PREFIX}/members/{self.user_one_private_chatroom_one_uid}",
            headers={"Authorization": f"Bearer {self.user_two_access_token}"},
        )
        assert (
            get_chatroom_one_members_after_user_two_removed_response.status_code == 200
        )
        # check members length
        chatroom_members_without_user_two = (
            get_chatroom_one_members_after_user_two_removed_response.json().get("users")
        )
        assert len(chatroom_members_without_user_two) == 2
        ########################################

        # try to add user3 to chatroom - regular
        # should succeed as user2 is a moderator now
        post_user_two_remove_user_three_success_response = test_client.post(
            f"{PRIVATE_CHAT_URL_PREFIX}/members/{self.user_one_private_chatroom_one_uid}/add?user_uid={self.user_three_uid}",
            headers={"Authorization": f"Bearer {self.user_two_access_token}"},
        )
        assert post_user_two_remove_user_three_success_response.status_code == 200
        # confirm chatroom members are now 3. incremented from 2.
        get_chatroom_one_members_after_user_two_added_response = test_client.get(
            f"{PRIVATE_CHAT_URL_PREFIX}/members/{self.user_one_private_chatroom_one_uid}",
            headers={"Authorization": f"Bearer {self.user_two_access_token}"},
        )
        assert get_chatroom_one_members_after_user_two_added_response.status_code == 200
        # check length
        chatroom_members_with_user_two = (
            get_chatroom_one_members_after_user_two_added_response.json().get("users")
        )
        assert len(chatroom_members_with_user_two) == 3

        # try to remove user1
        # should fail as user1 is the creator of the chatroom and cannot be removed by moderators
        post_user_two_remove_user_one_fail_response = test_client.post(
            f"{PRIVATE_CHAT_URL_PREFIX}/members/{self.user_one_private_chatroom_one_uid}/remove?user_uid={self.user_one_uid}",
            headers={"Authorization": f"Bearer {self.user_two_access_token}"},
        )
        assert post_user_two_remove_user_one_fail_response.status_code == 403

        ######################################## LOGOUT USER2 ########################################

    def test_chatroom_creator_successor(self, test_client):
        """
        test the creator successor feature to ensure private chatrooms always have a present overseer
        """

        ######################################## LOGIN USER1 ########################################
        # logged in as user 1
        # confirm user1 is chatroom creator
        get_user_one_is_chatroom_creator_response = test_client.get(
            f"/chat/check/{self.user_one_private_chatroom_one_uid}/user",
            headers={"Authorization": f"Bearer {self.user_one_access_token}"},
        )

        chatroom_one_membership_details_for_user_one = (
            get_user_one_is_chatroom_creator_response.json()
        )
        assert (
            chatroom_one_membership_details_for_user_one.get("user_status") == "creator"
        )

        #### CHECK USER MEMBERSHIP STATUS FOR ALL JOIN, LEAVE, ADD MOD, ETC ENDPOINTS

        # try to leave chatroom as creator
        # should fail as chatroom does not have a creator successor
        post_creator_leave_chatroom_fail_response = test_client.post(
            f"{PRIVATE_CHAT_URL_PREFIX}/leave/{self.user_one_private_chatroom_one_uid}",
            headers={"Authorization": f"Bearer {self.user_one_access_token}"},
        )
        assert post_creator_leave_chatroom_fail_response.status_code == 422

        # try to make user3 the successor
        # should fail as user3 is not a moderator
        post_make_user_three_successor_fail_response = test_client.post(
            f"{PRIVATE_CHAT_URL_PREFIX}/members/{self.user_one_private_chatroom_one_uid}/add/successor?user_uid={self.user_three_uid}",
            headers={"Authorization": f"Bearer {self.user_one_access_token}"},
        )
        assert post_make_user_three_successor_fail_response.status_code == 403

        # try to make user2 the successor
        # should succeed as user2 is a moderator
        post_make_user_two_successor_success_response = test_client.post(
            f"{PRIVATE_CHAT_URL_PREFIX}/members/{self.user_one_private_chatroom_one_uid}/add/successor?user_uid={self.user_two_uid}",
            headers={"Authorization": f"Bearer {self.user_one_access_token}"},
        )
        assert post_make_user_two_successor_success_response.status_code == 200

        # confirm user2 membership status is moderator
        get_user_two_is_chatroom_successor_response = test_client.get(
            f"/chat/check/{self.user_one_private_chatroom_one_uid}/user/?username={self.user_two_signup_data["username"]}",
            headers={"Authorization": f"Bearer {self.user_one_access_token}"},
        )
        user_two_chatroom_one_successor_details = (
            get_user_two_is_chatroom_successor_response.json()
        )
        assert user_two_chatroom_one_successor_details.get("user_status") == "successor"

        # try to leave chatroom as creator
        # should succeed as chatroom has a creator successor
        post_creator_leave_chatroom_success_response = test_client.post(
            f"{PRIVATE_CHAT_URL_PREFIX}/leave/{self.user_one_private_chatroom_one_uid}",
            headers={"Authorization": f"Bearer {self.user_one_access_token}"},
        )
        assert post_creator_leave_chatroom_success_response.status_code == 200

        # confirm user1 is not chatroom creator
        get_user_one_is_not_chatroom_creator_response = test_client.get(
            f"/chat/check/{self.user_one_private_chatroom_one_uid}/user",
            headers={"Authorization": f"Bearer {self.user_one_access_token}"},
        )
        user_one_chatroom_one_membership_details = (
            get_user_one_is_not_chatroom_creator_response.json()
        )
        assert user_one_chatroom_one_membership_details.get("user_status") == "removed"
        ######################################## LOGOUT USER1 ########################################

        ######################################## LOGIN USER2 ########################################
        # confirm user2 is chatroom creator
        get_user_two_is_chatroom_creator_response = test_client.get(
            f"/chat/check/{self.user_one_private_chatroom_one_uid}/user",
            headers={"Authorization": f"Bearer {self.user_two_access_token}"},
        )
        user_two_chatroom_one_membership_details = (
            get_user_two_is_chatroom_creator_response.json()
        )
        assert user_two_chatroom_one_membership_details.get("user_status") == "creator"

        ######################################## LOGOUT USER2 ########################################

    def test_chatroom_creation_with_user_hidden_status_active(self, test_client):
        """
        test chatroom creation with user privacy set to hidden, followed by chatroom deletion.
        """
        user_two_access_token = self.user_access_tokens[self.user_two_email]
        ######################################## LOGIN USER2 ########################################

        user_two_anonymous_username = "DangerousStranger"
        user_two_username = self.user_two_signup_data["username"]

        user_two_public_chatroom_create_data = self.public_chatroom_one_create_data
        user_two_public_chatroom_create_data.update(
            {"name": "user two public chatroom"}
        )

        user_two_private_chatroom_create_data = self.private_chatroom_one_create_data
        user_two_private_chatroom_create_data.update(
            {"name": "user two private chatroom"}
        )

        # update user one privacy status
        # endpoint works as toggle and sets to user's hidden status to it's opposite i.e true to false and vice versa
        patch_user_one_privacy_status_update_response = test_client.patch(
            f"{BASE_AUTH_URL_PREFIX}/privacy",
            headers={"Authorization": f"Bearer {user_two_access_token}"},
        )
        assert patch_user_one_privacy_status_update_response.status_code == 200
        user_one_privacy_status_update_json = (
            patch_user_one_privacy_status_update_response.json()
        )
        assert {"is_hidden"} == user_one_privacy_status_update_json.keys()

        user_one_privacy_status_is_hidden_status = (
            user_one_privacy_status_update_json.get("is_hidden")
        )
        # user hidden status should be true after toggle as it was previously false by default
        assert user_one_privacy_status_is_hidden_status is True

        # create public chatroom logged in as user2
        # creator username should default to provided anonymous username rather that user2 logged in username
        # this is because user2 is_hidden and chatroom is public
        post_user_two_anonymous_create_public_chatroom_response = test_client.post(
            f"{BASE_CHAT_URL_PREFIX}?anon_username={user_two_anonymous_username}",
            headers={"Authorization": f"Bearer {user_two_access_token}"},
            json=user_two_public_chatroom_create_data,
        )
        post_user_two_anonymous_create_public_chatroom_response.status_code == 201
        user_two_public_chatroom_original_creator_username = (
            post_user_two_anonymous_create_public_chatroom_response.json().get(
                "original_creator_username"
            )
        )
        assert (
            user_two_public_chatroom_original_creator_username
            == user_two_anonymous_username.lower()
        )
        self.__class__.user_two_public_chatroom_one_uid = (
            post_user_two_anonymous_create_public_chatroom_response.json().get("uid")
        )

        # create private chatroom logged in as user2
        # creator username should default to logged in user2 username instead of provided anonymous username
        # this is because even though user2 is_hidden, private chatroom must have user2 username as original creator username
        user_two_private_chatroom_create_data.update(
            {
                "password": PRIVATE_CHATROOM_PASSWORD,
                "confirm_password": PRIVATE_CHATROOM_PASSWORD,
            }
        )
        post_user_two_anonymous_create_private_chatroom_response = test_client.post(
            f"{BASE_CHAT_URL_PREFIX}?&anon_username={user_two_anonymous_username}",
            headers={"Authorization": f"Bearer {user_two_access_token}"},
            json=user_two_private_chatroom_create_data,
        )
        post_user_two_anonymous_create_private_chatroom_response.status_code == 201
        jj = post_user_two_anonymous_create_private_chatroom_response.json()
        user_two_private_chatroom_original_creator_username = (
            post_user_two_anonymous_create_private_chatroom_response.json().get(
                "original_creator_username"
            )
        )
        assert (
            user_two_private_chatroom_original_creator_username
            == user_two_username.lower()
        )
        self.__class__.user_two_private_chatroom_one_uid = (
            post_user_two_anonymous_create_private_chatroom_response.json().get("uid")
        )

        # revert user2 hidden status for future tests
        patch_user_one_privacy_status_revert_response = test_client.patch(
            f"{BASE_AUTH_URL_PREFIX}/privacy",
            headers={"Authorization": f"Bearer {user_two_access_token}"},
        )
        assert patch_user_one_privacy_status_revert_response.status_code == 200

        ######################################## LOGOUT USER2 ########################################

    def test_user_public_chatroom_moderation_and_restrictions(self, test_client):
        """
        test public chatroom  to confirm that moderation features are restricted
        """
        # testing with user_two_public_chatroom_one

        user_two_access_token = self.user_access_tokens[self.user_two_email]
        user_three_access_token = self.user_access_tokens[self.user_three_email]

        ######################################## LOGIN USER3 ########################################
        # login as user three to join chatroom for testing
        post_user_three_join_user_two_public_chatroom_one_response = test_client.post(
            f"{BASE_CHAT_URL_PREFIX}/private/room/join/{self.user_two_public_chatroom_one_uid}",
            headers={"Authorization": f"Bearer {user_three_access_token}"},
        )
        assert (
            post_user_three_join_user_two_public_chatroom_one_response.status_code
            == 200
        )

        # confirm public chatroom has no moderators
        # for private chatroom ONLY, creator is made into a moderator automatically on creation
        get_user_two_public_chatroom_one_moderators_response = test_client.get(
            f"{BASE_CHAT_URL_PREFIX}/private/room/members/{self.user_two_public_chatroom_one_uid}/?role=moderator",
            headers={"Authorization": f"Bearer {user_two_access_token}"},
        )
        assert get_user_two_public_chatroom_one_moderators_response.status_code == 200
        user_two_public_chatroom_one_moderators_list = (
            get_user_two_public_chatroom_one_moderators_response.json().get("users")
        )
        # confirm user list is empty
        assert len(user_two_public_chatroom_one_moderators_list) == 0

        ######################################## LOGOUT USER3 ########################################

        ######################################## LOGIN USER2 ########################################
        # logged in as user2, chatroom creator
        # try to add user3 to moderator
        # user3 is a member of public chatroom
        # should fail as chatroom is public and moderation features are reserved for private chatroom
        post_user_two_add_user_three_to_public_chatroom_moderators_failed_response = test_client.post(
            f"{BASE_CHAT_URL_PREFIX}/private/room/members/{self.user_two_public_chatroom_one_uid}/add/moderator?user_uid={self.user_three_uid}",
            headers={"Authorization": f"Bearer {user_two_access_token}"},
        )
        assert (
            post_user_two_add_user_three_to_public_chatroom_moderators_failed_response.status_code
            == 422
        )

        # confirm that chatroom still has no moderator
        # get_user_two_public_chatroom_one_moderators
        get_user_two_public_chatroom_one_moderators_after_failed_moderator_add_response = test_client.get(
            f"{BASE_CHAT_URL_PREFIX}/private/room/members/{self.user_two_public_chatroom_one_uid}/?role=moderator",
            headers={"Authorization": f"Bearer {user_three_access_token}"},
        )
        assert (
            get_user_two_public_chatroom_one_moderators_after_failed_moderator_add_response.status_code
            == 200
        )
        user_two_public_chatroom_one_moderators_after_failed_add_list = get_user_two_public_chatroom_one_moderators_after_failed_moderator_add_response.json().get(
            "users"
        )
        # confirm user list is empty
        assert len(user_two_public_chatroom_one_moderators_after_failed_add_list) == 0

        # try to make user3 the chatroom successor
        # should fail as chatroom is public
        # should fail as user3 would need to be a moderator first
        post_user_two_make_user_three_chatroom_successor_failed_response = test_client.post(
            f"{BASE_CHAT_URL_PREFIX}/private/room/members/{self.user_two_public_chatroom_one_uid}/add/successor?user_uid={self.user_three_uid}",
            headers={"Authorization": f"Bearer {user_two_access_token}"},
        )
        assert (
            post_user_two_make_user_three_chatroom_successor_failed_response.status_code
            == 422
        )

        ######################################## LOGOUT USER2 ########################################

    def test_creator_leave_public_chatroom_leaving(self, test_client):
        """
        test creator leaving public chatroom mechanism as chatroom creator: user2
        """

        user_two_access_token = self.user_access_tokens[self.user_two_email]
        # check user2 chatroom membership status to confirm user is creator before leaving
        get_user_two_membership_status_for_user_two_public_chatroom_one_before_leave_response = test_client.get(
            f"{BASE_CHAT_URL_PREFIX}/check/{self.user_two_public_chatroom_one_uid}/user/?username={self.user_two_signup_data["username"]}",
        )
        assert (
            get_user_two_membership_status_for_user_two_public_chatroom_one_before_leave_response.status_code
            == 200
        )
        user_two_membership_status_for_public_chatroom_one_before_leaving = get_user_two_membership_status_for_user_two_public_chatroom_one_before_leave_response.json().get(
            "user_status"
        )
        assert (
            user_two_membership_status_for_public_chatroom_one_before_leaving
            == "creator"
        )

        ######################################## LOGIN USER2 ########################################
        # logged in as user2, chatroom creator
        # try to leave chatroom
        # should succeed without restriction as chatroom is public
        post_user_two_leave_own_chatroom_response = test_client.post(
            f"{BASE_CHAT_URL_PREFIX}/private/room/leave/{self.user_two_public_chatroom_one_uid}/",
            headers={"Authorization": f"Bearer {user_two_access_token}"},
        )
        assert post_user_two_leave_own_chatroom_response.status_code == 200

        ######################################## LOGOUT USER2 ########################################

        # check user2 chatroom membership status to confirm user is removed after leaving
        get_user_two_membership_status_for_user_two_public_chatroom_one_after_leave_response = test_client.get(
            f"{BASE_CHAT_URL_PREFIX}/check/{self.user_two_public_chatroom_one_uid}/user/?username={self.user_two_signup_data["username"]}",
        )
        assert (
            get_user_two_membership_status_for_user_two_public_chatroom_one_after_leave_response.status_code
            == 200
        )
        user_two_membership_status_for_public_chatroom_one_after_leaving = get_user_two_membership_status_for_user_two_public_chatroom_one_after_leave_response.json().get(
            "user_status"
        )
        assert (
            user_two_membership_status_for_public_chatroom_one_after_leaving
            == "removed"
        )

    def test_chatroom_deletion(self, test_client):
        """
        test chatroom deletion mechanism. any type of chatroom, public or private, can be deleted, but only by it's creator
        """
        ###!!!!!! IMPORTANT !!!!!!###
        ## THIS SHOULD BE THE LAST TEST ##

        ## test to be carried out using user_two_private_chatroom_one and user_one_public_chatroom_one
        user_one_access_token = self.user_access_tokens[self.user_one_email]
        user_two_access_token = self.user_access_tokens[self.user_two_email]

        user_two_private_chatroom_uid = self.user_two_private_chatroom_one_uid
        user_one_public_chatroom_uid = self.user_one_public_chatroom_one_uid

        ######################################## LOGIN USER1 ########################################
        ######################################## LOGOUT USER1 ########################################
        # logged  in as user1
        # try to delete chatroom created by user2
        # should fail as chatroom can only be deleted by creator
        delete_user_two_private_chatroom_as_user_one_response = test_client.delete(
            f"{BASE_CHAT_URL_PREFIX}?id={user_two_private_chatroom_uid}",
            headers={"Authorization": f"Bearer {user_one_access_token}"},
        )
        assert delete_user_two_private_chatroom_as_user_one_response.status_code == 403

        # try to delete public chatroom created by logged in user: user1
        # should succeed as user1 is the creator
        delete_user_one_public_chatroom_as_owner_response = test_client.delete(
            f"{BASE_CHAT_URL_PREFIX}?id={user_one_public_chatroom_uid}",
            headers={"Authorization": f"Bearer {user_one_access_token}"},
        )
        assert delete_user_one_public_chatroom_as_owner_response.status_code == 200

        # try to retrieve chatroom info after delete
        # should return empty as chatroom no longer exists
        get_user_one_public_chatroom_info_after_delete_response = test_client.get(
            f"{BASE_CHAT_URL_PREFIX}/all?id={user_one_public_chatroom_uid}",
            headers={"Authorization": f"Bearer {user_one_access_token}"},
        )
        assert (
            get_user_one_public_chatroom_info_after_delete_response.status_code == 404
        )

        ######################################## LOGIN USER2 ########################################
        # logged in as user2
        # try to delete private chatroom created by logged in user: user2
        # should succeed as user2 is the creator
        delete_user_two_private_chatroom_as_owner_response = test_client.delete(
            f"{BASE_CHAT_URL_PREFIX}?id={user_two_private_chatroom_uid}",
            headers={"Authorization": f"Bearer {user_two_access_token}"},
        )
        assert delete_user_two_private_chatroom_as_owner_response.status_code == 200

        # try to retrieve chatroom info after delete
        # should return empty as chatroom no longer exists
        get_user_two_private_chatroom_info_after_delete_response = test_client.get(
            f"{BASE_CHAT_URL_PREFIX}/all?id={user_two_private_chatroom_uid}",
            headers={"Authorization": f"Bearer {user_one_access_token}"},
        )
        assert (
            get_user_two_private_chatroom_info_after_delete_response.status_code == 404
        )

        ######################################## LOGOUT USER2 ########################################
