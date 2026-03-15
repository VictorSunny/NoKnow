from src.apps.auth.tests.base_test_user_signup_login_jwt import BaseTestUserSignupLogin


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


class BaseTestUserIntegrations(BaseTestUserSignupLogin):

    async def test_get_user_details(self, test_client):
        """
        test get user details
        """
        expected_user_two_basic_details_json_keys = {
            "uid",
            "first_name",
            "last_name",
            "username",
            "bio",
            "joined",
            "is_hidden",
        }
        expected_user_one_private_details_json_keys = (
            expected_user_two_basic_details_json_keys.copy()
        )
        expected_user_one_private_details_json_keys.update(
            ["is_two_factor_authenticated", "email"]
        )

        get_user_one_details_response = test_client.get(
            f"{BASE_USER_URL_PREFIX}",
            headers={"Authorization": f"Bearer {self.user_one_access_token}"},
        )
        assert get_user_one_details_response.status_code == 200
        # confirm that user details response has correct keys
        user_one_details_json = get_user_one_details_response.json()
        assert expected_user_one_private_details_json_keys.issubset(
            user_one_details_json.keys()
        )

        get_user_two_details_logged_in_as_user_one_response = test_client.get(
            f"{BASE_USER_URL_PREFIX}?username={self.user_two_signup_data["username"]}",
            headers={"Authorization": f"Bearer {self.user_one_access_token}"},
        )
        assert get_user_two_details_logged_in_as_user_one_response.status_code == 200
        # confirm that user details response has correct keys
        user_two_details_json = (
            get_user_two_details_logged_in_as_user_one_response.json()
        )
        expected_user_two_basic_details_json_keys == user_two_details_json.keys()

    def test_user_friendship_send_unsend_accept_friend_request(self, test_client):
        user_one_access_token = self.user_access_tokens.get(self.user_one_email)
        user_two_access_token = self.user_access_tokens.get(self.user_two_email)
        user_three_access_token = self.user_access_tokens.get(self.user_three_email)

        ################################ LOGIN USER1 ########################################
        # test send friend request
        # logged in as user1
        # send friend request to user2

        # check friendship status between users before sending
        get_user_one_to_user_two_unfriended_friendship_status_response = test_client.get(
            f"{BASE_USER_URL_PREFIX}/friends/check?username={self.user_two_signup_data["username"]}",
            headers={"Authorization": f"Bearer {user_one_access_token}"},
        )
        assert (
            get_user_one_to_user_two_unfriended_friendship_status_response.status_code
            == 200
        )
        user_one_to_user_two_friendship_status_json = (
            get_user_one_to_user_two_unfriended_friendship_status_response.json()
        )
        assert "friendship_status" in user_one_to_user_two_friendship_status_json.keys()
        user_one_to_user_two_unfriended_friendship_status = (
            user_one_to_user_two_friendship_status_json["friendship_status"]
        )
        assert user_one_to_user_two_unfriended_friendship_status == "unfriended"

        # get all sent friend requests
        get_user_one_sent_friend_requests_before_sending_response = test_client.get(
            f"{BASE_USER_URL_PREFIX}/friends/requests/sent/all",
            headers={"Authorization": f"Bearer {user_one_access_token}"},
        )
        assert (
            get_user_one_sent_friend_requests_before_sending_response.status_code == 200
        )
        user_one_sent_friend_requests_before_sending_json = (
            get_user_one_sent_friend_requests_before_sending_response.json()
        )
        # confirm response has correct key
        assert "users" in user_one_sent_friend_requests_before_sending_json.keys()
        user_one_sent_friend_requests_before_sending = (
            user_one_sent_friend_requests_before_sending_json.get("users")
        )
        # confirm that user1 has not sent any friend request
        assert len(user_one_sent_friend_requests_before_sending) == 0

        post_user_one_add_user_two_success_response = test_client.post(
            f"{BASE_USER_URL_PREFIX}/friends/requests/send?id={self.user_two_uid}",
            headers={"Authorization": f"Bearer {user_one_access_token}"},
        )
        assert post_user_one_add_user_two_success_response.status_code == 200

        # get all sent friend requests after sending friend request
        get_user_one_sent_friend_requests_after_sending_response = test_client.get(
            f"{BASE_USER_URL_PREFIX}/friends/requests/sent/all",
            headers={"Authorization": f"Bearer {user_one_access_token}"},
        )
        assert (
            get_user_one_sent_friend_requests_after_sending_response.status_code == 200
        )
        user_one_sent_friend_requests_after_sending = (
            get_user_one_sent_friend_requests_after_sending_response.json().get("users")
        )
        # confirm that user1 has only one sent request
        assert len(user_one_sent_friend_requests_after_sending) == 1
        # confirm that list of dict contains correct data
        assert isinstance(user_one_sent_friend_requests_after_sending[0], dict)
        assert "uid" in user_one_sent_friend_requests_after_sending[0].keys()
        user_one_only_sent_friend_request_uid = (
            user_one_sent_friend_requests_after_sending[0].get("uid")
        )
        # confirm that the only sent request matches user2 uid
        # recall user1 their only friend request to user2
        assert user_one_only_sent_friend_request_uid == self.user_two_uid

        # check friendship status between users after sending
        get_user_one_to_user_two_requested_friendship_status_response = test_client.get(
            f"{BASE_USER_URL_PREFIX}/friends/check?username={self.user_two_signup_data["username"]}",
            headers={"Authorization": f"Bearer {user_one_access_token}"},
        )
        assert (
            get_user_one_to_user_two_requested_friendship_status_response.status_code
            == 200
        )
        user_one_to_user_two_requested_friendship_status = (
            get_user_one_to_user_two_requested_friendship_status_response.json().get(
                "friendship_status"
            )
        )
        assert user_one_to_user_two_requested_friendship_status == "requested"

        # try to send friend request to self
        # should fail as user should not be able to send friend request to self
        post_user_one_add_user_one_fail_response = test_client.post(
            f"{BASE_USER_URL_PREFIX}/friends/requests/send?id={self.user_one_uid}",
            headers={"Authorization": f"Bearer {user_one_access_token}"},
        )
        assert post_user_one_add_user_one_fail_response.status_code == 422

        # user1 unsend friend request to user2
        post_user_one_unsend_friend_request_to_user_two_success_response = test_client.post(
            f"{BASE_USER_URL_PREFIX}/friends/requests/unsend?id={self.user_two_uid}",
            headers={"Authorization": f"Bearer {user_one_access_token}"},
        )
        assert (
            post_user_one_unsend_friend_request_to_user_two_success_response.status_code
            == 200
        )

        ################################ LOGOUT USER1 ########################################

        ################################ LOGIN USER2 ########################################
        # confirm user2 has no pending friend requests
        get_user_two_empty_friend_requests_success_response = test_client.get(
            f"{BASE_USER_URL_PREFIX}/friends/requests/all",
            headers={"Authorization": f"Bearer {user_one_access_token}"},
        )

        assert get_user_two_empty_friend_requests_success_response.status_code == 200
        assert (
            "users" in get_user_two_empty_friend_requests_success_response.json().keys()
        )

        user_two_empty_friend_requests_list = (
            get_user_two_empty_friend_requests_success_response.json().get("users")
        )
        # confirm that user2 friend requests list is empty
        assert len(user_two_empty_friend_requests_list) == 0

        ################################ LOGOUT USER2 ########################################

        ################################ LOGIN USER3 ########################################
        # logged in as user3
        # send friend request to user2
        post_user_three_add_user_two_success_response = test_client.post(
            f"{BASE_USER_URL_PREFIX}/friends/requests/send?id={self.user_two_uid}",
            headers={"Authorization": f"Bearer {user_three_access_token}"},
        )
        assert post_user_three_add_user_two_success_response.status_code == 200

        ################################ LOGOUT USER3 ########################################

        ################################ LOGIN USER1 ########################################
        # logged in as user1
        # send friend request to user2
        post_user_one_add_user_two_success_response = test_client.post(
            f"{BASE_USER_URL_PREFIX}/friends/requests/send?id={self.user_two_uid}",
            headers={"Authorization": f"Bearer {user_one_access_token}"},
        )
        assert post_user_one_add_user_two_success_response.status_code == 200
        ################################ LOGOUT USER1 ########################################

        ################################ LOGIN USER2 ########################################

        get_user_two_friend_requests_success_response = test_client.get(
            f"{BASE_USER_URL_PREFIX}/friends/requests/all",
            headers={"Authorization": f"Bearer {user_two_access_token}"},
        )
        assert get_user_two_friend_requests_success_response.status_code == 200

        user_two_friend_requests_list = (
            get_user_two_friend_requests_success_response.json().get("users")
        )
        # confirm friend request list contains the correct uids
        assert len(user_two_friend_requests_list) == 2

        friend_requests_usernames = {
            user.get("username") for user in user_two_friend_requests_list
        }
        expected_friend_request_usernames = {
            self.user_one_signup_data["username"],
            self.user_three_signup_data["username"],
        }
        assert expected_friend_request_usernames == friend_requests_usernames

        for request_uid in expected_friend_request_usernames:
            get_user_two_to_user_friendship_requested_status_response = test_client.get(
                f"{BASE_USER_URL_PREFIX}/friends/check?username={request_uid}",
                headers={"Authorization": f"Bearer {user_two_access_token}"},
            )
            assert (
                get_user_two_to_user_friendship_requested_status_response.status_code
                == 200
            )
            user_two_to_user_friendship_requested_status = (
                get_user_two_to_user_friendship_requested_status_response.json().get(
                    "friendship_status"
                )
            )
            assert user_two_to_user_friendship_requested_status == "pending"

        # test user2 reject user1 friend request
        # should succeed as friend request from user1 exists
        post_user_two_reject_user_one_friend_request_success_response = test_client.post(
            f"{BASE_USER_URL_PREFIX}/friends/requests/reject?id={self.user_one_uid}",
            headers={"Authorization": f"Bearer {user_two_access_token}"},
        )
        assert (
            post_user_two_reject_user_one_friend_request_success_response.status_code
            == 200
        )

        # test accept friend request

        # test user2 accept user1 friend request
        # should fail as friend request from user1 doesn't exist
        # friend request from user1 was rejected earlier above
        post_user_two_accept_user_one_friend_request_fail_response = test_client.post(
            f"{BASE_USER_URL_PREFIX}/friends/requests/accept?id={self.user_one_uid}",
            headers={"Authorization": f"Bearer {user_two_access_token}"},
        )
        # confirm that friend request accept fails
        assert (
            post_user_two_accept_user_one_friend_request_fail_response.status_code
            == 422
        )

        # test user2 send friend request to user one
        # should fail as user3 already sent a friend request
        # user2 must accept or reject said friend request
        post_user_three_send_user_one_friend_request_failed_response = test_client.post(
            f"{BASE_USER_URL_PREFIX}/friends/requests/send?id={self.user_three_uid}",
            headers={"Authorization": f"Bearer {user_two_access_token}"},
        )
        assert (
            post_user_three_send_user_one_friend_request_failed_response.status_code
            == 422
        )

        # test user2 accept user3 friend request
        # should succeed as user3 sent a friend request earlier
        post_user_two_accept_user_three_friend_request_success_response = test_client.post(
            f"{BASE_USER_URL_PREFIX}/friends/requests/accept?id={self.user_three_uid}",
            headers={"Authorization": f"Bearer {user_two_access_token}"},
        )
        # confirm that friend request accept fails
        assert (
            post_user_two_accept_user_three_friend_request_success_response.status_code
            == 200
        )

        # test friend list retrieval
        get_user_two_friend_list_success_response = test_client.get(
            f"{BASE_USER_URL_PREFIX}/friends/all",
            headers={"Authorization": f"Bearer {user_two_access_token}"},
        )
        assert get_user_two_friend_list_success_response.status_code == 200

        user_two_friend_list = get_user_two_friend_list_success_response.json().get(
            "users"
        )
        # confirm that user2 has 1 friend after accepting user3 friend request
        assert len(user_two_friend_list) == 1
        # confirm that user3 is the 1 friend of user2
        only_friend_uid = user_two_friend_list[0].get("uid")
        assert only_friend_uid == self.user_three_uid

        # confirm frienship status as user2 to user3
        get_user_two_to_user_three_friended_friendship_status_response = test_client.get(
            f"{BASE_USER_URL_PREFIX}/friends/check?username={self.user_three_signup_data["username"]}",
            headers={"Authorization": f"Bearer {user_two_access_token}"},
        )
        assert (
            get_user_two_to_user_three_friended_friendship_status_response.status_code
            == 200
        )
        user_two_to_user_three_friended_friendship_status = (
            get_user_two_to_user_three_friended_friendship_status_response.json().get(
                "friendship_status"
            )
        )
        assert user_two_to_user_three_friended_friendship_status == "friended"

        ################################ LOGOUT USER2 ########################################

        ################################ LOGIN USER3 ########################################
        # confirm frienship status as user3 to user2 !IMPORTANT
        # confirm relationship to be mutual
        get_user_three_to_user_two_friended_friendship_status_response = test_client.get(
            f"{BASE_USER_URL_PREFIX}/friends/check?username={self.user_two_signup_data["username"]}",
            headers={"Authorization": f"Bearer {user_three_access_token}"},
        )
        assert (
            get_user_three_to_user_two_friended_friendship_status_response.status_code
            == 200
        )
        user_two_to_user_three_friended_friendship_status = (
            get_user_three_to_user_two_friended_friendship_status_response.json().get(
                "friendship_status"
            )
        )
        assert user_two_to_user_three_friended_friendship_status == "friended"

        ################################ LOGOUT USER3 ########################################

        # test removing friend
        post_user_two_remove_user_three_from_friends_success_response = (
            test_client.post(
                f"{BASE_USER_URL_PREFIX}/friends/remove?id={self.user_three_uid}",
                headers={"Authorization": f"Bearer {user_two_access_token}"},
            )
        )
        assert (
            post_user_two_remove_user_three_from_friends_success_response.status_code
            == 200
        )

        # confirm user friend list is now empty
        get_user_two_friend_list_after_user_three_unfriended_response = test_client.get(
            f"{BASE_USER_URL_PREFIX}/friends/all",
            headers={"Authorization": f"Bearer {user_two_access_token}"},
        )
        assert (
            get_user_two_friend_list_after_user_three_unfriended_response.status_code
            == 200
        )
        user_two_friend_list = (
            get_user_two_friend_list_after_user_three_unfriended_response.json().get(
                "users"
            )
        )
        # confirm that user2 has no friend after removing user3 as friend
        assert len(user_two_friend_list) == 0

        # confirm frienship status is now unfriended
        get_user_two_to_user_three_unfriended_friendship_status_response = test_client.get(
            f"{BASE_USER_URL_PREFIX}/friends/check?username={self.user_three_signup_data["username"]}",
            headers={"Authorization": f"Bearer {user_two_access_token}"},
        )
        assert (
            get_user_two_to_user_three_unfriended_friendship_status_response.status_code
            == 200
        )
        user_two_to_user_three_unfriended_friendship_status = (
            get_user_two_to_user_three_unfriended_friendship_status_response.json().get(
                "friendship_status"
            )
        )
        assert user_two_to_user_three_unfriended_friendship_status == "unfriended"

        # retry unfriended user3
        # should fail as user3 is not a friend
        post_remove_user_three_from_friends_failed_response = test_client.post(
            f"{BASE_USER_URL_PREFIX}/friends/remove?id={self.user_three_uid}",
            headers={"Authorization": f"Bearer {user_two_access_token}"},
        )
        assert post_remove_user_three_from_friends_failed_response.status_code == 422

        ################################ LOGOUT USER2 ########################################

        ################################ LOGIN USER3 ########################################
        # confirm frienship status as user3 to user2 !IMPORTANT
        # confirm relationship to be mutual
        get_user_three_to_user_two_unfriended_friendship_status_response = test_client.get(
            f"{BASE_USER_URL_PREFIX}/friends/check?username={self.user_two_signup_data["username"]}",
            headers={"Authorization": f"Bearer {user_three_access_token}"},
        )
        assert (
            get_user_three_to_user_two_unfriended_friendship_status_response.status_code
            == 200
        )
        user_two_to_user_three_unfriended_friendship_status = (
            get_user_three_to_user_two_unfriended_friendship_status_response.json().get(
                "friendship_status"
            )
        )
        assert user_two_to_user_three_unfriended_friendship_status == "unfriended"

        ################################ LOGOUT USER3 ########################################
