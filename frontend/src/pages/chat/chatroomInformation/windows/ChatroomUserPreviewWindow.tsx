import SpinnerLoader from "../../../../components/general/loaders/SpinnerLoader";
import useAxios from "../../../../hooks/useAxios";
import { AxiosInstance } from "axios";
import { useEffect, useState } from "react";
import { useParams } from "react-router-dom";
import { UUID } from "crypto";
import useGetLoggedInUser from "../../../../hooks/useGetLoggedInUser";
import { ChatroomUser, ChatroomUserSchema } from "../../../../schemas/ChatSchemas";
import ConfirmActionDialogue from "../../../../components/general/modals/ConfirmActionDialogue";
import { Link } from "react-router-dom";
import { AnimatePresence } from "framer-motion";
import useHandleError from "../../../../hooks/useHandleError";
import { SetOptionalTextState } from "../../../../types/types";
import ReloadSignal from "../../../../components/general/modals/ReloadModal";
import APIResponsePopup from "../../../../components/general/modals/APIResponsePopup";

export default function ChatroomUserPreviewWindow() {
  const { chatroomUID, username } = useParams();

  const [previewedUserDetails, setPreviewedUserDetails] = useState<ChatroomUser>();
  const [loggedInUserDetails, setLoggedInUserDetails] = useState<ChatroomUser>();

  const [isFetching, setIsFetching] = useState(false);
  const [errorMessage, setErrorMessage] = useState<string>();
  const apiErrorHandler = useHandleError();

  const userDetails = useGetLoggedInUser({ setErrorMessage });

  const axios = useAxios();

  // gets data for the user being previewed with details of their role in the chatroom
  const FetchPreviewedUserAction = () => {
    setIsFetching(true);
    axios
      .get(`/chat/check/${chatroomUID}/user?username=${username}`)
      .then((res) => {
        const parsedData = ChatroomUserSchema.parse(res.data);
        setPreviewedUserDetails(parsedData);
      })
      .catch((err) => {
        apiErrorHandler({ err, setErrorMessage });
      })
      .finally(() => {
        setIsFetching(false);
      });
  };

  // gets data for the logged in user with details of their role in the chatroom
  const fetchLoggedInUserAction = () => {
    axios
      .get(`/chat/check/${chatroomUID}/user`)
      .then((res) => {
        const parsedData = ChatroomUserSchema.parse(res.data);
        setLoggedInUserDetails(parsedData);
      })
      .catch((err) => {
        apiErrorHandler({ err, setErrorMessage });
      });
  };

  // fetch necessary users data
  useEffect(() => {
    FetchPreviewedUserAction();
    fetchLoggedInUserAction();
  }, [userDetails]);

  useEffect(() => {
    if (loggedInUserDetails && previewedUserDetails) {
      setErrorMessage(undefined);
    }
  }, [loggedInUserDetails, previewedUserDetails]);

  return (
    <div className="window chatroom-user-preview-window">
      {(!previewedUserDetails && !loggedInUserDetails && isFetching && <SpinnerLoader />) ||
        ((!previewedUserDetails || !loggedInUserDetails) && errorMessage && (
          <ReloadSignal
            isFetching={isFetching}
            isFetchingNextPage={isFetching}
            refreshClickFn={FetchPreviewedUserAction}
          >
            {errorMessage}
          </ReloadSignal>
        )) ||
        (previewedUserDetails && loggedInUserDetails && (
          <>
            <div className="window-section user-info-section">
              <Link
                className="title username"
                to={`/preview/user/${previewedUserDetails.username}`}
              >
                {previewedUserDetails.username}
              </Link>
              <strong>
                {(previewedUserDetails.user_status != "removed" &&
                  previewedUserDetails.user_status) ||
                  "non-member"}
              </strong>
              <p className="info medium-spaced">{previewedUserDetails.bio}</p>
            </div>
            <AnimatePresence>
              {
                // If the previewed user is not a member and the logged user is the chatroom creator or moderator,
                (loggedInUserDetails.user_status == "creator" ||
                  loggedInUserDetails.user_status == "moderator") && (
                  <div className="window-section grow">
                    {
                      // if the previewed user is not alrady a member
                      // render button allowing the chatroom creator/moderator to add the previewed user to chatroom members
                      (previewedUserDetails.user_status == "removed" && (
                        <AddRemoveUserButton
                          actionChoice="add"
                          axiosInstance={axios}
                          userUID={previewedUserDetails.uid as UUID}
                          errorMessage={errorMessage}
                          setErrorMessage={setErrorMessage}
                          chatroomUID={chatroomUID as UUID}
                          username={previewedUserDetails.username}
                          roleToAssign="member"
                          refreshFn={FetchPreviewedUserAction}
                        />
                      )) ||
                        // if the previewed user is a member
                        // render button allowing the chatroom creator/moderator to remove the previewed user from chatroom members
                        (previewedUserDetails.user_status == "member" && (
                          <>
                            <AddRemoveUserButton
                              actionChoice="remove"
                              axiosInstance={axios}
                              userUID={previewedUserDetails.uid as UUID}
                              errorMessage={errorMessage}
                              setErrorMessage={setErrorMessage}
                              chatroomUID={chatroomUID as UUID}
                              username={previewedUserDetails.username}
                              roleToAssign="member"
                              refreshFn={FetchPreviewedUserAction}
                            />

                            {
                              // if the previewed user is a moderator and the logged in user is the chatroom creator
                              // render button allowing the logged in user to add the previewed user to chatroom moderators
                              loggedInUserDetails.user_status == "creator" && (
                                <AddRemoveUserButton
                                  actionChoice="add"
                                  axiosInstance={axios}
                                  userUID={previewedUserDetails.uid as UUID}
                                  errorMessage={errorMessage}
                                  setErrorMessage={setErrorMessage}
                                  chatroomUID={chatroomUID as UUID}
                                  username={previewedUserDetails.username}
                                  roleToAssign="moderator"
                                  refreshFn={FetchPreviewedUserAction}
                                />
                              )
                            }
                          </>
                        )) ||
                        // If the previewed user is a moderator or successor, and the logged in user is the chatroom creator
                        // render buttons allow logged in user to remove the previewed user from moderators, remove from members,
                        // or assign the role of successor (if the previewed user is not already the successor)
                        ((previewedUserDetails.user_status == "moderator" ||
                          previewedUserDetails.user_status == "successor") &&
                          loggedInUserDetails.user_status == "creator" && (
                            <>
                              <AddRemoveUserButton
                                actionChoice="remove"
                                axiosInstance={axios}
                                userUID={previewedUserDetails.uid as UUID}
                                errorMessage={errorMessage}
                                setErrorMessage={setErrorMessage}
                                chatroomUID={chatroomUID as UUID}
                                username={previewedUserDetails.username}
                                roleToAssign="moderator"
                                refreshFn={FetchPreviewedUserAction}
                              />
                              <AddRemoveUserButton
                                actionChoice="remove"
                                axiosInstance={axios}
                                userUID={previewedUserDetails.uid as UUID}
                                errorMessage={errorMessage}
                                setErrorMessage={setErrorMessage}
                                chatroomUID={chatroomUID as UUID}
                                username={previewedUserDetails.username}
                                roleToAssign="member"
                                refreshFn={FetchPreviewedUserAction}
                              />
                              {previewedUserDetails.user_status != "successor" && (
                                <AddRemoveUserButton
                                  actionChoice="add"
                                  axiosInstance={axios}
                                  userUID={previewedUserDetails.uid as UUID}
                                  errorMessage={errorMessage}
                                  setErrorMessage={setErrorMessage}
                                  chatroomUID={chatroomUID as UUID}
                                  username={previewedUserDetails.username}
                                  roleToAssign="successor"
                                  refreshFn={FetchPreviewedUserAction}
                                />
                              )}
                            </>
                          )) ||
                        // if the previewed user is a member, and the logged in user is a creator
                        // render button allowing the logged in user to add the previewed user to moderators
                        (previewedUserDetails.user_status == "member" &&
                          loggedInUserDetails.user_status == "creator" && (
                            <AddRemoveUserButton
                              actionChoice="add"
                              axiosInstance={axios}
                              userUID={previewedUserDetails.uid as UUID}
                              errorMessage={errorMessage}
                              setErrorMessage={setErrorMessage}
                              chatroomUID={chatroomUID as UUID}
                              username={previewedUserDetails.username}
                              roleToAssign="moderator"
                              refreshFn={FetchPreviewedUserAction}
                            />
                          ))
                    }
                  </div>
                )
              }
            </AnimatePresence>
          </>
        ))}
    </div>
  );
}

