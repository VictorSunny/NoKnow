import useAxios from "../../../../hooks/useAxios";
import {
  ChatroomRecordingSwitchDialogue,
  PrivateChatroomJoinDialogue,
  PrivateChatroomLeaveDialogue,
} from "../../../preview/ChatroomPreview";
import { ChatroomExtended, ChatroomExtendedSchema } from "../../../../schemas/ChatSchemas";
import { UUID } from "crypto";
import { useEffect, useState } from "react";
import { useLocation, useNavigate, useParams } from "react-router-dom";
import useSetPageTitle from "../../../../hooks/useSetPageTitle";
import { useAuthContext } from "../../../../contexts/AuthContext";

import "./ChatroomMetadataWindow.css";
import SpinnerLoader from "../../../../components/general/loaders/SpinnerLoader";
import { AnimatePresence } from "framer-motion";
import ConfirmActionDialogue from "../../../../components/general/modals/ConfirmActionDialogue";
import useGetAnonymousUsername from "../../../../hooks/useGetAnonymousUsername";
import useHandleError from "../../../../hooks/useHandleError";
import { SetBoolState } from "../../../../types/types";
import FetchErrorSignal from "../../../../components/general/modals/FetchErrorModal";
import APIResponsePopup from "../../../../components/general/modals/APIResponsePopup";

export default function ChatroomMetadataWindow() {
  const { chatroomUID } = useParams();
  const { userDetails } = useAuthContext();
  const anonymousUsername = useGetAnonymousUsername();

  const [chatroomDetails, setChatroomDetails] = useState<ChatroomExtended>();
  const [showJoinChatroomDialogue, setShowJoinChatroomDialogue] = useState(false);
  const [showConfirmLeaveDialogue, setShowConfirmLeaveDialogue] = useState(false);
  const [showSetRecordingDialogue, setShowSetRecordingDialogue] = useState(false);
  const [showDeleteDialogue, setShowDeleteDialogue] = useState(false);

  const [isFetching, setIsFetching] = useState(false);
  const [errorMessage, setErrorMessage] = useState<string>();
  const apiErrorHandler = useHandleError();

  const navigate = useNavigate();
  const location = useLocation();

  const { accessTokenData } = useAuthContext();

  const _ = useSetPageTitle("chatroom meta");

  const axios = useAxios();

  const fetchChatroomDetails = () => {
    setIsFetching(true);
    axios
      .get(`/chat?chatroom_identifier=${chatroomUID}`)
      .then((res) => {
        const parsedChatroomData = ChatroomExtendedSchema.parse(res.data);
        setChatroomDetails(parsedChatroomData);
      })
      .catch((err) => {
        apiErrorHandler({ err, setErrorMessage });
      })
      .finally(() => {
        setIsFetching(false);
      });
  };

  useEffect(() => {
    fetchChatroomDetails();
  }, [accessTokenData]);

  const handleJoinChatroomClick = () => {
    setShowJoinChatroomDialogue(true);
  };
  const handleShowConfirmDialogue = () => {
    setShowConfirmLeaveDialogue(true);
  };
  const handleShowRecordingSwitchDialogue = () => {
    setShowSetRecordingDialogue(true);
  };
  const handleShowDeleteDialogue = () => {
    setShowDeleteDialogue(true);
  };
  const handleSetAnonymousClick = () => {
    navigate("/chat/alias", { state: { from: location }, replace: true });
  };

  return (
    <div className="window chat-details-window">
      <AnimatePresence>
        {(!chatroomDetails && isFetching && <SpinnerLoader />) ||
          (!chatroomDetails && !isFetching && errorMessage && (
            <FetchErrorSignal errorMessage={errorMessage} />
          )) ||
          (chatroomDetails && (
            <>
              <div className="window-section hero-container">
                <p className="chatroom-name title">{chatroomDetails.name}</p>
                <p className="chatroom-about">{chatroomDetails.about}</p>
              </div>
              <div className="window-section meta-data-container">
                <table>
                  <tbody>
                    <tr>
                      <th>username:</th>
                      <td className="username">
                        {(userDetails && !chatroomDetails.user_is_hidden && userDetails.username) ||
                          anonymousUsername}
                      </td>
                    </tr>
                    <tr>
                      <th>anonymous:</th>
                      <td>{(chatroomDetails.user_is_hidden && "yes") || "no"}</td>
                    </tr>
                    <tr>
                      <th>status:</th>
                      <td>
                        {(chatroomDetails.user_status != "removed" &&
                          chatroomDetails.user_status) ||
                          "guest"}
                      </td>
                    </tr>
                    <tr>
                      <th>members:</th>
                      <td>{chatroomDetails.members_count}</td>
                    </tr>
                    <tr>
                      <th>active visitors:</th>
                      {/* active visitors plus 1 as the user viewing this page is a visitor, */}
                      {/* but back-end api only recognizes connected websocket as active user */}
                      {/* user disconnects from websocket to view this page but should be counted regardless */}
                      <td>{chatroomDetails.active_visitors + 1}</td>
                    </tr>
                    <tr>
                      <th>type:</th>
                      <td>{chatroomDetails.room_type}</td>
                    </tr>
                    <tr>
                      <th>created:</th>
                      <td>{chatroomDetails.created_at}</td>
                    </tr>
                    <tr>
                      <th>original creator:</th>
                      <td>{chatroomDetails.original_creator_username}</td>
                    </tr>
                    <tr>
                      <th>recorded:</th>
                      <td>{(chatroomDetails.secret_mode && "no") || "yes"}</td>
                    </tr>
                  </tbody>
                </table>
              </div>
              <div className="window-section util-container">
                <button className="btn" onClick={handleSetAnonymousClick}>
                  set anonymous username
                </button>
                {(chatroomDetails.user_status != "removed" && (
                  <>
                    <button className="btn danger" onClick={handleShowConfirmDialogue}>
                      leave chat
                    </button>
                    {showConfirmLeaveDialogue && (
                      <PrivateChatroomLeaveDialogue
                        setShow={setShowConfirmLeaveDialogue}
                        chatroomUID={chatroomDetails.uid as UUID}
                      />
                    )}
                  </>
                )) || (
                  <>
                    <button className="btn positive" onClick={handleJoinChatroomClick}>
                      join chat
                    </button>
                    {showJoinChatroomDialogue && (
                      <PrivateChatroomJoinDialogue
                        chatroomType={chatroomDetails.room_type}
                        chatroomUID={chatroomUID as UUID}
                        setShow={setShowJoinChatroomDialogue}
                        navigateToChat={true}
                      />
                    )}
                  </>
                )}

                {(chatroomDetails.user_status == "creator" ||
                  chatroomDetails.user_status == "moderator") && (
                  <>
                    <button className="btn" onClick={handleShowRecordingSwitchDialogue}>
                      chat is {(chatroomDetails.secret_mode && "secret") || "recorded"}
                    </button>
                    {showSetRecordingDialogue && (
                      <ChatroomRecordingSwitchDialogue
                        chatroomUID={chatroomDetails.uid as UUID}
                        setShow={setShowSetRecordingDialogue}
                        successFunction={fetchChatroomDetails}
                        secretModeActive={chatroomDetails.secret_mode}
                      />
                    )}
                  </>
                )}
                {chatroomDetails.user_status == "creator" && (
                  <>
                    <button className="btn danger" onClick={handleShowDeleteDialogue}>
                      delete chatroom
                    </button>
                    {showDeleteDialogue && (
                      <ChatroomDeleteDialogue
                        chatroomUID={chatroomUID as UUID}
                        setShow={setShowDeleteDialogue}
                      />
                    )}
                  </>
                )}
              </div>
            </>
          ))}
      </AnimatePresence>
    </div>
  );
}

