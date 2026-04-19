import { ChatroomExtended, ChatroomExtendedSchema } from "../../../schemas/ChatSchemas";
import useSetPageTitle from "../../../hooks/useSetPageTitle";
import ConfirmActionDialogue from "../../../components/general/modals/ConfirmActionDialogue";
import useAxios from "../../../hooks/useAxios";
import { useEffect, useState } from "react";
import { useNavigate, useParams } from "react-router-dom";
import { ChatroomRecordingSwitchDialogue } from "../../preview/ChatroomPreview";
import { UUID } from "crypto";
import SpinnerLoader from "../../../components/general/loaders/SpinnerLoader";
import { Link } from "react-router-dom";

import "./UserChatInformation.css";
import useHandleError from "../../../hooks/useHandleError";
import { AnimatePresence } from "framer-motion";
import APIResponsePopup from "../../../components/general/modals/APIResponsePopup";
import FetchErrorSignal from "../../../components/general/modals/FetchErrorModal";

export default function UserChatInformation() {
  const { chatID } = useParams();
  const [chatroomDetails, setChatroomDetails] = useState<ChatroomExtended>();
  const [showConfirmChatDeleteDialogue, setShowConfirmChatDeleteDialogue] = useState(false);
  const [showSetRecordingDialogue, setShowSetRecordingDialogue] = useState(false);
  const [isFetching, setIsFetching] = useState(false);
  const axios = useAxios();
  const navigate = useNavigate();

  const [errorMessage, setErrorMessage] = useState<string>();
  const apiErrorHandler = useHandleError();

  const _ = useSetPageTitle(`chat ${chatID}`);

  const handleDeleteChatButton = () => {
    setIsFetching(true);
    setErrorMessage(undefined);
    axios
      .delete(`/chat?chatroom_identifier=${chatID}`)
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
      .get(`/chat?chatroom_identifier=${chatID}`)
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
  }, []);

  return (
    <div className="page-container user-chat-information-page">
      {(!chatroomDetails && isFetching && <SpinnerLoader />) ||
        (!chatroomDetails && !isFetching && errorMessage && (
          <FetchErrorSignal errorMessage={errorMessage} />
        )) ||
        (chatroomDetails && (
          <>
            <div className="section grow">
              <Link to={`/preview/user/${chatID}`} className="title">
                @{chatID}
              </Link>
              <button
                className="btn danger confirm-button"
                onClick={() => {
                  setShowConfirmChatDeleteDialogue(true);
                }}
              >
                delete chat
              </button>
              {showConfirmChatDeleteDialogue && (
                <ConfirmActionDialogue setModalDisplayState={setShowConfirmChatDeleteDialogue}>
                  <p className="title">this chat will be cleared for both you and {chatID}.</p>
                  <button
                    className={`btn danger ${(isFetching && "load") || ""}`}
                    onClick={handleDeleteChatButton}
                    disabled={isFetching}
                  >
                    confirm
                  </button>
                </ConfirmActionDialogue>
              )}
              <button
                className="btn add-btn"
                onClick={() => {
                  setShowSetRecordingDialogue(true);
                }}
              >
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
