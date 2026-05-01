import { Link } from "react-router-dom";

import "./ChatroomPages.css";
import { Chatroom, ChatroomListResponse } from "../../../schemas/ChatSchemas";
import { InfiniteData } from "@tanstack/react-query";
import FetchErrorSignal from "../../general/modals/FetchErrorModal";
import { motion } from "framer-motion";
import React from "react";
import LoadMoreButton from "../../general/loadMoreButton/LoadMoreButton";

type ChatroomPagesProps = {
  pagesData: InfiniteData<ChatroomListResponse, unknown>;
  isFetchingNextPage: boolean;
  handleFetchMoreClick: () => void;
  allChatroomsFetched: boolean;
  isFetchNextPageError: boolean;
};
export function ChatroomPages({
  pagesData,
  isFetchingNextPage,
  handleFetchMoreClick,
  allChatroomsFetched,
  isFetchNextPageError,
}: ChatroomPagesProps) {
  if (pagesData.pages[0].chatrooms.length < 1) {
    return <FetchErrorSignal errorMessage="sorry. no matches were found." />;
  }

  return (
    <>
      <div className="chatroom-list">
        {pagesData.pages?.map((page, index) => {
          return <ChatroomPage key={index} page={page} />;
        })}
      </div>
      {pagesData.pages[0].chatrooms.length > 0 && (
        <LoadMoreButton
          itemName="chatroom"
          isFetchingNextPage={isFetchingNextPage}
          isFetchNextPageError={isFetchNextPageError}
          allFetched={allChatroomsFetched}
          onClick={handleFetchMoreClick}
        />
      )}
    </>
  );
}
const ChatroomPage = React.memo(({ page }: { page: ChatroomListResponse }) => {
  return page.chatrooms?.map((chatroomDetails) => {
    return <ChatroomCard key={chatroomDetails.uid} chatroomDetails={chatroomDetails} />;
  });
});
export const ChatroomCard = React.memo(({ chatroomDetails }: { chatroomDetails: Chatroom }) => {
  return (
    <Link to={`/chat/engage/chatroom/${chatroomDetails.uid}`} className="chatroom-card">
      <p className="name">{chatroomDetails.name}</p>
      <p className="activity-data">{chatroomDetails.modified_at}</p>
    </Link>
  );
});
