import { Chatroom, ChatroomSchema } from "../../../schemas/ChatSchemas";
import useSetPageTitle from "../../../hooks/useSetPageTitle";
import FormErrorModal from "../../../components/general/modals/FormErrorModal";
import ConfirmActionDialogue from "../../../components/general/confirmationModals/ConfirmActionDialogue";
import useAxios from "../../../hooks/useAxios";
import { useEffect, useState } from "react";
import { useNavigate, useParams } from "react-router-dom";
import { ChatroomRecordingSwitchDialogue } from "../../Preview/ChatroomPreview";
import { UUID } from "crypto";
import LineLoadingSignal from "../../../components/general/fetchModals/LineLoadingModal";
import { Link } from "react-router-dom";

import "./UserChatInformation.css";
import useHandleError from "../../../hooks/useHandleError";
import APIResponsePopup from "../../../components/general/fetchModals/APIResponsePopup";
import { AnimatePresence } from "framer-motion";

export default function UserChatInformation() {
  const { chatID } = useParams();
  const [chatroomDetails, setChatroomDetails] = useState<Chatroom>();
  const [showConfirmChatDeleteDialogue, setShowConfirmChatDeleteDialogue] = useState(false);
  const [showSetRecordingDialogue, setShowSetRecordingDialogue] = useState(false);
  const [isFetching, setIsFetching] = useState(false);
  const axios = useAxios();
  const navigate = useNavigate();

  const [errorMessage, setErrorMessage] = useState<string>();
  const apiErrorHandler = useHandleError();

  const _ = useSetPageTitle(`chat ${chatID}`);

  const handleConfirmClick = () => {
    setShowConfirmChatDeleteDialogue(true);
  };
  const handleShowRecordingSwitchDialogue = () => {
    setShowSetRecordingDialogue(true);
  };
  const handleDeleteChatButton = () => {
    setIsFetching(true);
    setErrorMessage(undefined);
    axios
      .delete(`/chat/private/room/friends/conversation?username=${chatID}`)
      .then((res) => {
        navigate("/chat/friends");
      })
      .catch((err) => {
        apiErrorHandler({ err, setErrorMessage });
      })
      .finally(() => {
        setIsFetching(false);
      });
  };

  const fetchChatroomDetails = () => {
    setIsFetching(true);
    axios
      .get(`/chat/private/room/friends/conversation?username=${chatID}`)
      .then((res) => {
        const parsedChatroomData = ChatroomSchema.parse(res.data);
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
  }, []);

  return (
    <div className="page-container user-chat-information-page">
      {(!chatroomDetails && isFetching && <LineLoadingSignal />) ||
        (!chatroomDetails && !isFetching && errorMessage && (
          <FormErrorModal errorMessage={errorMessage} />
        )) ||
        (chatroomDetails && (
          <>
            <div className="section grow">
              <Link to={`/preview/user/${chatID}`} className="title">
                @{chatID}
              </Link>
              <button className="btn danger confirm-button" onClick={handleConfirmClick}>
                delete chat
              </button>
              {showConfirmChatDeleteDialogue && (
                <ConfirmActionDialogue setModalDisplayState={setShowConfirmChatDeleteDialogue}>
                  <p className="title">this chat will be cleared for both you and {chatID}.</p>
                  <button
                    className="btn danger"
                    onClick={handleDeleteChatButton}
                    disabled={isFetching}
                  >
                    confirm
                  </button>
                </ConfirmActionDialogue>
              )}
              <button className="btn add-btn" onClick={handleShowRecordingSwitchDialogue}>
                {(chatroomDetails.record_messages && "disable") || "allow"} messages saves
              </button>
              {showSetRecordingDialogue && (
                <ChatroomRecordingSwitchDialogue
                  chatroomUID={chatroomDetails.uid as UUID}
                  setShow={setShowSetRecordingDialogue}
                  successFunction={fetchChatroomDetails}
                  currentRecordingStatus={chatroomDetails.record_messages}
                />
              )}
            </div>
            <AnimatePresence>
              {errorMessage && (
                <APIResponsePopup
                  popupType="fail"
                  message={errorMessage}
                  setMessage={setErrorMessage}
                />
              )}
            </AnimatePresence>
          </>
        ))}
    </div>
  );
}