type AddRemoveUser = "add" | "remove";
type RoleToAssign = "successor" | "moderator" | "member";
type MembershipButtonProps = {
  axiosInstance: AxiosInstance;
  userUID: UUID;
  chatroomUID: UUID;
  username: string;
  errorMessage: string | undefined;
  setErrorMessage: SetOptionalTextState;
  actionChoice: AddRemoveUser;
  roleToAssign: RoleToAssign;
  refreshFn: () => void;
};
function AddRemoveUserButton({
  axiosInstance,
  userUID,
  username,
  chatroomUID,
  errorMessage,
  setErrorMessage,
  actionChoice,
  roleToAssign,
  refreshFn,
}: MembershipButtonProps) {
  const [successMessage, setSuccessMessage] = useState<string>();
  const [showConfirmationDialogue, setShowConfirmationDialogue] = useState(false);
  const [isFetching, setIsFetching] = useState(false);
  const apiErrorHandler = useHandleError();
  const handleOnClick = () => {
    setErrorMessage(undefined);
    const fetchURLPrefix =
      (roleToAssign == "moderator" &&
        `/chat/private/room/members/${chatroomUID}/${actionChoice}/moderator`) ||
      (roleToAssign == "successor" &&
        `/chat/private/room/members/${chatroomUID}/${actionChoice}/successor`) ||
      `/chat/private/room/members/${chatroomUID}/${actionChoice}`;
    axiosInstance
      .post(`${fetchURLPrefix}?user_uid=${userUID}`)
      .then((res) => {
        setSuccessMessage(res.data.message);
        refreshFn();
      })
      .catch((err) => {
        apiErrorHandler({ err, setErrorMessage });
      })
      .finally(() => {
        setIsFetching(false);
      });
  };

  const confirmPrompt =
    (roleToAssign == "successor" && `make @${username} your successor?`) ||
    (roleToAssign == "moderator" &&
      `${actionChoice} @${username} ${(actionChoice == "add" && "to") || "from"} moderators`) ||
    (roleToAssign == "member" &&
      `${actionChoice} ${(actionChoice == "add" && "to") || "from"} members`);

  return (
    <>
      <button
        className="btn positive-btn"
        name="button"
        aria-label={`${actionChoice} user to chatroom`}
        onClick={() => setShowConfirmationDialogue(true)}
      >
        {actionChoice} {roleToAssign}
      </button>
      {showConfirmationDialogue && (
        <ConfirmActionDialogue setModalDisplayState={setShowConfirmationDialogue}>
          <p className="title">are you sure you want to {confirmPrompt}</p>
          <button
            disabled={isFetching}
            className={(isFetching && "load") || ""}
            onClick={handleOnClick}
          >
            confirm
          </button>
          <AnimatePresence>
            {errorMessage && (
              <APIResponsePopup
                popupType="fail"
                message={errorMessage}
                setMessage={setErrorMessage}
              />
            )}
            {successMessage && (
              <APIResponsePopup
                popupType="success"
                message={successMessage}
                setMessage={setSuccessMessage}
                successAction={() => {
                  setShowConfirmationDialogue(false);
                }}
              />
            )}
          </AnimatePresence>
        </ConfirmActionDialogue>
      )}
    </>
  );
}
