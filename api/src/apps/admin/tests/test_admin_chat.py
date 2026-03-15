from uuid import UUID
import pytest
from sqlmodel import select
from sqlalchemy.orm import joinedload

from src.apps.admin.tests.base_test_admin_user_and_token_blacklisting import (
    BaseTestAdminUserAndTokenBlacklisting,
)
from src.db.models import Chatroom, User
from src.utilities.utilities import check_password, hash_password
from src.tests.conftest import test_client, r_client, test_session

UNIVERSAL_PASSWORD = "Abcd@1234"
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
TEST_OWNER_USERNAME = "Ragman"


class TestAdminChat(BaseTestAdminUserAndTokenBlacklisting):

    async def test_setup(self, test_session):
        parsed_password = hash_password(password="Abcd@1234")
        new_user = User(
            first_name="normal",
            last_name="guy",
            username=TEST_OWNER_USERNAME,
            email="e@mail.com",
            password=parsed_password,
            bio="this user is created solely for testing that user is attached to chatroom on creation by admin.",
        )
        test_session.add(new_user)
        await test_session.commit()
        await test_session.refresh(new_user)

        assert new_user.username == TEST_OWNER_USERNAME

        self.__class__.CHATROOM_OWNER_USERNAME = new_user.username

    async def test_admin_get_and_all_created_chatrooms(self, test_client, test_session):
        """
        get all created chatrooms.
        """
        newly_created_chatroom_count = 0
        chatroom_count_before_creating_new_chatrooms = 0
        admin_created_chatroom_uids_list = []

        ################################ LOGIN ADMIN ########################################
        # get all created chatrooms before creating new chatrooms
        get_all_created_chatrooms_before_creating_new_as_admin_user = test_client.get(
            f"/admin/chat/all",
            headers={"Authorization": f"Bearer {self.admin_one_access_token}"},
        )
        assert (
            get_all_created_chatrooms_before_creating_new_as_admin_user.status_code
            == 200
        )
        assert (
            "chatrooms"
            in get_all_created_chatrooms_before_creating_new_as_admin_user.json().keys()
        )

        # test public chatroom creation
        for n in range(1, 4):
            create_data_public_chatroom = {
                "name": f"test admin public chatroom {n}",
                "about": f"this is the number {n} public chatroom",
                "room_type": "public",
                "original_creator_username": self.CHATROOM_OWNER_USERNAME,
            }
            post_admin_user_create_public_chatroom_without_password_success_response = (
                test_client.post(
                    "/admin/chat",
                    json=create_data_public_chatroom,
                    headers={"Authorization": f"Bearer {self.admin_one_access_token}"},
                )
            )
            assert (
                post_admin_user_create_public_chatroom_without_password_success_response.status_code
                == 201
            )
            new_public_chatroom = (
                post_admin_user_create_public_chatroom_without_password_success_response.json()
            )

            assert type(new_public_chatroom) == dict
            assert new_public_chatroom.keys() == EXPECTED_CHATROOM_DETAILS_KEYS

            new_public_chatroom_uid = new_public_chatroom["uid"]
            new_public_chatroom_original_creator_username = new_public_chatroom[
                "original_creator_username"
            ]

            assert (
                new_public_chatroom_original_creator_username
                == str(self.CHATROOM_OWNER_USERNAME).lower()
            )
            assert new_public_chatroom.get("record_messages") is True

            # confirm that user with matching username is a member of the newly created chatroom
            executed_user_query = await test_session.execute(
                select(User).where(User.username == self.CHATROOM_OWNER_USERNAME)
            )
            assigned_creator = executed_user_query.scalar_one_or_none()
            assert assigned_creator is not None

            # retrieve newly created chatroom for necessary verifications
            query = (
                select(Chatroom)
                .options(
                    joinedload(Chatroom.members),
                    joinedload(Chatroom.moderators),
                    joinedload(Chatroom.banned_users),
                )
                .where(Chatroom.uid == UUID(new_public_chatroom_uid))
            )
            executed_query = await test_session.execute(query)
            db_new_public_chatroom: Chatroom = (
                executed_query.unique().scalar_one_or_none()
            )

            assert db_new_public_chatroom is not None
            assert assigned_creator in db_new_public_chatroom.members
            assert assigned_creator in db_new_public_chatroom.moderators
            assert assigned_creator not in db_new_public_chatroom.banned_users
            assert assigned_creator.uid == db_new_public_chatroom.creator_uid

            admin_created_chatroom_uids_list.append(new_public_chatroom_uid)
            newly_created_chatroom_count += 1

            # try creating public chatroom with password
            # should fail as password should not be provided for public chatroom
            create_data_public_chatroom_with_password = (
                create_data_public_chatroom.copy()
            )
            create_data_public_chatroom_with_password.update(
                {
                    "password": UNIVERSAL_PASSWORD,
                    "confirm_password": UNIVERSAL_PASSWORD,
                }
            )
            post_admin_user_create_public_chatroom_with_password_failed_response = (
                test_client.post(
                    "/admin/chat",
                    json=create_data_public_chatroom_with_password,
                    headers={"Authorization": f"Bearer {self.admin_one_access_token}"},
                )
            )
            assert (
                post_admin_user_create_public_chatroom_with_password_failed_response.status_code
                == 422
            )

            # try creating public chatroom with invalid_creator_username
            # should fail as provided username is not connected with any user account
            create_data_public_chatroom_with_invalid_creator_username = (
                create_data_public_chatroom.copy()
            )
            create_data_public_chatroom_with_invalid_creator_username.update(
                {
                    "original_creator_username": "invalidusername",
                }
            )
            post_admin_user_create_public_chatroom_with_invalid_creator_username_failed_response = test_client.post(
                "/admin/chat",
                json=create_data_public_chatroom_with_invalid_creator_username,
                headers={"Authorization": f"Bearer {self.admin_one_access_token}"},
            )
            assert (
                post_admin_user_create_public_chatroom_with_invalid_creator_username_failed_response.status_code
                == 404
            )

            # try creating chatroom without providing value for original creator username
            # should fail as field is required to link a user to a chatroom on creation via this endpoint
            create_data_public_chatroom_without_creator_username = (
                create_data_public_chatroom.copy()
            )
            if (
                "original_creator_username"
                in create_data_public_chatroom_without_creator_username.keys()
            ):
                del create_data_public_chatroom_without_creator_username[
                    "original_creator_username"
                ]
            post_admin_user_create_public_chatroom_without_creator_username_failed_response = test_client.post(
                "/admin/chat",
                json=create_data_public_chatroom_without_creator_username,
                headers={"Authorization": f"Bearer {self.admin_one_access_token}"},
            )

            assert (
                post_admin_user_create_public_chatroom_without_creator_username_failed_response.status_code
                == 422
            )

        # test private chatroom creation
        for n in range(1, 4):
            private_chatroom_create_data_without_password = {
                "name": f"test admin private chatroom {n}",
                "about": f"this is the number {n} private chatroom",
                "room_type": "private",
                "original_creator_username": self.CHATROOM_OWNER_USERNAME,
            }
            post_admin_user_create_private_chatroom_without_password_failed_response = (
                test_client.post(
                    "/admin/chat",
                    json=private_chatroom_create_data_without_password,
                    headers={"Authorization": f"Bearer {self.admin_one_access_token}"},
                )
            )
            assert (
                post_admin_user_create_private_chatroom_without_password_failed_response.status_code
                == 422
            )

            # try creating private chatroom with password
            # should fail as password should not be provided for private chatroom
            private_chatroom_create_data_with_password = (
                private_chatroom_create_data_without_password.copy()
            )
            private_chatroom_create_data_with_password.update(
                {
                    "password": UNIVERSAL_PASSWORD,
                    "confirm_password": UNIVERSAL_PASSWORD,
                }
            )
            post_admin_user_create_private_chatroom_with_password_success_response = (
                test_client.post(
                    "/admin/chat",
                    json=private_chatroom_create_data_with_password,
                    headers={"Authorization": f"Bearer {self.admin_one_access_token}"},
                )
            )
            assert (
                post_admin_user_create_private_chatroom_with_password_success_response.status_code
                == 201
            )
            new_private_chatroom = (
                post_admin_user_create_private_chatroom_with_password_success_response.json()
            )

            assert type(new_private_chatroom) == dict
            assert new_private_chatroom.keys() == EXPECTED_CHATROOM_DETAILS_KEYS
            assert (
                new_private_chatroom.get("original_creator_username")
                == self.CHATROOM_OWNER_USERNAME.lower()
            )
            assert new_private_chatroom.get("record_messages") is True

            new_private_chatroom_uid = new_private_chatroom.get("uid")

            # confirm that user with matching username is a member of the newly created chatroom
            executed_user_query = await test_session.execute(
                select(User).where(User.username == self.CHATROOM_OWNER_USERNAME)
            )
            assigned_creator = executed_user_query.scalar_one_or_none()
            assert assigned_creator is not None

            # retrieve newly created chatroom for necessary verifications
            query = (
                select(Chatroom)
                .options(
                    joinedload(Chatroom.members),
                    joinedload(Chatroom.moderators),
                    joinedload(Chatroom.banned_users),
                )
                .where(Chatroom.uid == UUID(new_private_chatroom_uid))
            )
            executed_query = await test_session.execute(query)
            db_new_private_chatroom: Chatroom = (
                executed_query.unique().scalar_one_or_none()
            )

            assert db_new_private_chatroom is not None
            assert assigned_creator in db_new_private_chatroom.members
            assert assigned_creator in db_new_private_chatroom.moderators
            assert assigned_creator not in db_new_private_chatroom.banned_users
            assert assigned_creator.uid == db_new_private_chatroom.creator_uid

            admin_created_chatroom_uids_list.append(new_private_chatroom_uid)
            newly_created_chatroom_count += 1

            # try creating private chatroom with invalid_creator_username
            # should fail as provided username is not connected with any user account
            private_chatroom_create_data_with_invalid_creator_username = (
                private_chatroom_create_data_with_password.copy()
            )
            private_chatroom_create_data_with_invalid_creator_username.update(
                {
                    "original_creator_username": "invalidusername",
                }
            )
            post_admin_user_create_private_chatroom_with_invalid_creator_username_failed_response = test_client.post(
                "/admin/chat",
                json=private_chatroom_create_data_with_invalid_creator_username,
                headers={"Authorization": f"Bearer {self.admin_one_access_token}"},
            )
            assert (
                post_admin_user_create_private_chatroom_with_invalid_creator_username_failed_response.status_code
                == 404
            )

            # try creating chatroom without providing value for original creator username
            # should fail as field is required to link a user to a chatroom on creation via this endpoint
            private_chatroom_create_data_without_creator_username = (
                private_chatroom_create_data_with_password.copy()
            )
            if (
                "original_creator_username"
                in private_chatroom_create_data_without_creator_username.keys()
            ):
                del private_chatroom_create_data_without_creator_username[
                    "original_creator_username"
                ]
            post_admin_user_create_private_chatroom_without_creator_username_failed_response = test_client.post(
                "/admin/chat",
                json=private_chatroom_create_data_without_creator_username,
                headers={"Authorization": f"Bearer {self.admin_one_access_token}"},
            )
            assert (
                post_admin_user_create_private_chatroom_without_creator_username_failed_response.status_code
                == 422
            )

        # create comma seperated string of all the chatrooms that got created
        # for url query in further testings
        admin_created_chatroom_uids_list_string = ",".join(
            admin_created_chatroom_uids_list
        )

        # get all created chatrooms after creating new chatrooms
        get_all_created_chatrooms_after_creating_new_as_admin_user_response = (
            test_client.get(
                f"/admin/chat/all",
                headers={"Authorization": f"Bearer {self.admin_one_access_token}"},
            )
        )
        chatroom_count_after_creating_new_chatrooms = len(
            get_all_created_chatrooms_after_creating_new_as_admin_user_response.json().get(
                "chatrooms"
            )
        )
        # confirm that the length of all created chatrooms has increased by the count of newly created chatrooms
        assert chatroom_count_after_creating_new_chatrooms == (
            (
                chatroom_count_before_creating_new_chatrooms
                + newly_created_chatroom_count
            )
        )

        # confirm admin created chatrooms exist in database before deletion
        # retrieve info for each chatroom
        expected_chatroom_info_keys = {
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
        for chatroom_uid in admin_created_chatroom_uids_list:
            get_chatroom_info_before_deletion_as_admin_one_response = test_client.get(
                f"/admin/chat/?id={chatroom_uid}",
                headers={"Authorization": f"Bearer {self.admin_one_access_token}"},
            )
            assert (
                get_chatroom_info_before_deletion_as_admin_one_response.status_code
                == 200
            )
            assert expected_chatroom_info_keys.issubset(
                get_chatroom_info_before_deletion_as_admin_one_response.json().keys()
            )
            chatroom_info_uid = (
                get_chatroom_info_before_deletion_as_admin_one_response.json().get(
                    "uid"
                )
            )
            assert chatroom_info_uid == chatroom_uid

        # as admin user
        # try to mass delete chatrooms
        # should fail as only superuser can mass delete chatrooms
        delete_all_chatrooms_as_admin_one_failed_response = test_client.delete(
            f"/admin/chat/all?id={admin_created_chatroom_uids_list_string}",
            headers={"Authorization": f"Bearer {self.admin_one_access_token}"},
        )
        assert delete_all_chatrooms_as_admin_one_failed_response.status_code == 403
        ################################ LOGOUT ADMIN ########################################

        ################################ LOGIN GOODMAN5 - NORMAL USER ########################################
        # as goodman5 - normal user
        # try to mass delete chatrooms
        # should fail as only superuser can mass delete chatrooms
        delete_all_chatrooms_as_goodman_five_failed_response = test_client.delete(
            f"/admin/chat/all?id={admin_created_chatroom_uids_list_string}",
            headers={"Authorization": f"Bearer {self.goodman_five_access_token}"},
        )
        assert delete_all_chatrooms_as_goodman_five_failed_response.status_code == 403
        ################################ LOGOUT GOODMAN5 - NORMAL USER ########################################

        ################################ LOGIN SUPERUSER ########################################
        # as superuser
        # try to mass delete chatrooms
        # should succeed as only superuser can mass delete chatrooms
        delete_all_chatrooms_as_superuser_success_response = test_client.delete(
            f"/admin/chat/all?id={admin_created_chatroom_uids_list_string}",
            headers={"Authorization": f"Bearer {self.superuser_access_token}"},
        )
        assert delete_all_chatrooms_as_superuser_success_response.status_code == 200

        # confirm admin created chatrooms does not exist in database after deletion
        # retrieve info for each chatroom
        for chatroom_uid in admin_created_chatroom_uids_list:
            get_chatroom_info_after_deletion_as_superuser_response = test_client.get(
                f"/admin/chat/?id={chatroom_uid}",
                headers={"Authorization": f"Bearer {self.superuser_access_token}"},
            )
            assert (
                get_chatroom_info_after_deletion_as_superuser_response.status_code
                == 404
            )

        # confirm that the number of created chatrooms has decreased to the original value before new chatrooms creation
        ################################ LOGOUT SUPERUSER ########################################

    async def test_admin_chatroom_details_update(self, test_client, test_session):
        """
        test chatroom data update endpoint.
        endpoint is the same as normal chatroom update endpoint.
        endpoint must allow only the chatroom creator or an admin user to update the chatroom data.
        """
        # create new chatrooms with goodman1 as the creator
        # setting goodman one as the creator to confirm that update can be carried out by admin users, not just chatroom creator
        new_chatroom = Chatroom(
            name="chatroom for update",
            about="this chatroom is created to test admin update operations",
            room_type="private",
            original_creator_username=self.CHATROOM_OWNER_USERNAME,
        )
        test_session.add(new_chatroom)
        await test_session.commit()
        await test_session.refresh(new_chatroom)

        new_chatroom_uid = str(new_chatroom.uid)
        new_chatroom_about = (
            "this is the chatroom description above 24 characters long."
        )
        new_chatroom_password = "P@ssWord12223"

        ################################ LOGIN GOODMAN5 - NORMAL USER ########################################
        # logged in as goodman5 - normal user
        # try to update chatroom data
        # should fail as goodman5 is neither an admin user, nor the creator of the chatroom
        patch_chatroom_data_update_as_normal_user_five_failed_response = (
            test_client.patch(
                f"/admin/chat/?id={new_chatroom_uid}",
                headers={"Authorization": f"Bearer {self.goodman_five_access_token}"},
                json={
                    "name": "new name one",
                    "about": new_chatroom_about,
                },
            )
        )
        assert (
            patch_chatroom_data_update_as_normal_user_five_failed_response.status_code
            == 403
        )
        ################################ LOGOUT GOODMAN5 - NORMAL USER ########################################

        ################################ LOGIN ADMIN ########################################
        # try update chatroom data with password
        # should fail as only super user has the privilege to update chatroom password
        patch_chatroom_data_as_admin_with_password_failed_response = test_client.patch(
            f"/admin/chat/?id={new_chatroom_uid}",
            headers={"Authorization": f"Bearer {self.admin_one_access_token}"},
            json={
                "name": "new name one",
                "about": new_chatroom_about,
                "password": new_chatroom_password,
                "confirm_password": new_chatroom_password,
            },
        )
        delnow = patch_chatroom_data_as_admin_with_password_failed_response.json()
        assert (
            patch_chatroom_data_as_admin_with_password_failed_response.status_code
            == 403
        )

        # logged in as admin user
        # try to update chatroom data
        # should succeed as admin user possess the privilege
        patch_chatroom_data_as_admin_without_password_success_response = (
            test_client.patch(
                f"/admin/chat/?id={new_chatroom_uid}",
                headers={"Authorization": f"Bearer {self.admin_one_access_token}"},
                json={
                    "name": "new name one",
                    "about": new_chatroom_about,
                },
            )
        )
        assert (
            patch_chatroom_data_as_admin_without_password_success_response.status_code
            == 200
        )

        # try to update chatroom data with 'about' description less than 25 characters
        # should fail as 'about' is too short
        patch_chatroom_data_as_admin_with_short_about_value_password_failed_response = (
            test_client.patch(
                f"/admin/chat/?id={new_chatroom_uid}",
                headers={"Authorization": f"Bearer {self.admin_one_access_token}"},
                json={
                    "name": "new name one",
                    "about": "short about",
                },
            )
        )
        assert (
            patch_chatroom_data_as_admin_with_short_about_value_password_failed_response.status_code
            == 422
        )
        ################################ LOGOUT ADMIN ########################################

        ################################ LOGIN SUPERUSER ########################################
        # logged in as superuser
        # try to update chatroom data, complete with password
        # should succeed as admin superuser possess the privilege
        patch_chatroom_data_as_superuser_with_password_and_without_confirm_password_failed_response = test_client.patch(
            f"/admin/chat/?id={new_chatroom_uid}",
            headers={"Authorization": f"Bearer {self.superuser_access_token}"},
            json={
                "name": "new name one",
                "about": new_chatroom_about,
                "password": new_chatroom_password,
            },
        )
        assert (
            patch_chatroom_data_as_superuser_with_password_and_without_confirm_password_failed_response.status_code
            == 422
        )

        patch_chatroom_data_as_superuser_with_password_and_incorrect_confirm_password_failed_response = test_client.patch(
            f"/admin/chat/?id={new_chatroom_uid}",
            headers={"Authorization": f"Bearer {self.superuser_access_token}"},
            json={
                "name": "new name one",
                "about": new_chatroom_about,
                "password": new_chatroom_password,
                "confirm_password": "1nc0RR#ct-Confirm-p@ssw0rd",
            },
        )
        assert (
            patch_chatroom_data_as_superuser_with_password_and_incorrect_confirm_password_failed_response.status_code
            == 422
        )

        patch_chatroom_data_as_superuser_with_password_and_correct_confirm_password_success_response = test_client.patch(
            f"/admin/chat/?id={new_chatroom_uid}",
            headers={"Authorization": f"Bearer {self.superuser_access_token}"},
            json={
                "name": "new name one",
                "about": new_chatroom_about,
                "password": new_chatroom_password,
                "confirm_password": new_chatroom_password,
            },
        )
        assert (
            patch_chatroom_data_as_superuser_with_password_and_correct_confirm_password_success_response.status_code
            == 200
        )
        ################################ LOGOUT SUPERUSER ########################################

        # clear chatroom used for test
        await test_session.delete(new_chatroom)
        await test_session.commit()
