import pytest

from src.tests.conftest import test_client

BASE_CHAT_URL_PREFIX = "/chat"


class TestPublicChatroomAndMessagingFeatures:

    def setup_method(self):

        self.public_chatroom_create_data = {
            "name": "public-chatroom-1",
            "about": "first public chatroom description which must be above 24 characters",
            "room_type": "public",
        }

    def test_create_public_chatroom_and_websocket_messaging(self, test_client):

        chatroom_successful_create_response = test_client.post(
            f"{BASE_CHAT_URL_PREFIX}?anon_username=anonymous_visitor",
            json=self.public_chatroom_create_data,
        )
        assert chatroom_successful_create_response.status_code == 201

        chatroom_success_details_dict = chatroom_successful_create_response.json()

        chatroom_creation_response_expected_keys = {
            "uid",
            "name",
            "about",
            "created_at",
            "modified_at",
            "original_creator_username",
            "room_type",
            "members_count",
        }
        assert chatroom_creation_response_expected_keys.issubset(
            set(chatroom_success_details_dict.keys())
        )

        self.__class__.public_chatroom_one_uid = chatroom_success_details_dict["uid"]

        get_chatroom_messages_response = test_client.get(
            f"{BASE_CHAT_URL_PREFIX}/messages/{self.public_chatroom_one_uid}"
        )
        assert get_chatroom_messages_response.status_code == 200

        chatroom_messages_details = get_chatroom_messages_response.json()

        # check that the chatroom type is correct
        assert chatroom_messages_details["room_type"] == "public"

        # check that the length of messages returned is 1
        # first message is for user creating the chatroom
        assert len(chatroom_messages_details["messages"]) == 1
