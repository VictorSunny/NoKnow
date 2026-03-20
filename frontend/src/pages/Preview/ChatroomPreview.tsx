import { useNavigate, useParams } from "react-router-dom";
import { SetStateAction, useEffect, useRef, useState } from "react";
import { ChatroomExtended, ChatroomExtendedListSchema } from "../../schemas/ChatSchemas";
import useAxios from "../../hooks/useAxios";
import { UUID } from "crypto";
import { Link } from "react-router-dom";
import getFormEntries from "../../utilities/getFormEntries";
import FetchErrorSignal from "../../components/general/fetchModals/FetchErrorModal";
import useSetPageTitle from "../../hooks/useSetPageTitle";
import ConfirmActionDialogue from "../../components/general/confirmationModals/ConfirmActionDialogue";

import "./ChatroomPreview.css";
import "./Preview.css";
import useHandleError from "../../hooks/useHandleError";
import { ChatroomPrivacyTypes } from "../../types/chatroomTypes";
import { SinglePasswordSchema } from "../../schemas/GenericSchemas";
import { AnimatePresence } from "framer-motion";
import APIResponsePopup from "../../components/general/fetchModals/APIResponsePopup";
import FormErrorModal from "../../components/general/modals/FormErrorModal";
import { SetBoolState } from "../../types/types";

function ChatroomPreview() {
  const { chatroomUID } = useParams();
  const [chatroomDetails, setChatroomDetails] = useState<ChatroomExtended>();
  const [chatroomIsProtected, setChatroomIsProtected] = useState(false);
  const [showJoinChatroomDialogue, setShowJoinChatroomDialogue] = useState(false);
  const [isFetching, setIsFetching] = useState(false);

  const [errorMessage, setErrorMessage] = useState<string>();
  const apiErrorHandler = useHandleError();

  const _ = useSetPageTitle(
    (chatroomDetails?.name && `chatroom: ${chatroomDetails.name}`) || "chatroom"
  );

  const axios = useAxios();

  const setChatroomExtendedDetails = () => {
    setIsFetching(true);
    axios
      .get(`/chat/all?id=${chatroomUID}`)
      .then((res) => {
        const parsedChatroomData = ChatroomExtendedListSchema.parse(res.data).chatrooms[0];
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
    setChatroomExtendedDetails();
  }, []);

  useEffect(() => {
    if (chatroomDetails?.user_status == "removed" && chatroomDetails?.room_type == "private") {
      setChatroomIsProtected(true);
    }
  }, [chatroomDetails]);

  const handleJoinChatroomClick = async () => {
    setShowJoinChatroomDialogue(true);
  };

  return (
    <div className="page-container preview-page-container chatroom-preview-page-container">
      {(chatroomDetails && (
        <>
          <div className="section">
            <div className="preview-intro">
              <strong className="name title">{chatroomDetails.name}</strong>
              <p className="info">{chatroomDetails.about}</p>
            </div>
          </div>

          <div className="section">
            <table>
              <tr>
                <th>
                  <span className="chatroom-active-user-count">active visitors:</span>
                </th>
                <td>
                  <span>{chatroomDetails.active_visitors}</span>
                </td>
              </tr>
              <tr>
                <th>
                  <span className="chatroom-active-user-count">members:</span>
                </th>
                <td>
                  <span>{chatroomDetails.members_count}</span>
                </td>
              </tr>
            </table>
          </div>

          <div className="section">
            <div className="preview-btns-container">
              {(chatroomIsProtected && (
                <button className="btn preview-btn positive" onClick={handleJoinChatroomClick}>
                  join chat
                </button>
              )) || (
                <Link
                  to={`/chat/engage/chatroom/${chatroomDetails.uid}`}
                  className="btn preview-btn"
                >
                  enter
                </Link>
              )}
            </div>
          </div>
          {showJoinChatroomDialogue && (
            <PrivateChatroomJoinDialogue
              chatroomUID={chatroomDetails.uid as UUID}
              setShow={setShowJoinChatroomDialogue}
              chatroomType={chatroomDetails.room_type}
              navigateToChat={true}
            />
          )}
        </>
      )) ||
        (!isFetching && (
          <FetchErrorSignal errorMessage={errorMessage ?? "unable to get chatroom info"} />
        ))}
    </div>
  );
}

export default ChatroomPreview;

type PrivateChatroomJoinDialogueProps = {
  chatroomUID: UUID;
  setShow: SetBoolState;
  chatroomType: ChatroomPrivacyTypes;
  navigateToChat?: boolean;
};
export function PrivateChatroomJoinDialogue({
  chatroomUID,
  chatroomType,
  navigateToChat,
  setShow,
}: PrivateChatroomJoinDialogueProps) {
  const [isFetching, setIsFetching] = useState(false);
  const passwordInputRef = useRef<HTMLInputElement>(null);
  const axios = useAxios();
  const navigate = useNavigate();

  const [successMessage, setSuccessMessage] = useState<string>();
  const [errorMessage, setErrorMessage] = useState<string>();
  const [errorPath, setErrorPath] = useState<string>();
  const apiErrorHandler = useHandleError();

  useEffect(() => {
    passwordInputRef.current?.focus();
  }, []);

  const handleJoinFormSubmit = async (e: React.FormEvent<HTMLFormElement>) => {
    e.preventDefault();
    setErrorMessage(undefined);
    setIsFetching(true);

    const passwordForm = getFormEntries(e.currentTarget);
    const parsedPasswordData = SinglePasswordSchema.parse(passwordForm);

    await axios
      .post(`/chat/private/room/join/${chatroomUID}`, parsedPasswordData)
      .then(() => {
        setSuccessMessage("you are now a member of this chatroom.");
      })
      .catch((err) => {
        apiErrorHandler({ err, setErrorMessage, setErrorPath });
      })
      .finally(() => {
        setIsFetching(false);
      });
  };

  return (
    <ConfirmActionDialogue setModalDisplayState={setShow}>
      <p className="title">enter password to join</p>
      <form
        name="chatroom-password-form"
        className="chatroom-password-form confirm-form"
        onSubmit={handleJoinFormSubmit}
        method="POST"
      >
        {chatroomType == "private" && (
          <div className="input-container">
            <input
              name="password"
              id="password"
              key="password"
              className={(errorPath == "password" && "error") || "normal"}
              type="password"
              placeholder="enter password"
              ref={passwordInputRef}
              required
            />
            {errorMessage && errorPath == "password" && (
              <FormErrorModal errorMessage={errorMessage} />
            )}
          </div>
        )}
        <button
          type="submit"
          className="btn positive"
          aria-label="submit join chatroom form"
          disabled={isFetching}
        >
          enter
        </button>
      </form>
      <AnimatePresence>
        {errorMessage && !errorPath && (
          <APIResponsePopup popupType="fail" message={errorMessage} setMessage={setErrorMessage} />
        )}
        {successMessage && (
          <APIResponsePopup
            popupType="success"
            message={successMessage}
            setMessage={setSuccessMessage}
            successAction={() => {
              navigateToChat && navigate(`/chat/engage/chatroom/${chatroomUID}`);
            }}
          />
        )}
      </AnimatePresence>
    </ConfirmActionDialogue>
  );
}

type PrivateChatroomLeaveDialogueProps = {
  chatroomUID: UUID;
  setShow: SetBoolState;
};
export function PrivateChatroomLeaveDialogue({
  chatroomUID,
  setShow,
}: PrivateChatroomLeaveDialogueProps) {
  const [successMessage, setSuccessMessage] = useState<string>();
  const [errorMessage, setErrorMessage] = useState<string>();
  const [isFetching, setIsFetching] = useState(false);
  const axios = useAxios();
  const navigate = useNavigate();

  const apiErrorHandler = useHandleError();

  const handleLeaveChatroomClick = () => {
    setIsFetching(true);
    setErrorMessage(undefined);
    axios
      .post(`/chat/private/room/leave/${chatroomUID}/`)
      .then((res) => {
        setSuccessMessage("you are no longer a member of this chatroom");
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
      <p className="title">confirm you want to leave chatroom</p>
      <button
        type="button"
        className="btn danger"
        aria-label="submit join chatroom form"
        disabled={isFetching}
        onClick={handleLeaveChatroomClick}
      >
        leave
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
              navigate("/chat/rooms");
            }}
          />
        )}
      </AnimatePresence>
    </ConfirmActionDialogue>
  );
}

