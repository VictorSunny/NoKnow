import React, { useState, useRef, useEffect } from "react";

import "./EngageChat.css";
import useAxios from "../../../hooks/useAxios";
import { QueryFunction, useInfiniteQuery } from "@tanstack/react-query";
import {
  Message,
  MessageListResponse,
  MessageListResponseSchema,
  MessageSchema,
} from "../../../schemas/ChatSchemas";
import getMessagesLength from "../../../utilities/getMessagesLength";
import SpinnerLoader from "../../../components/general/popups/loaders/SpinnerLoader";
import { validate as validateUUID } from "uuid";
import { UUID } from "crypto";
import useGetRecentChatrooms from "../../../hooks/useGetRecentChatrooms";
import SpeechBubble from "../../../components/general/speechBubble/SpeechBubble";
import useSetPageTitle from "../../../hooks/useSetPageTitle";
import { Link, useNavigate } from "react-router-dom";
import { useInView } from "react-intersection-observer";
import useResizeViewportContent from "../../../hooks/useResizeViewportContent";

import { ReactComponent as ArrowIcon } from "../../../assets/icons/caret-up-icon.svg";
import FetchErrorSignal from "../../../components/general/popups/messagePopups/FetchErrorModal";

export default function MessageBox({
  chatID,
  accessToken,
  chatTitle,
  anonymousUsername,
  userUID,
  chatType,
}: {
  chatID: string;
  accessToken: string | undefined;
  chatTitle: string | undefined;
  anonymousUsername: string;
  userUID: UUID | undefined;
  chatType: string;
}) {
  const _ = useSetPageTitle("engaged");

  const { updateRecentlyVisitedRoomsUIDs } = useGetRecentChatrooms();

  const [allMessagesFetched, setAllMessagesFetched] = useState<boolean>(false);
  const [chatEngaged, setChatEngaged] = useState<boolean>(false);
  const [connectingToChat, setConnectingToChat] = useState<boolean>(true);

  const wsUserMessagesCount = useRef(0);
  const wsUnreadMessagesCount = useRef(0);
  const messagesContainerRef = useRef<HTMLDivElement>(null);
  const messagesContainerScrollHeightRef = useRef(0);

  const navigate = useNavigate();

  const { ref: bottomFlagRef, inView: bottomRefinView } = useInView({
    root: messagesContainerRef.current,
    threshold: 0.1,
    rootMargin: "100px 0px",
  });

  const websocketRef = useRef<WebSocket>(null);
  const messageInput = useRef<HTMLTextAreaElement>(null);
  const [wsMessages, setWsMessages] = useState<Message[]>([]);

  const userPreviewURLPrefix =
    (chatType == "chatroom" && `/chat/meta/chatroom/${chatID}/users/preview`) || "/preview/user";

  const axios = useAxios();

  const fetchChatMessages: QueryFunction<MessageListResponse, [any], number> = async () => {
    const controller = new AbortController();
    messagesContainerScrollHeightRef.current = messagesContainerRef.current?.scrollHeight ?? 0;

    const pagesMessagesLength = (messagesData && getMessagesLength(messagesData.pages)) || 0;
    const offset = pagesMessagesLength + wsUserMessagesCount.current;
    try {
      const res = await axios.get(`/chat/messages/${chatID}?&offset=${offset}`, {
        signal: controller.signal,
      });
      if (res.data.messages && res.data.messages.length < 1) {
        setAllMessagesFetched(true);
      }
      const parsedMessages = MessageListResponseSchema.parse(res.data);
      return parsedMessages;
    } catch (err) {
      throw err;
    } finally {
      controller.abort();
    }
  };

  const {
    data: messagesData,
    isFetching,
    isFetchingNextPage,
    // isFetchNextPageError,
    isError,
    refetch,
    error,
    fetchNextPage,
  } = useInfiniteQuery({
    queryKey: [chatID],
    queryFn: fetchChatMessages,
    initialPageParam: 1,
    staleTime: Infinity,
    getNextPageParam: (_lastPage, messagesData) => messagesData.length + 1,
  });

  const handleFetchMoreClick = () => {
    fetchNextPage();
  };
  const handleMessagingFormSubmit = (e: React.FormEvent<HTMLFormElement>) => {
    e.preventDefault();
    messageInput.current?.focus();
    const form = new FormData(e.currentTarget);
    const message = form.get("message-body");
    if (websocketRef.current?.readyState == 1) {
      websocketRef.current?.send(message!);
      e.currentTarget.reset();
    } else {
      navigate(0);
    }
  };

  const scrollToMessagesBotttom = (props?: { smooth: boolean }) => {
    if (messagesContainerRef.current) {
      const top = messagesContainerRef.current.scrollHeight;
      messagesContainerRef.current.scrollTo({
        top: top,
        left: 0,
        behavior: (props?.smooth && "smooth") || "instant",
      });
    }
  };
  const __ = useResizeViewportContent(scrollToMessagesBotttom);

  useEffect(() => {
    const chatURL = `/ws/chat/engage/${chatID}?anon_username=${anonymousUsername}&token=${accessToken}`;
    setConnectingToChat(true);
    try {
      const ws = new WebSocket(chatURL);
      ws.onmessage = (event) => {
        const message = JSON.parse(event.data);
        const parsedMessageJson = MessageSchema.parse(message);
        if (
          (parsedMessageJson.type == "user" && parsedMessageJson.recorded) ||
          parsedMessageJson.type == "announcement"
        ) {
          wsUserMessagesCount.current += 1;
        }
        setWsMessages((prev) => [...prev, parsedMessageJson]);
      };
      websocketRef.current = ws;
    } catch (err) {
      websocketRef.current = null;
    } finally {
      setConnectingToChat(false);
    }

    return () => {
      if (websocketRef.current) {
        setChatEngaged(false);
        websocketRef.current.close();
        websocketRef.current = null;
      }
    };
  }, []);

  useEffect(() => {
    if (websocketRef.current?.CONNECTING) {
      setConnectingToChat(true);
      setChatEngaged(false);
    } else if (websocketRef.current?.OPEN) {
      setConnectingToChat(false);
      setChatEngaged(true);
      if (validateUUID(chatID)) {
        updateRecentlyVisitedRoomsUIDs(chatID as UUID);
      }
      scrollToMessagesBotttom();
    } else {
      setConnectingToChat(false);
      setChatEngaged(false);
    }
  }, [websocketRef.current]);

  useEffect(() => {
    if (messagesContainerRef.current) {
      const scrollHeightChange =
        messagesContainerRef.current.scrollHeight - messagesContainerScrollHeightRef.current;
      messagesContainerRef.current.scrollTo({
        top: scrollHeightChange,
        left: 0,
        behavior: "instant",
      });
    }
  }, [messagesData?.pages]);

  useEffect(() => {
    if (bottomRefinView) {
      scrollToMessagesBotttom();
    } else {
      wsUnreadMessagesCount.current += 1;
    }
  }, [wsMessages]);

  useEffect(() => {
    wsUnreadMessagesCount.current = 0;
  }, [bottomRefinView]);

  return (
    <div className="message-box">
      <div className="utils-section">
        <p className="chat-name">{chatTitle}</p>
        {(chatType == "chatroom" && (
          <Link to={`/chat/meta/${chatType}/${chatID}`} className="btn chat-meta-btn">
            ...
          </Link>
        )) || (
          <Link to={`/chat/meta/user/${chatID}`} className="btn chat-meta-btn">
            ...
          </Link>
        )}
      </div>

      <div className="section all-messages-section" ref={messagesContainerRef}>
        {(connectingToChat && !chatEngaged && <SpinnerLoader />) ||
          (!connectingToChat && chatEngaged && (
            <>
              <button
                name="button"
                onClick={handleFetchMoreClick}
                className="btn load-messages-btn"
                disabled={allMessagesFetched || isFetchingNextPage}
              >
                {(allMessagesFetched && "no older messages") || "load older"}
              </button>
              <div className="messages-container">
                {messagesData?.pages &&
                  messagesData.pages
                    .slice()
                    .reverse()
                    .map((page, i, arr) => {
                      const index = arr.length - 1 - i;
                      return (
                        <MessagePages
                          key={index}
                          page={page}
                          userPreviewURLPrefix={userPreviewURLPrefix}
                          anonymousUsername={anonymousUsername}
                          userUID={userUID}
                          chatID={chatID}
                        />
                      );
                    })}
                <WebsocketMessagesWindow
                  anonymousUsername={anonymousUsername}
                  userUID={userUID}
                  userPreviewURLPrefix={userPreviewURLPrefix}
                  messagesList={wsMessages}
                  chatID={chatID}
                />
              </div>
            </>
          )) ||
          (!chatEngaged && !connectingToChat && (
            <FetchErrorSignal errorMessage="Failed to connect to chat." />
          ))}
        <div id="bottom-identifier" ref={bottomFlagRef}></div>
        {!bottomRefinView && (
          <button
            className="scroll-to-bottom-btn"
            onClick={() => scrollToMessagesBotttom({ smooth: true })}
          >
            <ArrowIcon className="flip-vertical btn-icon" />
            {wsUnreadMessagesCount.current > 0 && (
              <span className="unread-msgs-count">{wsUnreadMessagesCount.current}</span>
            )}
          </button>
        )}
      </div>

      <div className="main-form-section">
        <form
          name="send-message"
          onSubmit={handleMessagingFormSubmit}
          className="send-message-form"
        >
          <textarea
            ref={messageInput}
            name="message-body"
            placeholder="type a message"
            id="send-message-input"
            autoComplete="off"
            maxLength={800}
          />
          <button
            type="submit"
            className="btn send-msg-btn"
            aria-label="send message to chat"
            name="button"
          >
            send
          </button>
        </form>
      </div>
    </div>
  );
}

