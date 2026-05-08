import { ChatroomExtended, ChatroomExtendedSchema } from "../../../schemas/ChatSchemas";
import useSetPageTitle from "../../../hooks/useSetPageTitle";
import ConfirmActionDialogue from "../../../components/general/modals/ConfirmActionDialogue";
import useAxios from "../../../hooks/useAxios";
import { useEffect, useState } from "react";
import { useNavigate, useParams } from "react-router-dom";
import { ChatroomRecordingSwitchDialogue } from "../../preview/ChatroomPreview";
import { UUID } from "crypto";
import FetchingLoader from "../../../components/general/loaders/FetchingLoader";
import { Link } from "react-router-dom";

import "./UserChatInformation.css";
import useHandleError from "../../../hooks/useHandleError";
import { AnimatePresence } from "framer-motion";
import APIResponsePopup from "../../../components/general/modals/APIResponsePopup";
import FetchErrorSignal from "../../../components/general/modals/FetchErrorModal";

import { ReactComponent as DeleteIcon } from "../../../assets/icons/trash-bin-icon.svg";
import { ReactComponent as EyeOpenIcon } from "../../../assets/icons/eye-open-icon.svg";
import { ReactComponent as EyeCloseIcon } from "../../../assets/icons/eye-close-icon.svg";

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
      {(!chatroomDetails && isFetching && <FetchingLoader />) ||
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
                <div className="text-icon-container">
                  <DeleteIcon className="icon" aria-label="trash bin icon" />
                  <span>delete chat</span>
                </div>
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
                <div className="text-icon-container">
                  {(chatroomDetails.secret_mode && (
                    <EyeCloseIcon className="icon" aria-label="eye close icon" />
                  )) || <EyeOpenIcon className="icon" aria-label="eye open icon" />}
                  <span>{(chatroomDetails.secret_mode && "secret") || "recorded"}</span>
                </div>
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