type ChatroomRecordingSwitchDialogueProps = {
  chatroomUID: UUID;
  setShow: SetBoolState;
  successFunction?: () => void;
  currentRecordingStatus: boolean;
};
export function ChatroomRecordingSwitchDialogue({
  chatroomUID,
  setShow,
  successFunction,
  currentRecordingStatus,
}: ChatroomRecordingSwitchDialogueProps) {
  const [isFetching, setIsFetching] = useState(false);
  const passwordInputRef = useRef<HTMLInputElement>(null);
  const axios = useAxios();

  const [successMessage, setSuccessMessage] = useState<string>();
  const [errorMessage, setErrorMessage] = useState<string>();
  const apiErrorHandler = useHandleError();

  useEffect(() => {
    passwordInputRef.current?.focus();
  }, []);

  const handleSwitchRecordingStatus = () => {
    setErrorMessage(undefined);
    setIsFetching(true);
    axios
      .patch(`/chat/private/room/recording/${chatroomUID}/switch`)
      .then((res) => {
        setSuccessMessage(`Done`);
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
      <p className="title">
        confirm you want to turn messages recording {(currentRecordingStatus && "off") || "on"}
      </p>
      <button
        type="button"
        className="btn"
        aria-label="submit join chatroom form"
        disabled={isFetching}
        onClick={handleSwitchRecordingStatus}
      >
        confirm
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
              successFunction && successFunction();
              setShow(false);
            }}
          />
        )}
      </AnimatePresence>
    </ConfirmActionDialogue>
  );
}