type MessageCardProps = {
  messageDetails: Message;
  anonymousUsername: string;
  userUID: UUID | undefined;
  chatID: string | UUID;
  userPreviewURLPrefix: string;
  animate?: boolean;
};
const MessageCard = React.memo(
  ({
    messageDetails,
    userUID,
    anonymousUsername,
    userPreviewURLPrefix,
    animate,
  }: MessageCardProps) => {
    const [seeMore, setSeeMore] = useState<boolean>(false);
    const handleSeeMoreClick = () => {
      setSeeMore((prev) => !prev);
    };
    const maxWords = 255;
    const maxWordsExceeded = messageDetails.content.length > maxWords;
    return (
      <>
        {(messageDetails.type == "user" && (
          <SpeechBubble
            tickerPosition={
              (((messageDetails.sender_uid && userUID && messageDetails.sender_uid == userUID) ||
                messageDetails.sender_username == anonymousUsername) &&
                "right") ||
              "left"
            }
            messageType={messageDetails.type}
            animate={animate}
            className="message-card"
          >
            <Link
              to={`${userPreviewURLPrefix}/${messageDetails.sender_username}`}
              className="sender-name username"
            >
              {messageDetails.sender_username}
            </Link>
            <p
              className={`message-body ${(maxWordsExceeded && !seeMore && "cut") || (seeMore && "full") || ""}`}
            >
              {messageDetails.content}
            </p>
            <p className="message-date">{messageDetails.created_at?.split(",")[0]}</p>
            {maxWordsExceeded && (
              <button onClick={handleSeeMoreClick} className="text-btn">
                {(!seeMore && "see more") || "see less"}
              </button>
            )}
          </SpeechBubble>
        )) || (
          <SpeechBubble messageType={messageDetails.type} tickerPosition="both">
            <p className="message-body">{messageDetails.content}</p>
          </SpeechBubble>
        )}
      </>
    );
  }
);

