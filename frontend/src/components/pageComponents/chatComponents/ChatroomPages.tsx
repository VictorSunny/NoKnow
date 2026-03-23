import { Link } from "react-router-dom";

import "./ChatroomPages.css";
import { Chatroom, ChatroomListResponse } from "../../../schemas/ChatSchemas";
import { InfiniteData } from "@tanstack/react-query";
import FetchErrorSignal from "../../general/fetchModals/FetchErrorModal";
import { motion } from "framer-motion";

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
        {pagesData.pages?.map((page) => {
          return page.chatrooms?.map((chatroomDetails, index) => {
            return <ChatroomCard key={index} chatroomDetails={chatroomDetails} />;
          });
        })}
      </div>
      {pagesData.pages[0].chatrooms.length > 0 && (
        <motion.button
          className={`btn fetch-more-btn ${isFetchingNextPage && "load"}`}
          type="button"
          aria-label="load more chatrooms"
          onClick={handleFetchMoreClick}
          disabled={isFetchingNextPage || allChatroomsFetched}
          layout
        >
          {/* change button value while fetching next page */}
          {(isFetchingNextPage && "loading") ||
            (isFetchNextPageError && "retry") ||
            (allChatroomsFetched && "end of list") ||
            "load more rooms"}
        </motion.button>
      )}
    </>
  );
}

export function ChatroomCard({ chatroomDetails }: { chatroomDetails: Chatroom }) {
  return (
    <Link to={`/chat/engage/chatroom/${chatroomDetails.uid}`} className="chatroom-card">
      <p className="name">{chatroomDetails.name}</p>
      <p className="activity-data">{chatroomDetails.modified_at}</p>
    </Link>
  );
}