type ChatroomDeleteDialogueProps = {
  chatroomUID: UUID;
  setShow: SetBoolState;
};
export function ChatroomDeleteDialogue({ chatroomUID, setShow }: ChatroomDeleteDialogueProps) {
  const [isFetching, setIsFetching] = useState(false);
  const axios = useAxios();
  const navigate = useNavigate();

  const [successMessage, setSuccessMessage] = useState<string>();

  const [errorMessage, setErrorMessage] = useState<string>();
  const apiErrorHandler = useHandleError();

  const handleDeleteChatroomClick = () => {
    setIsFetching(true);
    axios
      .delete(`/chat?id=${chatroomUID}`)
      .then(() => {
        setSuccessMessage("chatroom deleted.");
      })
      .catch((err) => {
        apiErrorHandler({ err, setErrorMessage });
      })
      .finally(() => {
        setIsFetching(false);
      });
  };

  return (
    <ConfirmActionDialogue setModalDisplayState={setShow}>
      <p className="title">confirm you want to delete chatroom. this action cannot be reversed</p>
      <button
        type="submit"
        className="btn danger"
        aria-label={`submit join chatroom form ${(isFetching && "load") || ""}`}
        disabled={isFetching}
        onClick={handleDeleteChatroomClick}
      >
        delete
      </button>
      <AnimatePresence>
        {errorMessage && (
          <APIResponsePopup popupType="fail" message={errorMessage} setMessage={setErrorMessage} />
        )}
        {successMessage && (
          <APIResponsePopup
            popupType="success"
            message={successMessage}
            setMessage={setSuccessMessage}
            successAction={() => {
              navigate("/chat");
            }}
          />
        )}
      </AnimatePresence>
    </ConfirmActionDialogue>
  );
}