type MessagesPagesProps = {
  page: MessageListResponse;
  anonymousUsername: string;
  userUID: UUID | undefined;
  userPreviewURLPrefix: string;
  chatID: string | UUID;
};
const MessagePages = React.memo(
  ({ page, anonymousUsername, userUID, chatID, userPreviewURLPrefix }: MessagesPagesProps) => {
    const latestDate = useRef<string>(null);
    const latestChanged = useRef(false);
    console.log("hh");
    return (
      <>
        {page.messages?.map((messageDetails) => {
          const date = messageDetails.created_at?.split(",")[1] || null;
          if (latestDate.current != date) {
            latestDate.current = date;
            latestChanged.current = true;
          } else {
            latestChanged.current = false;
          }
          return (
            <React.Fragment key={messageDetails.uid}>
              {latestChanged.current && <div className="messages-date-indicator">{date}</div>}
              <MessageCard
                chatID={chatID}
                anonymousUsername={anonymousUsername}
                userUID={userUID}
                messageDetails={messageDetails}
                userPreviewURLPrefix={userPreviewURLPrefix}
              />
            </React.Fragment>
          );
        })}
      </>
    );
  }
);

type WebsocketMessagesWindowProps = {
  messagesList: Message[] | undefined;
  anonymousUsername: string;
  userUID: UUID | undefined;
  chatID: string | UUID;
  userPreviewURLPrefix: string;
};
function WebsocketMessagesWindow({
  messagesList,
  anonymousUsername,
  userUID,
  chatID,
  userPreviewURLPrefix,
}: WebsocketMessagesWindowProps) {
  return (
    <>
      {messagesList?.map((messageDetails) => {
        return (
          <MessageCard
            chatID={chatID}
            anonymousUsername={anonymousUsername}
            userUID={userUID}
            key={messageDetails.uid}
            messageDetails={messageDetails}
            userPreviewURLPrefix={userPreviewURLPrefix}
            animate
          />
        );
      })}
    </>
  );
}
