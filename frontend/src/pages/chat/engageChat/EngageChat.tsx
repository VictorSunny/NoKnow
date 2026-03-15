import useAxios from "../../../hooks/useAxios";
import { FriendshipStatusResponseSchema } from "../../../schemas/AuthSchema";
import { ChatroomExtendedListSchema } from "../../../schemas/ChatSchemas";
import { useEffect, useState } from "react";
import { useParams } from "react-router-dom";
import MessageBox from "./MessageBox";
import FetchErrorSignal from "../../../components/general/fetchModals/FetchErrorModal";
import LineLoadingSignal from "../../../components/general/fetchModals/LineLoadingModal";
import { Link } from "react-router-dom";
import { UUID } from "crypto";
import { useAuthContext } from "../../../contexts/AuthContext";
import useSetPageTitle from "../../../hooks/useSetPageTitle";
import useGetAnonymousUsername from "../../../hooks/useGetAnonymouseUsername";
import useHandleError from "../../../hooks/useHandleError";
import { ChatType } from "../../../types/chatroomTypes";

export default function EngageChat() {
  const { accessTokenData, userDetails } = useAuthContext();
  const { chatType, chatID } = useParams();
  const axios = useAxios();
  const [allowConnect, setAllowConnect] = useState(false);
  const [allowNextButton, setAllowNextButton] = useState(false);
  const [isFetching, setIsFetching] = useState(false);
  const [chatTitle, setChatTitle] = useState<string>();

  const [errorMessage, setErrorMessage] = useState<string>();
  const apiErrorHandler = useHandleError();

  const anonymousUsername = useGetAnonymousUsername();
  const [userUID, setUserUID] = useState<UUID | undefined>(userDetails?.uid as UUID);

  const _ = useSetPageTitle((chatTitle && `engaging ${chatTitle}`) || "...");

  useEffect(() => {
    if (chatType == "user") {
      setIsFetching(true);
      axios
        .get(`/user/friends/check?username=${chatID}`)
        .then((res) => {
          const friendshipStatus = FriendshipStatusResponseSchema.parse(res.data).friendship_status;
          if (friendshipStatus == "friended") {
            setAllowConnect(true);
            setChatTitle(chatID);
          } else {
            const message =
              (friendshipStatus == "requested" &&
                "your friend request has not yet been accepted.") ||
              (friendshipStatus == "pending" && "you need to accept their friend request first.") ||
              "send a friend request?";
            setErrorMessage(`you cannot message @${chatID}. ${message}`);
          }
          setAllowNextButton(true);
        })
        .catch((err) => {
          apiErrorHandler({ err, setErrorMessage });
        })
        .finally(() => {
          setIsFetching(false);
        });
    }
    if (chatType == "chatroom") {
      setIsFetching(true);
      axios
        .get(`/chat/all/?id=${chatID}`)
        .then((res) => {
          const chatroomInfo = ChatroomExtendedListSchema.parse(res.data).chatrooms[0];
          if (chatroomInfo.user_status == "removed" && chatroomInfo.room_type == "private") {
            setErrorMessage("chatroom is private and you're not a member. join chatroom?");
          } else {
            setAllowConnect(true);
            setChatTitle(chatroomInfo.name);
          }
          setAllowNextButton(true);
        })
        .catch((err) => {
          apiErrorHandler({ err, setErrorMessage });
        })
        .finally(() => {
          setIsFetching(false);
        });
    }
  }, [accessTokenData]);

  useEffect(() => {
    setUserUID(userDetails?.uid as UUID);
  }, [userDetails]);

  return (
    <div className="page-container engage-chat-page">
      {(allowConnect && anonymousUsername && (
        <MessageBox
          anonymousUsername={anonymousUsername}
          userUID={userUID as UUID}
          chatID={chatID as UUID}
          chatTitle={chatTitle}
          accessToken={accessTokenData?.access_token}
          chatType={chatType as ChatType}
        />
      )) ||
        (isFetching && !errorMessage && anonymousUsername && <LineLoadingSignal />) ||
        (errorMessage && !isFetching && (
          <>
            <FetchErrorSignal errorMessage={errorMessage}>
              {allowNextButton && (
                <Link className="btn" to={`/preview/${chatType}/${chatID}`}>
                  view {chatType}
                </Link>
              )}
            </FetchErrorSignal>
          </>
        ))}
    </div>
  );
}
